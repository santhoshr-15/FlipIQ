from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import (
    Product, Category, Cart, CartItem, Order, OrderItem, 
    Review, Seller, WishlistItem, UserProfile, User , FreshnessDetectionLog
)

class HomeView(ListView):
    model = Product
    template_name = 'flipkart_app/home.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(stock__gt=0)
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        
        if category:
            queryset = queryset.filter(category__name=category)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['featured_products'] = Product.objects.filter(is_featured=True)[:6]
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'flipkart_app/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]
        context['reviews'] = Review.objects.filter(product=self.object)
        return context

def user_register(request):
    if request.method == 'POST':
        # Extract registration form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        user_type = request.POST.get('user_type')  

        # Validation checks
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
            return redirect('register')

        # Create user
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password
        )
        user.first_name = first_name
        user.last_name = last_name
        user.is_customer = user_type == 'customer'
        user.is_seller = user_type == 'seller'
        user.save()

        # Create user profile
        user_profile = UserProfile.objects.create(
            user=user,
            phone_number=phone_number,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            user_type=user_type
        )

        # Create seller profile if user is a seller
        if user_type == 'seller':
            Seller.objects.create(user_profile=user_profile, is_verified=False)

        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')

    return render(request, 'flipkart_app/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_seller:
                return redirect('seller_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'flipkart_app/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def complete_seller_profile(request):
    if not request.user.is_seller:
        messages.error(request, 'You do not have seller permissions.')
        return redirect('home')

    seller_profile = request.user.profile.seller

    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        gst_number = request.POST.get('gst_number')
        bank_account_number = request.POST.get('bank_account_number')
        ifsc_code = request.POST.get('ifsc_code')

        # Add validation logic
        seller_profile.company_name = company_name
        seller_profile.gst_number = gst_number
        seller_profile.bank_account_number = bank_account_number
        seller_profile.ifsc_code = ifsc_code
        seller_profile.save()

        messages.success(request, 'Seller profile updated successfully.')
        return redirect('seller_dashboard')

    return render(request, 'Seller/complete_seller_profile.html', {'seller': seller_profile})

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all() if not created else []
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    
    return render(request, 'flipkart_app/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart.')
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action')

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()
    elif action == 'remove':
        cart_item.delete()
    else:
        messages.error(request, 'Invalid action.')

    return redirect('cart')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if cart.items.count() == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        phone_number = request.POST.get('phone_number')
        payment_method = request.POST.get('payment_method')
        
        if not shipping_address or not phone_number or not payment_method:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('checkout')
        
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            phone_number=phone_number,
            payment_method=payment_method,
            total_amount=cart.get_total()
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.discounted_price(),
            )

        cart.items.all().delete()

        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'flipkart_app/checkout.html', {'cart': cart})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'flipkart_app/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'flipkart_app/order_history.html', {'orders': orders})

