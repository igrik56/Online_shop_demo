import os

from flask import Flask, render_template, flash, redirect, session, g
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from forms import *
from models import *
from convert import Convert
import pandas as pd

CURR_USER_KEY = "curr_user"
CART = 'cart'
ADMIN_ID = os.environ.get('ADMIN_ID', 'Kolobok_admin')

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///shop'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

app.app_context().push()
connect_db(app)
db.create_all()


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    '''If user logged in, add curr user to Flask global.'''

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    '''Log in user.'''

    session[CURR_USER_KEY] = user.id

    if CART not in session:
        session[CART] = []


def do_logout():
    '''Logout user.'''

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def get_currency(location): # pass location as var
    '''Getting currency based on user's location'''
    return Convert.check(location)    
    # return currency

@app.route('/')
def homepage():
    '''Show homepage'''
    if g.user:
        if g.user.location:
            products = (Product
                        .query
                        .order_by(Product.name)
                        .all())
            
            currency = get_currency(g.user.location)

            return render_template('home.html', currency = currency, products=products, ADMIN_ID = ADMIN_ID)
    else:
        return render_template('home-anon.html')
        

@app.route('/signup', methods=["GET", "POST"])
def admin_signup():
    '''Handle user signup. Only admin of the website
        is allowed to add new users.'''
    
    # print(type(g.user))

    if g.user.username in ADMIN_ID:

        form = UserAddForm()

        if form.validate_on_submit():
            try:
                User.signup(
                    username=form.username.data,
                    location=form.location.data,
                    address=form.location.data,
                    password=form.password.data,
                    email=form.email.data,
                    # image_url=form.image_url.data or User.image_url.default.arg
                )
                db.session.commit()

            except IntegrityError:
                db.session.rollback()
                flash("Username already taken", 'danger')
                return render_template('admin/signup.html', form=form)

            return redirect("/", 404) #will redirect user back to home page in case it's not Admin.

        else:
            return render_template('admin/signup.html', form=form, ADMIN_ID = ADMIN_ID, )
    else: return redirect ('/')


@app.route('/login', methods=["GET", "POST"])
def login():
    '''Handle user login.'''

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def user_delete(user_id):
    '''Delete user.'''

    if not g.user.username in ADMIN_ID:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()

    return redirect("/")


@app.route('/logout')
def logout():
    '''Handle logout of user.'''

    do_logout()
    flash("Farewell.", "success")
    return redirect('/login')



##############################################################################
# General user routes:

@app.route('/users/update', methods=["GET", "POST"])
def user_update():
    '''Update profile for current user.'''

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = UserEditFrom()

    if form.validate_on_submit(): 
        user = User.query.get_or_404(session[CURR_USER_KEY])

        email = form.email.data if form.email.data else user.email 
        image_url = form.image_url.data if form.image_url.data else user.image_url
        location = form.location.data if form.location.data else user.location
        address = form.address.data if form.address.data else user.address

        pw = form.password.data if form.password.data else redirect('/')


        user = User.edit(user.id, email, image_url, pw, location, address)

        if user:
            db.session.add(user)
            db.session.commit()
            flash("Profile updated.", "success")
            return redirect(f'/users/{user.id}')
        else: 
            flash("Access unauthorized.", "danger")
            return redirect ('/')

    return render_template('users/edit.html', form=form)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    '''Show user profile.'''

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    elif g.user.username in ADMIN_ID:
        flash('Admin check', 'success')
    elif g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    orders = (Order   
                .query
                .filter(Order.user_id == user.id)
                .order_by(Order.timestamp)
                .limit(10)
                .all())

    return render_template('users/show.html', user = user, ADMIN_ID = ADMIN_ID, orders = orders)


