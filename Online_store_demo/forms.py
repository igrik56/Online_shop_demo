from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, FloatField
from wtforms.validators import DataRequired, email, Length


class ProductAddForm(FlaskForm):
    """Form for adding products."""

    name = StringField('Name', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    weight = IntegerField('Weight in grams', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price in USD', validators=[DataRequired()])
    quantity = IntegerField('Quantity:', validators=[DataRequired()])
    image_url = StringField('Image URL:', validators=[DataRequired()])

class ProductEditForm(FlaskForm):
    ''' Form t update product '''

    name = StringField('(Optional) Name')
    category = StringField('(Optional) Category')
    weight = IntegerField('(Optional) Weight in grams')
    description = TextAreaField('(Optional) Description')
    price = FloatField('(Optional) Price in USD')
    quantity = IntegerField('(Optional) Quantity:')
    image_url = StringField('(Optional) Image URL')

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), email(message = 'Enter valid email')])
    location = StringField('Location', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditFrom(FlaskForm):
    '''Form where user can edit its info'''
    
    image_url = StringField('(Optional) Image URL')
    email = StringField('(Optional) E-mail')
    location = StringField('(Optional) Location')
    address = StringField('(Optional) Address')
    password = PasswordField('Password', validators=[Length(min=6)])
    
class AddToCartForm(FlaskForm):
    '''Form for adding product to the cart'''
    quantity =  IntegerField('Quantity:', validators=[DataRequired()])

class PurchaseForm(FlaskForm):
    '''Form to submit an order'''    