@login_required
def profile(request):
    # Try to get the user profile, create it if it doesn't exist
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'phone_number': '',
            'address': '',
            'city': '',
            'state': '',
            'pincode': '',
            'user_type': 'customer'
        }
    )
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')

        if all([phone_number, address, city, state, pincode]):
            profile.phone_number = phone_number
            profile.address = address
            profile.city = city
            profile.state = state
            profile.pincode = pincode
            profile.save()
            messages.success(request, 'Profile updated successfully.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'flipkart_app/user_profile.html', {'profile': profile})

@login_required
def wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'flipkart_app/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.get_or_create(user=request.user, product=product)
    return JsonResponse({'added': True}, status=200)

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.filter(user=request.user, product=product).delete()
    return JsonResponse({'removed': True}, status=200)


@login_required
def seller_dashboard(request):
    if not request.user.is_seller:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    try:
        seller = Seller.objects.get(user_profile__user=request.user)
    except Seller.DoesNotExist:
        messages.error(request, 'Seller profile not found.')
        return redirect('home')

    # Calculate total products and in-stock products
    total_products = Product.objects.filter(seller=seller).count()
    in_stock_products = Product.objects.filter(seller=seller, stock__gt=0).count()

    # Filter orders that contain products from this seller
    orders = Order.objects.filter(items__product__seller=seller).distinct()

    # Calculate total sales
    total_sales = sum(
        order.total_amount for order in orders 
        if order.status not in ['cancelled']
    )

    # Calculate pending payments
    pending_payments = sum(
        order.total_amount for order in orders 
        if order.status in ['pending', 'processing']
    )

    context = {
        'orders': orders,
        'seller': seller,
        'total_sales': total_sales,
        'pending_payments': pending_payments,
        'total_orders': orders.count(),
        'total_products': total_products,
        'in_stock_products': in_stock_products,
    }

    return render(request, 'Seller/seller_dashboard.html', context)



@login_required
def manage_products(request):
    # Ensure only sellers can access this view
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'seller':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    # Get the seller's products
    seller = request.user.profile.seller
    products = Product.objects.filter(seller=seller).select_related('category')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(category__name__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    sort_options = {
        'name': 'name',
        'price': 'price',
        'stock': 'stock',
        '-name': '-name',
        '-price': '-price',
        '-stock': '-stock'
    }
    products = products.order_by(sort_options.get(sort_by, 'name'))
    
    # Pagination
    paginator = Paginator(products, 10)  # 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    return render(request, 'Seller/manage_products.html', context)


@login_required
def edit_product(request, product_id):
    # Ensure only sellers can edit products
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'seller':
        messages.error(request, "You do not have permission to edit products.")
        return redirect('home')
    
    # Get the seller
    seller = request.user.profile.seller
    
    # Get the product, ensuring it belongs to the current seller
    try:
        product = Product.objects.get(id=product_id, seller=seller)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('manage_products')
    
    # Handle POST request
    if request.method == 'POST':
        try:
            # Get values from request.POST
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            category_id = request.POST.get('category')
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            is_featured = request.POST.get('is_featured') == 'on'
            discount_percentage = request.POST.get('discount_percentage', 0)
            
            # Validate inputs
            if not name:
                raise ValueError("Product name is required.")
            
            if not category_id:
                raise ValueError("Category is required.")
            
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be a positive number.")
            except ValueError:
                raise ValueError("Invalid price.")
            
            try:
                stock = int(stock)
                if stock < 0:
                    raise ValueError("Stock cannot be negative.")
            except ValueError:
                raise ValueError("Invalid stock quantity.")
            
            try:
                discount_percentage = int(discount_percentage)
                if discount_percentage < 0 or discount_percentage > 100:
                    raise ValueError("Discount percentage must be between 0 and 100.")
            except ValueError:
                raise ValueError("Invalid discount percentage.")
            
            # Get category
            category = get_object_or_404(Category, id=category_id)
            
            # Handle image upload
            if 'image' in request.FILES:
                image = request.FILES['image']
                product.image = image
            
            # Update product attributes
            product.category = category
            product.name = name
            product.description = description
            product.price = price
            product.stock = stock
            product.is_featured = is_featured
            product.discount_percentage = discount_percentage
            
            # Save updated product
            product.save()
            
            # Success message
            messages.success(request, f"Product '{product.name}' updated successfully!")
            return redirect('manage_products')
        
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, "An error occurred while updating the product.")
    
    # Prepare context for template
    context = {
        'product': product,
        'categories': Category.objects.all(),
        'editing': True
    }
    
    return render(request, 'Seller/edit_product.html', context)
# Separate view for deleting product (same as your original implementation)
@login_required
def delete_product(request, product_id):
    try:
        # Check user profile and permissions
        profile = request.user.profile
        if not profile or profile.user_type != 'seller':
            messages.error(request, "You do not have permission to delete products.")
            return redirect('home')
        
        # Get seller and product
        seller = profile.seller
        product = get_object_or_404(Product, id=product_id, seller=seller)
        
        # Check for active orders
        active_orders = product.orderitem_set.filter(order__status__in=['pending', 'processing', 'shipped'])
        if active_orders.exists():
            messages.error(request, "Cannot delete a product with active orders.")
            return redirect('manage_products')
        
        # Delete product
        product_name = product.name
        product.delete()
        
        messages.success(request, f"Product '{product_name}' deleted successfully!")
        return redirect('manage_products')
    
    except Exception as e:
        messages.error(request, f"Error deleting product: {str(e)}")
        return redirect('manage_products')

@login_required
def edit_product(request, product_id):
    if not request.user.is_seller:
        messages.error(request, 'You do not have permission to edit products.')
        return redirect('home')

    try:
        product = Product.objects.get(id=product_id, seller__user_profile__user=request.user)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('manage_products')

    if request.method == 'POST':
        # Similar to add_product logic, but update existing product
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.discount_percentage = request.POST.get('discount_percentage', 0)
        product.is_featured = request.POST.get('is_featured') == 'on'

        # Handle category change
        category_id = request.POST.get('category')
        product.category = Category.objects.get(id=category_id)

        # Handle image update (optional)
        new_image = request.FILES.get('image')
        if new_image:
            product.image = new_image

        product.save()
        messages.success(request, f'Product "{product.name}" updated successfully.')
        return redirect('manage_products')

    return render(request, 'Seller/edit_product.html', {
        'product': product,
        'categories': Category.objects.all()
    })



@login_required
def order_detail(request, order_id):
    """
    Display details for a specific order.
    Ensure the logged-in user is a seller and the order contains only their products.
    """
    # Check if the logged-in user is a seller
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'seller':
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')  # Redirect to the home page

    # Retrieve the order; ensure it exists
    order = get_object_or_404(Order, id=order_id)

    # Fetch all items in the order
    order_items = order.items.all()

    # Calculate total items in the order
    total_items = sum(item.quantity for item in order_items)

    # Ensure all items in the order belong to the seller's products
    seller = request.user.profile.seller
    seller_items = all(item.product.seller == seller for item in order_items)
    if not seller_items:
        messages.error(request, "You can only view orders that include your products.")
        return redirect('seller_dashboard')  # Redirect to seller dashboard or another appropriate page

    # Handle order status updates
    if request.method == 'POST':
        if 'update_status' in request.POST:
            new_status = request.POST.get('status')
            if new_status in dict(Order.STATUS_CHOICES):  # Ensure the status is valid
                order.status = new_status
                order.save()
                messages.success(request, f"Order status updated to {order.get_status_display()}")
                return redirect('order_detail', order_id=order.id)
            else:
                messages.error(request, "Invalid order status selected.")

    # Context for rendering the order details page
    context = {
        'order': order,
        'order_items': order_items,
        'total_items': total_items,
        'status_choices': Order.STATUS_CHOICES,
    }

    return render(request, 'Seller/order_detail.html', context)



@login_required
def add_product(request):
    if not request.user.is_seller:
        messages.error(request, 'You do not have permission to add products.')
        return redirect('home')

    try:
        seller = Seller.objects.get(user_profile__user=request.user)
    except Seller.DoesNotExist:
        messages.error(request, 'Seller profile not found.')
        return redirect('home')

    if request.method == 'POST':
        # Collect form data
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')
        is_featured = request.POST.get('is_featured') == 'on'
        discount_percentage = request.POST.get('discount_percentage', 0)

        # Validate required fields
        if not all([name, description, category_id, price, stock, image]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'Seller/add_product.html', {
                'categories': Category.objects.all(),
                'seller': seller
            })

        try:
            # Get the category
            category = Category.objects.get(id=category_id)

            # Create new product
            product = Product.objects.create(
                seller=seller,
                category=category,
                name=name,
                description=description,
                price=float(price),
                stock=int(stock),
                image=image,
                is_featured=is_featured,
                discount_percentage=int(discount_percentage) if discount_percentage else 0
            )

            messages.success(request, f'Product {product.name} added successfully.')
            return redirect('seller_dashboard')

        except (Category.DoesNotExist, ValueError) as e:
            messages.error(request, f'Error creating product: {str(e)}')

    # GET request - show the add product form
    return render(request, 'Seller/add_product.html', {
        'categories': Category.objects.all(),
        'seller': seller
    })





def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'flipkart_app/track_order.html', context)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['delivered', 'cancelled']:
        messages.error(request, 'You cannot cancel a delivered or already cancelled order.')
    else:
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Your order has been cancelled.')

    return redirect('order_history')

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    # Category filtering
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        products = products.filter(category__name__in=selected_categories)

    # Price filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 9)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Preserve query parameters
    query_string = request.GET.copy()
    if 'page' in query_string:
        query_string.pop('page')
    query_string = query_string.urlencode()

    context = {
        'categories': categories,
        'products': page_obj,
        'selected_categories': selected_categories,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'query_string': query_string
    }
    return render(request, 'flipkart_app/product_list.html', context)

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True)[:6]
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'flipkart_app/home.html', context)



