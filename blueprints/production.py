from flask import Blueprint, jsonify, request
from models import db, Production, Product
from sqlalchemy import func
from datetime import datetime
from app import limiter

# Define the blueprint
production_bp = Blueprint('production_bp', __name__)

# Route to create a new production record
@production_bp.route('', methods=['POST'])
@limiter.limit("10/minute")
def create_production():
    data = request.get_json()
    if not data or 'product_id' not in data or 'quantity_produced' not in data or 'date_produced' not in data:
        return jsonify({'error': 'Bad request. Product ID, quantity produced, and date produced are required.'}), 400

    try:
        # Parse the date string into a datetime object
        date_produced = datetime.strptime(data['date_produced'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD format.'}), 400

    new_production = Production(product_id=data['product_id'], quantity_produced=data['quantity_produced'], date_produced=date_produced)
    db.session.add(new_production)
    db.session.commit()
    return jsonify({'message': 'Production record created successfully'}), 201

# Route to fetch all production records
@production_bp.route('', methods=['GET'])
@limiter.limit("15/minute")
def get_productions():
    productions = Production.query.all()
    result = [{'id': prod.id, 'product_id': prod.product_id, 'quantity_produced': prod.quantity_produced, 'date_produced': prod.date_produced} for prod in productions]
    return jsonify(result), 200

# Task 4: Evaluate Production Efficiency
@production_bp.route('/efficiency', methods=['GET'])
def evaluate_production_efficiency():
    # Get the production date from query parameters
    production_date = request.args.get('date', default=None)
    if production_date is None:
        return jsonify({'error': 'Production date is required.'}), 400
    
    # Parse the provided date
    try:
        production_date = datetime.strptime(production_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD format.'}), 400

    # Subquery to filter production records by date
    subquery = db.session.query(Production.id) \
                         .filter(Production.date_produced == production_date).subquery()

    # Query to calculate the total quantity produced for each product on the specified date
    result = db.session.query(
        Product.name,
        func.sum(Production.quantity_produced).label('total_quantity_produced')
    ).join(Production, Product.id == Production.product_id) \
     .filter(Production.id.in_(subquery)) \
     .group_by(Product.name).all()

    # Format the result into a list of dictionaries
    efficiency_data = [{'product': row.name, 'total_quantity_produced': row.total_quantity_produced} for row in result]
    
    return jsonify(efficiency_data), 200
