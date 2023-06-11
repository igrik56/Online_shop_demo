"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

    #################### USER MODEL ####################

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement = True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    location = db.Column(
        db.Text,
        nullable = False
    )

    address = db.Column(
        db.Text,
        nullable = False,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    orders = db.relationship('Order', cascade = 'all, delete', backref = 'users')


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}, {self.address}, {self.location}>"
    

    @classmethod
    def signup(cls, username, location, address, password , email):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            location = location,
            address = address,
            password=hashed_pwd,
            email=email
        )

        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    
    @classmethod
    def edit(cls, id, email, image_url, pw, location, address):

        user = cls.query.get_or_404(id)
        
        if cls.authenticate(user.username, pw):

            user.email = email
            user.image_url = image_url
            user.location = location
            user.address = address

            return user
        
        else: return False
    
    #################### PRODUCT MODEL ####################

class Product(db.Model):
    """An individual product."""

    __tablename__ = 'products'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement = True
    )

    name = db.Column(
        db.Text,
        nullable = False,
        unique = True
    )

    category = db.Column(
        db.Text,
        nullable = False,
    )

    weight = db.Column(
        db.Integer,
        nullable = False
    )

    description = db.Column(
        db.Text,
        nullable = False
    )

    price = db.Column(
        db.Float,
        nullable = False
    )

    quantity = db.Column(
        db.Integer,
        nullable = False
    )
    image_url = db.Column(
        db.Text,
        nullable = True,
    )

    in_order = db.relationship('Order', secondary = 'orders_products', backref = 'products')

    def __repr__(self):
        return f"<Product #{self.id}: {self.name}, {self.category}, {self.description}, {self.price}, {self.quantity}>"
    

    @classmethod
    def add(cls, name, category, weight, description , price, quantity, image_url):

        product = Product(name = name,
                          category = category,
                          weight = weight,
                          description = description,
                          price = price,
                          quantity = quantity,
                          image_url = image_url
                          )
        
        db.session.add(product)
        db.session.commit()
        return product
    
    @classmethod
    def edit(cls, id, name, category, weight, description , price, quantity, image_url):

        product = cls.query.get_or_404(id)

        if product:
            product.name = name
            product.category = category,
            product.weight = weight,
            product.description = description,
            product.price = price,
            product.quantity = quantity,
            product.image_url = image_url

            return product
        
        else: return False

    def displayed_price(self, rate):
        return self.price * rate


#     #################### ORDERS MODEL ####################

class Order(db.Model):
    
    __tablename__ = 'orders' 

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement = True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable = False
    )
    
    timestamp = db.Column(        
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )

    total = db.Column(
        db.Float,
        nullable = False
    )

    @classmethod
    def add(cls, user_id, total, products):
        order = Order(
            user_id = user_id,
            total = total
        )

        db.session.add(order)
        db.session.flush()

        for p in products:
            order_product = OrderProduct(
                order_id = order.id,
                product_id = p[0].id,
                quantity = p[1]
                )
            
            db.session.add(order_product)
            p[0].quantity = p[0].quantity - p[1]
            
        db.session.commit()


class OrderProduct(db.Model):
    '''Mapping Order to Product'''
    
    __tablename__ = 'orders_products'

    id = db.Column(
        db.Integer, 
        primary_key = True,
        autoincrement = True
    )

    order_id = db.Column(
        db.Integer, 
        db.ForeignKey('orders.id'),
        primary_key = True
    )

    product_id = db.Column(
        db.Integer, 
        db.ForeignKey('products.id'),
        primary_key = True
    )

    quantity = db.Column(
        db.Integer,
        nullable = False
    )