@login_required
def seller_support(request):
    context = {
        'page_title': 'Seller Support',
        'support_issues': [
            {
                'category': 'Billing',
                'description': 'Questions about payments, invoicing, and financial matters'
            },
            {
                'category': 'Product Listing',
                'description': 'Help with adding, editing, or removing product listings'
            },
            {
                'category': 'Account Management',
                'description': 'Issues with account settings, profile, and credentials'
            },
            {
                'category': 'Order Processing',
                'description': 'Support for order fulfillment, shipping, and tracking'
            }
        ]
    }
    return render(request, 'Seller/support.html', context)

import os
import base64
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Order, FreshnessDetectionLog
from ultralytics import YOLO
import logging
import uuid  # Added for unique filename generation

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the YOLO model
MODEL_PATH = os.path.join(settings.BASE_DIR, 'flipkart_app/ml_models/FRESH_MASS.pt')
yolo_model = YOLO(MODEL_PATH)

def detect_freshness(request, order_id):
    """
    View for handling AI freshness detection.
    Supports image upload, camera capture (internal/external), and YOLO model predictions.
    """
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        try:
            # Handle image upload or camera capture
            image_data = request.POST.get('image_data')  # From camera
            external_camera = request.POST.get('external_camera', False)
            
            # Generate a unique filename
            unique_filename = f"{uuid.uuid4()}"

            if image_data:
                # Decode the base64 image
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]  # Get file extension
                
                # Incorporate external camera flag in filename
                camera_type = "external" if external_camera else "internal"
                image_name = f"{unique_filename}_{camera_type}_capture.{ext}"
                
                image_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image_name)
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                
                # Save the image to local storage
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(imgstr))
            else:
                # From file upload
                uploaded_file = request.FILES.get('image')
                if not uploaded_file:
                    return JsonResponse({'success': False, 'error': 'No image uploaded or captured.'})

                # Generate unique filename for uploaded file
                ext = uploaded_file.name.split('.')[-1]
                image_name = f"{unique_filename}_upload.{ext}"
                
                image_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image_name)
                os.makedirs(os.path.dirname(image_path), exist_ok=True)

                # Save the uploaded image
                with open(image_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

            # Perform detection using YOLO model
            logger.info(f"Starting YOLO detection on {image_name}")
            results = yolo_model.predict(source=image_path, conf=0.2, iou=0.45, agnostic_nms=False)
            analysis_results = []

            # Parse YOLO results
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                    conf = box.conf[0].item()
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]

                
                    analysis_results.append({
                        'class_name': class_name,
                        'confidence': round(conf, 2),
                        'bounding_box': [x1, y1, x2, y2]
                    })

            # Save results to the database
            FreshnessDetectionLog.objects.create(
                order=order,
                image_path=image_path,
                results=analysis_results,
                camera_type='external' if external_camera else 'internal',
            )

            if not analysis_results:
                return JsonResponse({
                    'success': True, 
                    'message': 'No objects detected.', 
                    'results': [],
                    'camera_type': 'external' if external_camera else 'internal'
                })

            logger.info("Detection completed successfully")
            return JsonResponse({
                'success': True, 
                'results': analysis_results,
                'camera_type': 'external' if external_camera else 'internal'
            })

        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'Seller/detect_freshness.html', {'order': order})


