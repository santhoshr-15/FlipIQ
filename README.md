# 🎯Flipkart Grid 6.0 Robotic Challenge

## 🎥 FlipIQ in Action!

Watch this demo video to see FlipIQ in action! 🚀

https://drive.google.com/file/d/19D83m61gtqdWOlJPh5cJsa5Ec-4SRwCJ/view

## 🎗️Problem Statement:
### Problem Statement:
In modern retail environments, automating inventory and product information capture is essential for operational efficiency. The challenge is to develop a vision-based AI system capable of extracting structured product details from packed product images.

### Objective:
Build a robust AI-powered system that can accurately identify and extract key information from product packaging images, including:

✅ Brand Name

✅ Maximum Retail Price (MRP)

✅ Manufacturing Date (MFD)

✅ Expiry Date (EXP)

✅ Net Quantity / Weight

### Constraints & Considerations:

The text may appear in various orientations, fonts, and lighting conditions.

Some details may be embedded in cluttered backgrounds or artistic packaging.

The system must handle multiple languages or numeric formats (e.g., "MRP ₹45.00", "EXP: 12/25", etc.).

High precision is required for brand name detection, especially when it overlaps with other promotional content.

### Deliverables:

An OCR-based pipeline that localizes and extracts the above details.

A method (preferably using deep learning or NLP techniques) to determine brand names from noisy text outputs.

A structured JSON output per image containing all extracted fields.


## 🌟Project Overview
This AI-powered solution is designed to:
- 🏷️ Detect **product brand names**.
- 🍃 Assess **freshness levels**.
- 📅 Extract **expiry dates** from product images.  

---

## ✨Key Features

### 🏷️Brand Name Detection
- Uses **YOLO** to detect product's text regions.
- Extracts **brand names**, **product type**, and **flavor details** using **PaddleOCR**.

### 🍃Freshness Detection
- Identifies **unpacked products** and assesses appearance using **YOLO** and **ResNet** for identifying the freshness of the item.
- Predicts **freshness levels** based on visual cues.
- Estimates **remaining shelf life** with lifespan prediction models.

### 📅Expiry Date Detection
- Utilizes **YOLO** for bounding regions containing expiry dates.
- Combines **Faster R-CNN with ResNet45** for text extraction.
- Verifies and parses **date-like patterns** using regex-based **DMY detection**.

---

## 🚀Future Scope
- Improve model **efficiency, speed, and accuracy**.  
- Expand capabilities for **new use cases**.  
- Enhance **multilingual support**.  

---

## 🛠️Technology Stack

### 🎨Frontend
- **HTML/CSS/JavaScript**: For creating a responsive, user-friendly interface.
- **Django Templates**: For rendering pages dynamically.

### ⚙️Backend
- **Django**: Framework for building scalable and secure web applications.
- **Django Object-Relational Mapping (ORM)**: For interacting with the database in an intuitive and efficient way.
- **Business Logic Integration**: Handles predictions, freshness scoring, and expiry detection.

### 🤖Machine Learning
- **YOLO**: For object detection (frehness, expiry regions, product appearance).
- **PaddleOCR**: For Optical Character Recognition (OCR).
- **ResNet50**: For identifying the freshness of the items.
- **Faster R-CNN with ResNet45**: For high-accuracy text detection.

### 💾Data Storage
- **NoSQL Database (MongoDB)**: Stores unstructured data like detected text and logs.

### 🌐Deployment
- **Colab Notebooks**: For training and testing models.
- **Kaggle Notebooks**:For training and testing models in GPU environment for training large datasets
- **Docker**: For scalable deployments.
### ✨Computer vision software platform :
- **Roboflow** - Software used to label and annotation the dataset.
- **LableImg** - Software used to label and annotation the dataset.
  
### 💻Programming Languages:
- **Python**: Backend development, ML model implementation, and data processing.
- **JavaScript**: For frontend interactivity.

### 📚Libraries and Frameworks:
- **OpenCV**: Image processing and visualization.
- **NumPy/Pandas**: For data handling.
- **Matplotlib/Seaborn**: For data visualization.
- **Regex**: To extract patterns like dates.

