import os
from flask import Flask,url_for, flash, redirect, request,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager,current_user
from flask_session import Session

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
#############################################################################
############ CONFIGURATIONS (CAN BE SEPARATE CONFIG.PY FILE) ###############
###########################################################################

# Remember you need to set your environment variables at the command line
# when you deploy this to a real website.
# export SECRET_KEY=mysecret
# set SECRET_KEY=mysecret
app.config['SECRET_KEY'] = 'mysecret'

#################################
### DATABASE SETUPS ############
###############################

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
Migrate(app,db)


###########################
#### LOGIN CONFIGS #######
#########################

login_manager = LoginManager()

# We can now pass in our app to the login manager
login_manager.init_app(app)

# Tell users what view to go to when they need to login.
login_manager.login_view = "users.login"


###########################
#### BLUEPRINT CONFIGS #######
#########################

# Import these at the top if you want
# We've imported them here for easy reference
from ecommerce.core.views import core
from ecommerce.users.views import users
from ecommerce.error_pages.handlers import error_pages
from ecommerce.api.views import api  # Import the 'api' Blueprint from the respective module
from ecommerce.shop.views import shop,getLoginDetails

# Register the apps
app.register_blueprint(users)
app.register_blueprint(core)
app.register_blueprint(error_pages)
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(shop)
from ecommerce.models import Product, Cart,User

@app.context_processor
def inject_common_data():
    ourcart=[]
    
    if current_user.is_authenticated:
        noOfItems = getLoginDetails()
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
        ourcart = [{'cart': cart, 'subtotal': subtotal,'noOfItems':noOfItems}]

    else:
        ourcart = [{'cart': [], 'subtotal': 0,'noOfItems':0}]
    return {'ourcart': ourcart}


