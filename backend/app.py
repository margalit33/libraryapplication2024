import json ,time,os
from flask import Flask, jsonify, request, render_template, send_from_directory,url_for
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.sqlite3'
app.config['SECRET_KEY'] = "random string"
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# models
# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
class Customer(db.Model):
    id = db.Column('customer_id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    age =  db.Column(db.Integer)
    loans = db.relationship('Loan', backref='customer', lazy=True)

    
    def __init__(self, name, city, age):
        self.name = name
        self.city = city
        self.age = age

class Book(db.Model):
    id = db.Column('book_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    author = db.Column(db.String(100))
    year_published = db.Column(db.Integer)
    book_type = db.Column(db.String(50))
    loans = relationship('Loan', backref='book')

    def __init__(self, name, author, year_published, book_type):
        self.name = name
        self.author = author
        self.year_published = year_published
        self.book_type = book_type
    
    @classmethod
    def update_book_type(cls):
        # Fetch all books from the database
        books = cls.query.all()
        
        # Iterate through each book and update its book_type based on loans
        for book in books:
            # Assume book has a list of loans (loans attribute)
            if book.loans:  
                latest_loan = max(book.loans, key=lambda loan: loan.loan_date)
                difference = latest_loan.return_date - latest_loan.loan_date
                if difference >= timedelta(days=10):
                    book.book_type = 1
                elif difference >= timedelta(days=5):
                    book.book_type = 2
                elif difference >= timedelta(days=2):
                    book.book_type = 3
                else:
                    book.book_type = None
            else:
                book.book_type = None
        
        # Commit the changes to the database
        db.session.commit()

class Loan(db.Model):
    id = db.Column('loan_id', db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)

    def __init__(self, customer_id, book_id, loan_date, return_date=None):
        self.customer_id = customer_id
        self.book_id = book_id
        self.loan_date = loan_date
        self.return_date = return_date

  
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = str(data['password'])  # Ensure password is converted to a string
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    is_admin = data.get('is_admin', False)
    new_user = User(username=username, password=hashed_password, is_admin=is_admin)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = str(data['password'])  # Ensure password is converted to a string
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid username or password'}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if current_user and not current_user.is_admin:
            return jsonify({'message': 'Admin permission required'}), 403
        return fn(*args, **kwargs)
    return wrapper

# Define a decorator to check if the user is logged in
def user_logged_in(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({'message': 'User login required'}), 401
        return fn(*args, **kwargs)
    return wrapper
    
#crud Customer
#read all the customers
@app.route('/customers')
def show_all_customers():
    customers = Customer.query.all()
    customer_data = [{"id": customer.id, "name": customer.name, "city": customer.city, "age": customer.age} for customer in customers]
    return jsonify(customer_data)
   
#add/create a customer 
@app.route('/new_customer', methods = ['GET', 'POST'])
@jwt_required()
@admin_required
def new():
    request_data = request.get_json()
    city = request_data['city']
    name= request_data["name"]
    age= request_data["age"]
    newCustomer= Customer(name,city,age)
    db.session.add (newCustomer)
    db.session.commit()
    return "a new customer was create"
 
#Delete the customer according to the id
@app.route('/del_customer/<id>', methods = ['DELETE'])
@jwt_required()
@admin_required
def delete(id=-1):
    del_row = Customer.query.filter_by(id=id).first()
    if del_row:
        db.session.delete(del_row)
        db.session.commit()
        return "a row was delete"
    return "no such customer...."    


# Update the customer according to the id
@app.route('/upd_customer/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_customer(id):
    try:
        request_data = request.get_json()
        city = request_data.get('city')
        name = request_data.get('name')
        age = request_data.get('age')
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({'message': 'Customer not found'}), 404
        if city:
            customer.city = city
        if name:
            customer.name = name
        if age:
            customer.age = age
        db.session.commit()
        return jsonify({'message': 'Customer updated'}), 200
    except Exception as e:
        return jsonify({'message': 'Error updating customer'}), 500

# Find customer by name
@app.route('/find_customer_by_name', methods=['GET'])
@jwt_required()
@admin_required
def find_customer_by_name():
    customer_name = request.args.get('name')

    if customer_name:
        # Case-insensitive search for customers by name
        customers = Customer.query.filter(func.lower(Customer.name) == func.lower(customer_name)).all()

        if customers:
            return jsonify([{"id": customer.id, "name": customer.name, "city": customer.city, "age": customer.age} for customer in customers])
        else:
            return "No customers found with the given name"
    else:
        return "Please provide a customer name in the query parameters"


# CRUD operations for books
#read all the books

@app.route('/books')
def show_all_books():
    books = Book.query.all()
    book_data = [{"id": book.id, "name": book.name, "author": book.author, "year_published": book.year_published, "book_type": book.book_type}
        for book in books]
    return jsonify(book_data)

#add a book
@app.route('/new_book', methods=['GET', 'POST'])
@jwt_required()
@admin_required
def new_book():
    if request.method == 'POST':
        request_data = request.get_json()
        name = request_data['name']
        author = request_data['author']
        year_published = request_data['year_published']
        book_type = request_data['book_type']  

        new_book = Book(name, author, year_published, book_type)
        db.session.add(new_book)
        db.session.commit()
        return "A new book record was created"
    else:
        return "Method not allowed"

#Delete the book according to the id
@app.route('/del_book/<id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_book(id):
    del_book = Book.query.filter_by(id=id).first()
    if del_book:
        db.session.delete(del_book)
        db.session.commit()
        return "A book was deleted"
    return "No such book found"


#update the book according to the id
@app.route('/upd_book/<id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_book(id):
    request_data = request.get_json()
    upd_book = Book.query.filter_by(id=id).first()
    if upd_book:
        upd_book.name = request_data['name']
        upd_book.author = request_data['author']
        upd_book.year_published = request_data['year_published']
        upd_book.book_type = request_data['book_type']
        db.session.commit()
        return "A book record was updated"
    return "No such book found"



# Find book by name
@app.route('/find_book_by_name', methods=['GET'])
def find_book_by_name():
    book_name = request.args.get('name')

    if book_name:
        # Case-insensitive search for books by name
        books = Book.query.filter(func.lower(Book.name) == func.lower(book_name)).all()

        if books:
            return jsonify([{"id": book.id, "name": book.name, "author": book.author, "year_published": book.year_published, "book_type": book.book_type} for book in books])
        else:
            return "No books found with the given name"
    else:
        return "Please provide a book name in the query parameters"



#return a book
@app.route('/return_book/<loan_id>', methods=['PUT'])
@jwt_required()
@user_logged_in
def return_book(loan_id):
    request_data = request.get_json()
    return_date = request_data.get('return_date', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    loan = Loan.query.filter_by(id=loan_id).first()
    if loan:
        loan.return_date = return_date
        db.session.commit()
        return "Book returned successfully"
    return "No such loan found"


#function that checks whether a book was returned on time based on the book type
def is_return_on_time(loan_date, return_date, book_type):
    # Assuming loan_date and return_date are datetime objects
    # Calculate the difference between return_date and loan_date
    time_difference = return_date - loan_date
    if book_type == 1 and time_difference <= timedelta(days=10):
        return True
    elif book_type == 2 and time_difference <= timedelta(days=5):
        return True
    elif book_type == 3 and time_difference <= timedelta(days=2):
        return True
    else:
        return False


# CRUD for loans
#display all loans

@app.route('/loans')
def show_all_loans():
    loans = Loan.query.all()
    loan_data = [{"id": loan.id, "customer_id": loan.customer_id, "book_id": loan.book_id, 
    "loan_date": loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'), "return_date": loan.return_date.strftime('%Y-%m-%d %H:%M:%S') 
    if loan.return_date 
        else None} for loan in loans]
    return jsonify(loan_data)


#display late loans
@app.route('/late_loans', methods=['GET'])
@jwt_required()
@admin_required
def get_late_loans():
    late_loans = []

    # Assuming Loan has a relationship with Book, adjust accordingly
    for loan in Loan.query.all():
        if loan.return_date and loan.book and not is_return_on_time(loan.loan_date, loan.return_date, loan.book.book_type):
            late_loans.append({
                "id": loan.id,
                "customer_id": loan.customer_id,
                "book_id": loan.book_id,
                "loan_date": loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
                "return_date": loan.return_date.strftime('%Y-%m-%d %H:%M:%S')
            })

    return jsonify(late_loans)


@app.route('/new_loan', methods=['POST','PUT'])
@jwt_required()
@admin_required
def new_loan():
    request_data = request.get_json()
    customer_id = request_data['customer_id']
    book_id = request_data['book_id']
    loan_date = request_data['loan_date']
    return_date = request_data.get('return_date')
    
    # Convert date-time strings to datetime objects
    loan_date = datetime.strptime(loan_date, '%Y-%m-%d %H:%M:%S')
    return_date = datetime.strptime(return_date, '%Y-%m-%d %H:%M:%S') if return_date else None
    
    new_loan = Loan(customer_id=customer_id, book_id=book_id, loan_date=loan_date, return_date=return_date)
    db.session.add(new_loan)
    db.session.commit()
    
    # Update the book_type for the associated book after adding the loan
    Book.update_book_type()
    
    return "A new loan record was created successfully"

    
#delete loan
@app.route('/del_loan/<id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_loan(id=-1):
    del_loan = Loan.query.filter_by(id=id).first()
    if del_loan:
        db.session.delete(del_loan)
        db.session.commit()
        return "A loan record was deleted"
    return "No such loan record"

@app.route('/loan_book', methods=['POST'])
@jwt_required()
@user_logged_in
def loan_book():
    request_data = request.get_json()
    customer_id = request_data['customer_id']
    book_id = request_data['book_id']
    customer = Customer.query.filter_by(id=customer_id).first()
    book = Book.query.filter_by(id=book_id).first()
    if customer and book:
        # Check if the book is available for loan
        if not is_book_available_for_loan(book_id):
            return "The book is not available for loan"

        # Create a new loan record
        loan_date = datetime.utcnow()
        return_date = None  # Assuming the book is not returned at the time of loaning
        new_loan = Loan(customer_id=customer_id, book_id=book_id, loan_date=loan_date, return_date=return_date)
        db.session.add(new_loan)
        db.session.commit()
        return "Book loaned successfully"
    return "Customer or book not found"


def is_book_available_for_loan(book_id):
    # Check if the book is already on loan
    existing_loan = Loan.query.filter_by(book_id=book_id, return_date=None).first()
    return not existing_loan


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    

# http://127.0.0.1:5000