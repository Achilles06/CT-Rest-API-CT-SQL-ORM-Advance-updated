from flask import Blueprint, jsonify, request
from models import db, Employee, Production
from sqlalchemy import func
from app import limiter

# Define the blueprint
employee_bp = Blueprint('employee_bp', __name__)

# Route to create a new employee
@employee_bp.route('', methods=['POST'])
@limiter.limit("10/minute")
def create_employee():
    data = request.get_json()
    if not data or 'name' not in data or 'position' not in data:
        return jsonify({'error': 'Bad request. Name and position are required.'}), 400
    
    new_employee = Employee(name=data['name'], position=data['position'])
    db.session.add(new_employee)
    db.session.commit()
    return jsonify({'message': 'Employee created successfully'}), 201

# Route to fetch all employees
@employee_bp.route('', methods=['GET'])
@limiter.limit("15/minute")
def get_employees():
    employees = Employee.query.all()
    result = [{'id': emp.id, 'name': emp.name, 'position': emp.position} for emp in employees]
    return jsonify(result), 200

# Task 1: Analyze Employee Performance
@employee_bp.route('/performance', methods=['GET'])
def analyze_employee_performance():
    # Query to calculate total quantity produced by each employee, grouped by name
    result = db.session.query(
        Employee.name,
        func.sum(Production.quantity_produced).label('total_quantity')
    ).join(Production, Employee.id == Production.product_id) \
     .group_by(Employee.name).all()

    # Format the result into a list of dictionaries
    performance_data = [{'employee': row.name, 'total_quantity': row.total_quantity} for row in result]
    
    return jsonify(performance_data), 200
