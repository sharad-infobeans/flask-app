from flask import Flask, render_template, flash, session, request,Blueprint, redirect, url_for
from flask_session import Session
from ecommerce import db
from ecommerce.models import Product, Cart,User
from flask_login import login_user, current_user, logout_user, login_required

shop = Blueprint('shop', __name__)



def getLoginDetails():
    if current_user.is_authenticated:
        noOfItems = Cart.query.filter_by(buyer=current_user).count()
    else:
        noOfItems = 0
    return noOfItems

@shop.route('/shop/checkout')
def cart_checkout():
        return render_template('checkout.html')

@shop.route('/')
def product_listing():
    # Fetch products from the database
    noOfItems = getLoginDetails()
    products = Product.query.all()
    if current_user.is_authenticated:
        cart = Product.query.join(Cart).add_columns(Cart.quantity, Product.price, Product.name, Product.id).filter_by(buyer=current_user).all()
        subtotal = 0
        for item in cart:
            subtotal+=int(item.price)*int(item.quantity)

        if request.method == "POST":
            qty = request.form.get("qty")
            idpd = request.form.get("idpd")
            cartitem = Cart.query.filter_by(product_id=idpd).first()
            cartitem.quantity = qty
            db.session.commit()
            cart = Product.query.join(Cart).add_columns(Cart.quantity, Product.price, Product.name, Product.id).filter_by(buyer=current_user).all()
            subtotal = 0
            for item in cart:
                subtotal+=int(item.price)*int(item.quantity)
    else:
        cart=[]
        subtotal=0
    return render_template('index.html', products=products,noOfItems=noOfItems,cart=cart,subtotal=subtotal)

@shop.route('/add-to-cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    # check if product is already in cart
    product = Product.query.get_or_404(product_id)
    row = Cart.query.filter_by(product_id=product_id, buyer=current_user).first()
    if product.quantity > 0:
        if row:
            # if in cart update quantity : +1
            row.quantity += 1
            product.quantity -= 1
            db.session.commit()
            flash('This item is already in your cart, 1 quantity added!', 'success')
            
            # if not, add item to cart
        else:
            user = User.query.get(current_user.id)
            user.add_to_cart(product_id)
            product.quantity -= 1
            db.session.commit()
    else:
        flash('Product is out of stock.', 'warning')
    return redirect('/')


@shop.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    noOfItems = getLoginDetails()
    # display items in cart
    cart = Product.query.join(Cart).add_columns(Cart.quantity, Product.price, Product.name, Product.id).filter_by(buyer=current_user).all()
    subtotal = 0
    for item in cart:
        subtotal+=int(item.price)*int(item.quantity)

    if request.method == "POST":
        qty = request.form.get("qty")
        idpd = request.form.get("idpd")
        cartitem = Cart.query.filter_by(product_id=idpd).first()
        cartitem.quantity = qty
        db.session.commit()
        cart = Product.query.join(Cart).add_columns(Cart.quantity, Product.price, Product.name, Product.id).filter_by(buyer=current_user).all()
        subtotal = 0
        for item in cart:
            subtotal+=int(item.price)*int(item.quantity)
    return render_template('cart.html', cart=cart, noOfItems=noOfItems, subtotal=subtotal)

@shop.route("/removeFromCart/<int:product_id>")
@login_required
def removeFromCart(product_id):
    product = Product.query.get_or_404(product_id)
    item_to_remove = Cart.query.filter_by(product_id=product_id, buyer=current_user).first()
    print(item_to_remove)
    if item_to_remove is not None:
        # Get the product associated with the cart item
        # Update the available quantity by adding the removed quantity back
        product.quantity += item_to_remove.quantity

        # Delete the cart item
        db.session.delete(item_to_remove)
        db.session.commit()

        flash('Your item has been removed from your cart!', 'success')
        return redirect(url_for('shop.cart'))
    else:
         flash('No products found to delete', 'success')


@shop.route('/updatecart', methods=['POST'])
@login_required  # Assuming you're using Flask-Login to handle user authentication
def updatecart():
    cart_items = Product.query.join(Cart).add_columns(Cart.quantity, Product.price, Product.name, Product.id).filter_by(buyer=current_user).all()

    for cart_item in cart_items:
        quantity = request.form.get(f'quantity-{cart_item.id}')
        if quantity is not None:
            cart = Cart.query.filter_by(product_id=cart_item.id, buyer=current_user).first()
            cart.quantity = int(quantity)

    db.session.commit()

    return redirect(url_for('shop.cart'))

