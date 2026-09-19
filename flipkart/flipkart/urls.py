from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from flipkart_app import views

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Home Page
    path('', views.HomeView.as_view(), name='home'),

    # Product Listings and Detail Views
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),

    # Cart Management
    path('cart/', views.cart_detail, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),

    # Checkout Process
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    # User Profile and Order History
    path('user_profile/', views.profile, name='profile'),
    path('order-history/', views.order_history, name='order_history'),

    # User Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # Seller Dashboard
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),

    # Wishlist Management
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),

    # Order Tracking and Management
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    # Seller Profile and Product Management
    path('complete-seller-profile/', views.complete_seller_profile, name='complete_seller_profile'),
    path('add-product/', views.add_product, name='add_product'),
    path('seller/manage-products/', views.manage_products, name='manage_products'),
    path('seller/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('seller/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('seller-support/', views.seller_support, name='seller_support'),
    path('detect-freshness/<int:order_id>/', views.detect_freshness, name='detect_freshness'),
    path('detect-items/<int:order_id>/', views.detect_items, name='detect_items'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

