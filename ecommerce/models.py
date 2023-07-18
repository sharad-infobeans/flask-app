from flask import Flask, flash, session, request,Blueprint, redirect, url_for
from ecommerce import db,login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
# By inheriting the UserMixin we get access to a lot of built-in attributes
# which we will be able to call in our views!
# is_authenticated()
# is_active()
# is_anonymous()
# get_id()


# The user_loader decorator allows flask-login to load the current user
# and grab their id.

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):

    # Create a table in the db
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    firstname=db.Column(db.String(64))
    lastname=db.Column(db.String(64))
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True)
    profile_image = db.Column(db.String(20), nullable=False, default='default_profile.png')
    password_hash = db.Column(db.String(128))
    cart = db.relationship('Cart', backref='buyer', lazy=True)

    def add_to_cart(self,product_id):
        item_to_add = Cart(product_id=product_id, user_id=self.id)
        db.session.add(item_to_add)
        db.session.commit()
        flash('Your item has been added to your cart!', 'success')

    def __init__(self,firstname,lastname, email, username, password):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        # https://stackoverflow.com/questions/23432478/flask-generate-password-hash-not-constant-output
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f"First Name: {self.firstname}"

    def save_profile_image(self, image):
            extension = image.filename.split('.')[-1]  # Get the file extension
            filename = f"{self.id}.{extension}"  # Generate a unique filename using the user's ID
            image.save(f"static/profile_pics/{filename}")  # Save the image to a desired location
            self.profile_image = filename  # Update the profile_image attribute

class Product(db.Model):

    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self,name,price,quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return f"Product Name: {self.name}"


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # def update_qty(self, qty):
    #     cartitem = Cart.query.filter_by(product_id=self.id).first()
    #     cartitem.quantity = qty
    #     db.session.commit()
    def __repr__(self):
        return f"Cart('Product id:{self.product_id}','id: {self.id}','User id:{self.user_id}'')"