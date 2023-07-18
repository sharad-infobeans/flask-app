from flask import render_template, url_for, flash, redirect, request, Blueprint,jsonify
from ecommerce import db
from ecommerce.models import Product
api = Blueprint('api', __name__)

@api.route('/products', methods=['POST'])
def add_product():
    data = request.json  # Assuming you're sending JSON data in the request body
    
    # Create a new Product object with the provided data
    productdata = Product(
        name=data['name'],
        price=data['price'],
        quantity=data['quantity']
    )
    # Add the product to the database and commit the changes
    db.session.add(productdata) 
    db.session.commit()

    return jsonify({'message': 'Product added successfully'})

@api.route('/products', methods=['GET'])
def list_products():
    products = Product.query.all()

    product_list = []
    for product in products:
        product_list.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': product.quantity
        })

    return jsonify(product_list)


@api.route('/products/<int:product_id>', methods=['POST'])
def update_product(product_id):
    data = request.json  # Assuming you're sending JSON data in the request body

    # Get the product from the database by its ID
    product = Product.query.get_or_404(product_id)

    # Update the product attributes with the provided data
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.quantity = data.get('quantity', product.quantity)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({'message': 'Product updated successfully'})