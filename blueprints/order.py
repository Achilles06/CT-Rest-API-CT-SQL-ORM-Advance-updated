# blueprints/order.py

from flask import Blueprint, jsonify, request
from models import db, Order

order_bp = Blueprint('order_bp', __name__)

@order_bp.route('', methods=['GET'])
def get_orders():
    # Get page and per_page from query parameters with defaults
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Paginate the orders
    orders_pagination = Order.query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get paginated orders
    orders = orders_pagination.items

    # Create response format
    result = [{
        'id': ord.id,
        'customer_id': ord.customer_id,
        'product_id': ord.product_id,
        'quantity': ord.quantity,
        'total_price': ord.total_price
    } for ord in orders]

    # Include pagination metadata in the response
    return jsonify({
        'orders': result,
        'total': orders_pagination.total,
        'page': orders_pagination.page,
        'pages': orders_pagination.pages,
        'per_page': orders_pagination.per_page
    }), 200
