# The Library Application

## Overview
The Library Application is a web-based system that facilitates the management of books, customers, and loans. It offers CRUD (Create, Read, Update, Delete) functionality for customers, books, and loans. Admin users have full access to CRUD operations, while regular users can only perform loan and return actions.

## Features
- **Admin Functions:**
  - Create, read, update, and delete customers
  - Create, read, update, and delete books
  - Create, read, update, and delete loans

- **Public Access:**
  - Read the list of available books
  - Find a book by name

- **User Functions:**
  - Loan a book
  - Return a book

## Methods Used
- **GET** `/customers`: Retrieves all customers.
- **GET** `/customers/<customer_id>`: Retrieves a specific customer by ID.
- **POST** `/customers`: Creates a new customer.
- **PUT** `/customers/<customer_id>`: Updates an existing customer.
- **DELETE** `/customers/<customer_id>`: Deletes a customer.

- **GET** `/books`: Retrieves all books.
- **GET** `/books/<book_id>`: Retrieves a specific book by ID.
- **POST** `/books`: Creates a new book.
- **PUT** `/books/<book_id>`: Updates an existing book.
- **DELETE** `/books/<book_id>`: Deletes a book.

- **GET** `/loans`: Retrieves all loans.
- **GET** `/loans/<loan_id>`: Retrieves a specific loan by ID.
- **POST** `/loans`: Creates a new loan.
- **PUT** `/loans/<loan_id>`: Updates an existing loan.
- **DELETE** `/loans/<loan_id>`: Deletes a loan.

- **GET** `/books/list`: Retrieves the list of available books.
- **GET** `/books/search/<book_name>`: Finds a book by name.

- **POST** `/users/login`: Logs in a user.
- **POST** `/users/logout`: Logs out a user.
- **POST** `/users/register`: Registers a new user.

## Requirements
- bcrypt==4.1.2
- blinker==1.7.0
- click==8.1.7
- colorama==0.4.6
- Flask==3.0.0
- Flask-Bcrypt==1.0.1
- Flask-Cors==4.0.0
- Flask-JWT-Extended==4.6.0
- Flask-SQLAlchemy==3.1.1
- greenlet==3.0.3
- itsdangerous==2.1.2
- Jinja2==3.1.2
- MarkupSafe==2.1.3
- mysql-connector==2.2.9
- mysql-connector-python==8.2.0
- protobuf==4.21.12
- PyJWT==2.8.0
- SQLAlchemy==2.0.24
- typing_extensions==4.9.0
- Werkzeug==3.0.1

## Usage
1. Clone the repository:
2. Install dependencies:pip install -r requirements.txt
3. Run the application: python app.py

4. Access the application in your web browser at `http://localhost:5000`

## Usage Notes
- To access admin functionalities, login with admin credentials.
- Regular users can only access loan and return functionalities.
- Ensure MySQL is running and configured properly.

## Credits
This application is created and maintained by Margalit Assayag.