def visualize_results(image_path, results):
    """
    Function to visualize YOLO results on an image.
    """
    import cv2
    import matplotlib.pyplot as plt

    img = cv2.imread(image_path)

    if results:
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                conf = box.conf[0].item()
                class_id = int(box.cls[0])
                class_name = result.names[class_id]

                # Draw bounding boxes and labels
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{class_name} {conf:.2f}"
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


    # Convert to RGB for Matplotlib
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Display the image
    plt.imshow(img_rgb)
    plt.axis('off')
    plt.show()


import uuid
import logging
import cv2
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from .models import Order, CategoryBrandDetectionLog
from ultralytics import YOLO
from paddleocr import PaddleOCR

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the models
CATEGORY_MODEL_PATH = os.path.join(settings.BASE_DIR, 'flipkart_app/ml_models/category.pt')
BRAND_TYPE_FLAVOR_MODEL_PATH = os.path.join(settings.BASE_DIR, 'flipkart_app/ml_models/brand_type_flavour.pt')

category_model = YOLO(CATEGORY_MODEL_PATH)
brand_type_flavor_model = YOLO(BRAND_TYPE_FLAVOR_MODEL_PATH)
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Class mappings
CATEGORY_CLASS_MAPPING = {0: 'chips', 1: 'biscuit', 2: 'chocolate', 3: 'duo', 4: 'milk', 5: 'shampoo'}
CLASS_MAPPING = {0: 'Flavour', 1: 'Product_Type', 2: 'Brandname'}