### 🔗APIs:
- **PaddleOCR API**: For multilingual text recognition.
- **Custom Django REST APIs**: For frontend-backend communication.

### 🌟Version Control:
- **Git/GitHub**: For managing the codebase and collaboration.

---
## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Santhosh-0031/FlipIQ
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Run the development server:
   ```bash
   python manage.py runserver


## 🛒User Guide for FlipIQ  

Welcome to **FlipIQ**, a platform designed for **Customers**, **Sellers**, and **Admins**. This guide will walk you through the process of registering, logging in, and navigating the system based on your role.

---

## 🌐 Accessing the Website  
1. Open your browser and go to the **FlipVision website**.  
2. On the homepage, you will find login options for:
   - **Customer**
   - **Seller**
   - **Admin**

---

## 👤 Customer Workflow  

### 1. Registering as a Customer  
If you are a new customer, follow these steps:  
- Select **Customer** from the dropdown menu.  
- Fill out the registration form with the following information:  
  - **Username**  
  - **Email Address**  
  - **First Name and Last Name**  
  - **Password** (Ensure it is strong)  
  - **Phone Number**  
  - **Address**  
  - **City, State, and Pincode**  
- Click on **Register** to create your account.  

### 2. Logging in as a Customer  
Once registered, log in by:  
- Selecting **Customer** from the dropdown.  
- Entering your **username** and **password**.  
- Clicking the **Login** button.  

### 3. Ordering Products  
After logging in:  
- Browse the products on the platform.  
- Use the following filters to refine your search:  
  - **Categories**: Packed or Unpacked Items  
  - **Price Range**: Set minimum and maximum price  
  - **Sort by**: Sort products by price or other criteria  
- Click **Add to Cart** to add products for purchase.  
- You can also add items to your **Wishlist** for future reference.  

### 4. Checkout  
To complete your purchase:  
- Go to your **Cart**.  
- Review your selected products.  
- Click **Proceed to Checkout** to finalize the order.  

### 5. Order Process  
- Your order will be forwarded to the respective seller for processing.  

---

## 🛍️ Seller Workflow  

### 1. Registering as a Seller  
If you are a new seller, follow these steps:  
- Select **Seller** from the dropdown menu.  
- Fill out the registration form with the necessary details.  
- Click **Register** to create your account.  

### 2. Logging in as a Seller  
Once registered, log in by:  
- Selecting **Seller** from the dropdown.  
- Entering your **username** and **password**.  
- Clicking the **Login** button.  

### 3. Setting up the Seller Profile  
After logging in, access your **Seller Dashboard**:  
- Update your profile with the following information:  
  - **Company Name**  
  - **GST Number**  
  - **Bank Account Details**  
- Wait for the **Admin** to verify your profile.  

### 4. Adding Products  
Once verified:  
- Navigate to the **Product Management Area**.  
- Add products by providing:  
  - **Product Name**  
  - **Category**: Packed or Unpacked  
  - **Description**  
  - **Price**  
  - **Stock Quantity**  
  - **Discount Percentage**  
  - **Product Image**  
- Optionally, mark products as **Featured**.  
- Manage your products using the **Manage Products** button.  

### 5. Handling Orders  
- View orders in the **Recent Orders** section, which displays:  
  - **Order ID**  
  - **Customer Name**  
  - **Total Amount**  
  - **Status**  
- Click on an order to **View Details**.  

### 6. Validating Products  

#### For Unpacked Products (Fruits/Vegetables):  
- Select **Freshness Analysis**.  
- Access a camera from the dropdown or upload an image.  
- Click **Detect** to get the freshness results.  

> **Note**: The freshness model is trained on the following classes:  
> - **Apple**  
> - **Carrot**  
> - **Banana**  
> - **Cucumber**  
> - **Orange**  

#### For Packed Products:  
- Perform **Brand Detection** and **Expiry Detection**:  
  - Capture an image or upload it.  
  - Click **Detect** to get the results.  
- Ensure the products belong to these classes:  
  - **Chips**  
  - **Biscuits**  
  - **Chocolates**  

### 7. Updating Order Status  
- Once products are validated and shipped, update the order status using the **Update Status** button.  

---

## 👩‍💼 Admin Workflow  
The **Admin** oversees and verifies seller profiles, manages orders, and ensures smooth platform operations.

---

## 📌 Key Notes  
1. Ensure all required details are provided during registration.  
2. Follow the appropriate workflow based on your role.  
3. Adhere to the model constraints for unpacked products.  

Enjoy your experience on **FlipIQ**! 🚀  



## 📸Screenshots and Outputs

### 1. Homepage
- FlipIQ  
![image](https://github.com/user-attachments/assets/03d03268-71d8-4a5e-9807-1c17f589d58c)


### 2. Brand Name Detection
- Example of a detected brand name with bounding boxes.
  <table>
<tr>
<td>
  
![image](https://github.com/user-attachments/assets/6df98ea6-4a09-4672-a9dc-d99799552058)
</td> 
<td>
  
![image](https://github.com/user-attachments/assets/59bf5606-d2ef-41c5-b42b-1777d28bca5c)
</td>
</tr> 
<tr>
<td>
  
![WhatsApp Image 2024-12-11 at 20 15 29_eb32c2be](https://github.com/user-attachments/assets/398dd991-0e50-4b94-ae57-3674cc1428ec)

</td> 
<td>
  
![WhatsApp Image 2024-12-11 at 20 17 27_40dd8dc0](https://github.com/user-attachments/assets/dbe6691a-3bc5-4c1c-9d26-fe97cf93bb5e)

</td>
</tr> 
</table>


### 3. Freshness Detection
- Output showcasing the freshness level assessment.
<table>
<tr>
<td>
  
![Screenshot 2024-12-09 102916](https://github.com/user-attachments/assets/d9c67007-20ea-42c1-831c-a81685f6657c)


</td> 
<td>
  
![Screenshot 2024-12-09 103358](https://github.com/user-attachments/assets/5b9d393e-ade0-4c52-8936-d0184fe46fc0)


</td>
</tr> 
<tr>
<td>
  
![WhatsApp Image 2024-12-11 at 20 43 49_59a998a5](https://github.com/user-attachments/assets/b49d3c11-95fc-4347-8c41-2b61dc87bdb0)

</td> 
<td>
  
![WhatsApp Image 2024-12-11 at 20 34 33_675fb8cb](https://github.com/user-attachments/assets/721bdd63-3908-40fd-b24e-3cd352129120)


</td>
</tr> 
</table>

### 4. Expiry Date Detection
- Example output of the expiry date detection model.
<table>
<tr>
<td>
  
![image](https://github.com/user-attachments/assets/a8d600f4-4a67-4142-9940-6bac7a59ff69)
</td> 
<td>
  
![image](https://github.com/user-attachments/assets/11743aaa-9984-4138-96ed-522f782d7ad1)

</td>
</tr>
<tr>
<td>
  
![Screenshot 2024-12-11 203255](https://github.com/user-attachments/assets/c17cae87-83f8-4e49-b776-9fd9524aaa63)

</td>
<td>
  
![WhatsApp Image 2024-12-11 at 20 03 01_050451a5](https://github.com/user-attachments/assets/80931929-f4c2-4d2a-a03b-4b186c024538)

</td>
</tr> 
</table>


### 5. Complete Workflow
- Screenshot of flowchart illustrating the end-to-end system.
![image](https://github.com/user-attachments/assets/734c9b15-8121-46c9-9145-9d0c26a124cd)

## Contributors

We welcome contributions to FlipIQ! Feel free to fork this repo, create new features, or report bugs. Together, we can make FlipIQ the best e-commerce platform out there!

 Explore FlipIQ Now! 

Access the website: https://app.saveetha.in

## Connect With Us

Website: https://app.saveetha.in

Happy shopping and selling on FlipIQ!
