from my_app import db
from flask_wtf import FlaskForm
from decimal import Decimal
from wtforms import StringField, DecimalField, SelectField, TextField
from wtforms.validators import InputRequired, NumberRange, ValidationError

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

class CategoryField(SelectField):
    def iter_choices(self):
        categories = [(c.id, c.name) for c in Category.query.all()]
        for value, label in categories:
            yield (value, label, self.coerce(value) == self.data)
    
    def pre_validate(self, form):
        for v, _ in [(c.id, c.name) for c in Category.query.all()]:
            if self.data == v:
                break
            else:
                raise ValueError(self.gettext('Not a valid choice'))

class NameForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
 
class ProductForm(NameForm):
    price = DecimalField('Price', validators=[
        InputRequired(), NumberRange(min=Decimal('0.0'))
    ])
    category = CategoryField('Category', validators=[InputRequired()], coerce=int)

def check_duplicate_category(case_sensitive=True):
    def _check_duplicate(form, field):
        if case_sensitive:
            res = Category.query.filter(
                Category.name.like('%' + field.data + '%')
            ).first()
        else:
            res = Category.query.filter(
                Category.name.like('%' + field.data + '%')
            ).first()
        if res:
            raise ValidationError('Category named {field.data} already exists')
    return _check_duplicate


class CategoryForm(NameForm):
    name = TextField('Name', validators=[InputRequired(), check_duplicate_category()])

