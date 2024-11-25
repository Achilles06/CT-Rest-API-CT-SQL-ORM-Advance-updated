from flask import Blueprint, jsonify, request
from models import db, Customer, Order
from sqlalchemy import func
from app import limiter

# Define the blueprint
customer_bp = Blueprint('customer_bp', __name__)

# Route to create a new customer
@customer_bp.route('', methods=['POST'])
@limiter.limit("10/minute")
def create_customer():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data or 'phone' not in data:
        return jsonify({'error': 'Bad request. Name, email, and phone are required.'}), 400
    
    new_customer = Customer(name=data['name'], email=data['email'], phone=data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'Customer created successfully'}), 201

# Route to fetch all customers
@customer_bp.route('', methods=['GET'])
@limiter.limit("15/minute")
def get_customers():
    customers = Customer.query.all()
    result = [{'id': cust.id, 'name': cust.name, 'email': cust.email, 'phone': cust.phone} for cust in customers]
    return jsonify(result), 200

# Task 3: Determine Customer Lifetime Value
@customer_bp.route('/lifetime-value', methods=['GET'])
def determine_customer_lifetime_value():
    # Get the minimum threshold for customer lifetime value from query parameters (default to 1000)
    min_value = request.args.get('min_value', 1000, type=float)

    # Query to calculate the total value of orders placed by each customer
    result = db.session.query(
        Customer.name,
        func.sum(Order.total_price).label('total_order_value')
    ).join(Order, Customer.id == Order.customer_id) \
     .group_by(Customer.name) \
     .having(func.sum(Order.total_price) >= min_value).all()

    # Format the result into a list of dictionaries
    lifetime_values = [{'customer': row.name, 'total_order_value': row.total_order_value} for row in result]
    
    return jsonify(lifetime_values), 200
