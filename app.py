from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db
from blueprints.employee import employee_bp
from blueprints.products import product_bp
from blueprints.order import order_bp
from blueprints.customer import customer_bp
from blueprints.production import production_bp

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    
    # Configuration settings
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/factory.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)

    # Register Blueprints
    app.register_blueprint(employee_bp, url_prefix='/employees')
    app.register_blueprint(product_bp, url_prefix='/products')
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(production_bp, url_prefix='/production')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)


from sqlalchemy import func, desc
from flask import jsonify, request

# Advanced Querying Functions

@app.route('/employee-performance', methods=['GET'])
def employee_performance():
    results = session.query(
        Employee.name,
        func.sum(Production.quantity).label('total_quantity')
    ).join(Production).group_by(Employee.name).all()
    return jsonify([{'name': r[0], 'total_quantity': r[1]} for r in results])

@app.route('/top-selling-products', methods=['GET'])
def top_selling_products():
    results = session.query(
        Product.name,
        func.sum(Order.quantity).label('total_quantity')
    ).join(Order).group_by(Product.name).order_by(desc('total_quantity')).all()
    return jsonify([{'product_name': r[0], 'total_quantity': r[1]} for r in results])

@app.route('/customer-lifetime-value', methods=['GET'])
def customer_lifetime_value():
    threshold = request.args.get('threshold', type=float)
    results = session.query(
        Customer.name,
        func.sum(Order.total_price).label('total_order_value')
    ).join(Order).group_by(Customer.name).having(func.sum(Order.total_price) >= threshold).all()
    return jsonify([{'customer_name': r[0], 'total_order_value': r[1]} for r in results])

@app.route('/production-efficiency', methods=['GET'])
def production_efficiency():
    specific_date = request.args.get('date', type=str)
    subquery = session.query(Production).filter(Production.date == specific_date).subquery()
    results = session.query(
        Product.name,
        func.sum(subquery.c.quantity).label('total_quantity')
    ).join(Product, Product.id == subquery.c.product_id).group_by(Product.name).all()
    return jsonify([{'product_name': r[0], 'total_quantity': r[1]} for r in results])
