
# MyRestaurant


## Table of Contents:
- About the Project
- Features
- Setup
    - Prerequisites
    - Installation
- Usage
- Features that can be added


## About the Project
This project focuses on creating a user-friendly, fully functional restaurant website. It aims to enhance the online food ordering experience. Customers will be able to browse the restaurant's categories and food menu. The website will enable customers to easily place orders. It ensures a smooth, convenient experience for users. The goal is to improve overall customer satisfaction with online ordering.








## Features
1- User Authentication & Authorization: Users can sign up, log in, and access protected routes using JWT tokens.

2- Role-based Access Control: Admins can manage the menu and users, while regular users can only order food and manage their profile.

3- Restaurant Menu Management: Admins can add, edit, or remove food items, and users can browse the menu.

4- Cart Management: Users can add, remove, update items, and view the total price of their cart.

5- Order Management: Users can place orders, moving items from the cart to the orders table, and view order history.

6- Search & Filtering (Optional): Users can search for food items and filter by categories or price.

7- Security & Validation: Validate inputs like phone numbers and emails, hash passwords securely, and implement authorization checks.


## Setup

1- Prerequisites

   - Python (version 3.12.3)
   - PostgreSQL – Database for storing product and user information.
   - Git – Version control system(git version 2.47.1)


2- Installation

Clone the repo with "git clone " and install the dependencies from the requirements.txt using "pip"

## Usage
- Start the program with "uvicorn main:app --reload"
- Access the application at http://localhost:8000
- Register/Login to your account
- Search menu for food
- Choose favorites and add in cart
- Proceed through the order process
## Features that can be added
- Payment Integration: Users can pay for their orders via an external payment system, and orders are confirmed upon successful payment.

- Notifications: Send notifications to users and admins for order status updates or low stock alerts.

- Admin Dashboard (Optional): Admins can manage users, orders, and food items via a dashboard interface.

- Search & Filtering (Optional): Users can search for food items and filter by categories or price.