@app.route('/users/<int:user_id>/orders')
def users_orders(user_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    elif g.user.username in ADMIN_ID:
        flash('Admin check', 'success')
    elif g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    orders = user.orders

    return render_template('users/orders.html', user = user, ADMIN_ID = ADMIN_ID, orders = orders)

##############################################################################
# Products routes:

@app.route('/products/new', methods=["GET", "POST"])
def produts_add():
    '''Add a product:

    Show form if GET. If valid, update product and redirect to user page.
    '''

    if not g.user.username in ADMIN_ID:             # only admin can add new products.
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = ProductAddForm()

    if form.validate_on_submit():
        try:
            Product.add(
                form.name.data,
                form.category.data,
                form.weight.data,
                form.description.data,
                form.price.data,
                form.quantity.data,
                form.image_url.data
            )

        except IntegrityError:
                db.session.rollback()
                flash("Product already exists. Use edit", 'danger')
                return redirect("/")    
        flash("Product added!", 'success')
        return redirect('/')

    return render_template('admin/product_add.html', form=form, ADMIN_ID = ADMIN_ID)


@app.route('/products/<int:product_id>', methods=["GET", "POST"])
def products_show(product_id):
    '''Show a product.'''

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect ('/')
    
    product = Product.query.get_or_404(product_id)
    currency = get_currency(g.user.location)

    form = AddToCartForm()

    if form.validate_on_submit():

        if product.quantity < 1:
            flash("Product is sold out and can't be added at this time", 'warning')
            return redirect('/')

        quantity = form.quantity.data if form.quantity.data > 0 else 1

        if quantity > product.quantity:
            flash(f"""Your desire for {product.name} is noted! 
                  Unfortunatly we are unable to satisfy it at 
                  the moment. Please choose lower quantity.""", 'warning')
            return redirect(f'/products/{product.id}')
        
        cart_list = session[CART]
        
        cart_list.append(
            {
                'product_id': product_id,
                'quantity' : quantity,
            }
        )

        df = pd.DataFrame(cart_list)                    # checking for duplicates in a cart. If found removes old entery
        df.drop_duplicates(subset = ['product_id'], keep = 'last', inplace = True)
        new_cart_list = df.to_dict('records')
        
        if new_cart_list != cart_list:
            flash('No duplicates in a cart allowed. Previous entery was removed.')
        session[CART] = new_cart_list
        


        flash("Item added to your cart", "success")
        return redirect('/')    

    return render_template('products/details.html', 
                           product = product, 
                           currency = currency, 
                           form = form,
                           ADMIN_ID = ADMIN_ID)


@app.route('/products/<int:product_id>/update', methods=["GET", "POST"])
def product_update(product_id):
    '''Update product. ONLY FOR ADMIN'''

    if not g.user.username in ADMIN_ID:             # only admin can delete products.
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = ProductEditForm()
    product = Product.query.get_or_404(product_id)
    
    if form.validate_on_submit(): 
        

        name = form.name.data if form.name.data else product.name 
        category = form.category.data if form.category.data else product.category
        weight = form.weight.data if form.weight.data else product.weight
        description = form.description.data if form.description.data else product.description
        price = form.price.data if form.price.data else product.price
        quantity = form.quantity.data if form.quantity.data else product.quantity
        image_url = form.image_url.data if form.image_url.data else product.image_url

        product.edit (product_id, name, category, weight, description, price, quantity, image_url)

        if product:
            db.session.add(product)
            db.session.commit()
            flash("Product has been updated.", "success")
            return redirect(f'/products/{product.id}')
        else: 
            flash("Access unauthorized.", "danger")
            return redirect ('/')

    return render_template('products/edit.html', form=form, product = product)


@app.route('/products/<int:product_id>/delete', methods = ['POST'])
def product_delete(product_id):
    '''Delete a product. ONLY FOR ADMIN'''

    if not g.user.username in ADMIN_ID:             # only admin can delete products.
        flash("Access unauthorized.", "danger")
        return redirect("/")

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    return redirect('/')



####### CATEGORIES

@app.route('/categories', methods = ['GET'])
def categories_show():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
        
    products = Product.query.all()

    categories = []
    
    for p in products:
        categories.append(p.category)
    
    categories = list(set(categories))
    
    return render_template('products/categories.html', categories = categories)

@app.route('/categories/<category>', methods = ['GET'])
def categories_filter(category):

    if g.user:
        if g.user.location:
            products = (Product
                        .query
                        .order_by(Product.name)
                        .filter(Product.category == category)
                        .all())
            
            currency = get_currency(g.user.location)

            return render_template('home.html', 
                                   currency = currency, 
                                   products=products, 
                                   ADMIN_ID = ADMIN_ID)
    else:
        return render_template('home-anon.html')



####### CART 

@app.route('/cart', methods=['GET', 'POST'])
def cart_view():
    ''' This logic assumes that user will not be able to make 
        changes to the cart (delete items or change quantites).
        In this version the edit of cart is not available.
        To edit a cart user will need to buy Pro version for $0.99.
        If BMW can sell heated seat subs why can't we XD. 
        JK. It will be added in v1.1 
        
        It also stores the total in DB in user's currency at rate when
        of purchase time. But DB does not have the currency field.
        This will be also address in the v1.1 ''' 

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user
    currency = get_currency(user.location)
    cart = session[CART]
    products = []
    total = 0

    for c in cart:
        products.append(
            [Product.query.get_or_404(c.get('product_id')), c.get('quantity')]
        )
    
    for p in products:                                              # checking quantity placed with products.quantity in DB
        if p[0].quantity == 0:
            flash(f"Sorry, it looks like {p[0].name} is Sold Out and was removed from your cart", 'danger')
            products.remove(p)
            session[CART].pop(p[0].id)

        elif p[0].quantity < p[1]:
            flash(f"{p[0].name} quantity exceeded availabiliy. Changed to maximum avaliable.", 'danger')
            p[1] = p[0].quantity


    for p in products:
        total += (p[0].price * p[1])
    total = round(total * currency.get('rate'), 2)              # change to currency rate and roundup to 2 decimals


    form = PurchaseForm()
    if form.validate_on_submit():
        try:
    
            Order.add(user.id, total, products)
            session[CART] = []

            flash("Your order has been placed!", 'success')
            return redirect(f"/users/{user.id}/orders")

        except IntegrityError:
                db.session.rollback()
                flash("Was not able to place an order", 'danger')
                return redirect("/cart")

    return render_template('/users/cart.html', 
                           products = products, 
                           currency = currency, 
                           form = form,
                           total = total)


@app.route('/cart/delete/<int:product_id>')
def cart_delete(product_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    products = []

    for c in session[CART]:
        products.append(
            [Product.query.get_or_404(c.get('product_id')), c.get('quantity')]
        )
    
    for p in products:                                              # checking quantity placed with products.quantity in DB
        if p[0].id == product_id:
            index = products.index(p)
            session[CART].pop(index)

    flash('Product was removed from cart T_T', 'warning')
    return redirect('/cart')

@app.after_request
def add_header(req):
    '''Add non-caching headers on every request.'''

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
