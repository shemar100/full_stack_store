from my_app import db
from flask_wtf import FlaskForm
from decimal import Decimal
from wtforms import StringField, DecimalField, SelectField
from wtforms.validators import InputRequired, NumberRange

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(244))
    price = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('products', lazy='dynamic'))

    def __init__(self, name, price, category):
        self.name = name
        self.price = price
        self.category = category
    
    def __repr__(self):
        return 'Product<%d> ' % self.id

class Category(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        f'<Category> {self.id}'

class NameForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
 
class ProductForm(NameForm):
    price = DecimalField('Price', validators=[
        InputRequired(), NumberRange(min=Decimal('0.0'))
    ])
    category = SelectField('Category', validators=[InputRequired()], coerce=int)

class CategoryForm(NameForm):
    pass

