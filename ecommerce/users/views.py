from flask import render_template, url_for, flash, redirect, request, Blueprint,jsonify
from flask_login import login_user, current_user, logout_user, login_required
from ecommerce import db
from werkzeug.security import generate_password_hash,check_password_hash
from ecommerce.models import Product, Cart,User
from ecommerce.users.forms import RegistrationForm, LoginForm, UpdateUserForm
from ecommerce.users.picture_handler import add_profile_pic
from ecommerce.shop.views import getLoginDetails



users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    def generate_unique_username(firstname, lastname):
        # Generate unique username using firstname and lastname
        username = f"{firstname.lower()}.{lastname.lower()}"

        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{firstname.lower()}.{lastname.lower()}.{counter}"
            counter += 1

        return username

    if form.validate_on_submit():
          # Generate unique username using firstname and lastname
        username = generate_unique_username(form.firstname.data, form.lastname.data)
        user = User(firstname=form.firstname.data,
                    lastname=form.lastname.data,
                    username=username,
                    email=form.email.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash(f'Thanks for registering, "{username} "  Now you can login!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.check_password(form.password.data):
            # Log in the user
            login_user(user)
            flash('Logged in successfully.','success')

            # If a user was trying to visit a page that requires a login,
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next is None or not next.startswith('/'):
                next = url_for('users.dashboard')

            return redirect(next)
        else:
            flash('Invalid email or password.', 'warning')

    return render_template('login.html', form=form)


@users.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UpdateUserForm()
    if form.validate_on_submit():
        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data,username)
            current_user.profile_image = pic

        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        db.session.commit()
        flash('User Account Updated')
        return redirect(url_for('users.dashboard'))

    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
    noOfItems= getLoginDetails()
    
    return render_template('dashboard.html',profile_image=profile_image, form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