def extract_text_from_bbox(image, bbox):
    """
    Crop the region of interest (ROI) and run PaddleOCR on it.
    """
    x1, y1, x2, y2 = map(int, bbox)
    roi = image[y1:y2, x1:x2]
    result = ocr.ocr(roi, cls=True)

    text_list = []
    if result and result[0]:
        for line in result[0]:
            text_list.append(line[1][0])

    return ' '.join(text_list) if text_list else 'No text detected'

def detect_items(request, order_id):
    """
    View to handle AI detection for category, brand, type, and flavor.
    """
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        try:
            # Handle image upload
            uploaded_file = request.FILES.get('image')
            if not uploaded_file:
                return JsonResponse({'success': False, 'error': 'No image uploaded.'})

            # Save image with a unique filename
            unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
            image_path = os.path.join(settings.MEDIA_ROOT, 'uploads', unique_filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)

            with open(image_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # Load the image
            image = cv2.imread(image_path)
            original_image = image.copy()

            # Run the first YOLO model (category detection)
            category_results = category_model.predict(image)
            items_info = []

            for category_result in category_results:
                for i, category_box in enumerate(category_result.boxes.xyxy):
                    # Get category details
                    category_class_id = int(category_result.boxes.cls[i])
                    category_name = CATEGORY_CLASS_MAPPING.get(category_class_id, 'Unknown')

                    # Draw bounding box on original image
                    x1, y1, x2, y2 = map(int, category_box)
                    cv2.rectangle(original_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(original_image, category_name, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    category_roi = image[y1:y2, x1:x2]

                    # Run the second YOLO model (brand, type, and flavor detection)
                    btf_results = brand_type_flavor_model.predict(category_roi)

                    item_info = {'Brandname': 'No text detected',
                                 'Product_Type': 'No text detected', 'Flavour': 'No text detected'}

                    detected_texts = {'Brandname': [], 'Product_Type': [], 'Flavour': []}

                    for j, btf_box in enumerate(btf_results[0].boxes.xyxy):
                        # Get class details
                        class_id = int(btf_results[0].boxes.cls[j])
                        class_name = CLASS_MAPPING.get(class_id, 'Unknown')

                        # Adjust bounding box coordinates to the original image
                        bx1, by1, bx2, by2 = map(int, btf_box)
                        abs_bx1, abs_by1 = bx1 + x1, by1 + y1
                        abs_bx2, abs_by2 = bx2 + x1, by2 + y1

                        cv2.rectangle(original_image, (abs_bx1, abs_by1), (abs_bx2, abs_by2), (255, 0, 0), 2)
                        cv2.putText(original_image, class_name, (abs_bx1, abs_by1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                        # Extract text from the bounding box
                        text_detected = extract_text_from_bbox(category_roi, btf_box)
                        detected_texts[class_name].append(text_detected)

                    # Add detected texts to item_info
                    item_info['Brandname'] = ', '.join(detected_texts['Brandname']) or 'No text detected'
                    item_info['Product_Type'] = ', '.join(detected_texts['Product_Type']) or 'No text detected'
                    item_info['Flavour'] = ', '.join(detected_texts['Flavour']) or 'No text detected'

                    items_info.append(item_info)

            # Save annotated image
            annotated_image_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f"annotated_{unique_filename}")
            cv2.imwrite(annotated_image_path, original_image)

            # Save log to the database
            CategoryBrandDetectionLog.objects.create(
                order=order,
                image_path=image_path,
                results=items_info,
                camera_type='upload',
            )

            return JsonResponse({'success': True, 'items_info': items_info, 'annotated_image': annotated_image_path})

        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'Seller/detect_items.html', {'order': order})