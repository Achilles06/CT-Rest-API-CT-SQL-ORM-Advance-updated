from flask import Blueprint, jsonify, request
from models import db, Product
from utils.util import role_required

product_bp = Blueprint('product_bp', __name__)

# Only admin can create new products
@product_bp.route('', methods=['POST'])
@role_required('admin')
def create_product():
    """
    Create a new product (admin only).
    """
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({'error': 'Bad request. Name and price are required.'}), 400

    new_product = Product(name=data['name'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully'}), 201

# Both admin and user can view products
@product_bp.route('', methods=['GET'])
@role_required('user')  # Both admin and user roles can access this endpoint
def get_products():
    """
    Get the list of products (user or admin).
    """
    products = Product.query.all()
    result = [{'id': prod.id, 'name': prod.name, 'price': prod.price} for prod in products]
    return jsonify(result), 200
