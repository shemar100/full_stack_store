from flask import request, jsonify, Blueprint, render_template, flash, redirect, abort
from my_app import ALLOWED_EXTENSIONS
from flask.helpers import url_for
from flask_wtf import csrf
from werkzeug.utils import secure_filename
from my_app import db, app, redis
from my_app.catalog.models import Product, Category
from sqlalchemy.orm.util import join
from my_app.catalog.models import ProductForm, CategoryForm
import os
import json
from flask.views import MethodView
#from functools import wraps

catalog = Blueprint('catalog', __name__)


def allowed_file(filename):
    return '.' in filename and \
        filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


'''
prints "Welcome to the catalog home" on the index route 
'''
@catalog.route('/home')
@catalog.route('/')
def home():
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        products = Product.query.all()
        return jsonify({
            'count' : len(products)
        })
    return render_template('home.html')

 
@catalog.route('/products')
@catalog.route('/products/<int:page>')
def products(page=1): 
    #products = Product.query.all() expensive to fetch all from we will paginate (depracted for now)
    products = Product.query.paginate(page, 10)
    # res = {} 
    # for product in products: 
    #     res[product.id] = { 
    #         'name': product.name, 
    #         'price': product.price, 
    #         'category': product.category.name
    #     } 
    # return jsonify(res) 
    return render_template('products.html', products=products)
 
@catalog.route('/product/<id>') 
def product(id): 
    product = Product.query.get_or_404(id) 
    product_key = 'product-%s' % product.id 
    redis.set(product_key, product.name) 
    redis.expire(product_key, 600) 
    return render_template('product.html', product=product)  

@catalog.route('/recent-products') 
def recent_products(): 
    keys_alive = redis.keys('product-*') 
    products = [redis.get(k).decode('utf-8') for k in keys_alive] 
    return jsonify({'visited': products})
    
@catalog.route('/product-create', methods=['POST','GET']) 
def create_product():
    form = ProductForm()

    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data 
        category = Category.query.get_or_404(
            form.category.data
        )
        image = form.image.data
        if allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        product = Product(name, price, category, filename)
         
        db.session.add(product) 
        db.session.commit() 
        flash(f'The product {name} has been created', 'success')
        return redirect(url_for('catalog.product', id=product.id))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('product-create.html', form=form)

@catalog.route('/product-search')
@catalog.route('/product-search/<int:page>')
def product_search(page=1):
    name = request.args.get('name')
    price = request.args.get('price')
    category = request.args.get('category')
    products = Product.query
    if name:
        products = products.filter(Product.name.like('%' + name + '%'))
    if price:
        products = products.filter(Product.price.like('%' + price + '%'))
    if category:
        products = products.select_from(join(Product, Category)).filter(Category.name.like('%' + category + '%'))
    return render_template('products.html', products=products.paginate(page,10))
    


@catalog.route('/category-create', methods=['POST','GET']) 
def create_category(): 
    form = CategoryForm()
    if form.validate_on_submit():
        name = request.form.get('name') 
        category = Category(name) 
        db.session.add(category) 
        db.session.commit()
        flash(f'Category {name} created successfully', 'success')
        return redirect(url_for('catalog.category', id=category.id))
    
    if form.errors:
        flash(form.errors, 'danger')
    
    return render_template('category-create.html', form=form)  

@catalog.route('/categories') 
def categories(): 
    categories = Category.query.all() 
    # res = {} 
    # for category in categories: 
    #     res[category.id] = { 
    #         'name': category.name 
    #     } 
        # for product in category.products: 
        #     res[category.id]['products'] = { 
        #         'id': product.id, 
        #         'name': product.name, 
        #         'price': product.price,
        #     }
    # return jsonify(res)
    return render_template('categories.html',categories=categories) 

@catalog.route('/category/<id>') 
def category(id): 
    category = Category.query.get_or_404(id) 
    return render_template('category.html', category=category)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

class ProductView(MethodView):
    def get(self, id=None, page=1):
        if not id:
            products = Product.query.paginate(page, 10).items()
            res = {}
            for product in products:
                res[product.id] = {
                    'name': product.name,
                    'price': product.price,
                    'category': product.category.name
                }
        else:
            product = Product.query.filter_by(id=id).first()
            if not product:
                abort(404)
            res = json.dumps({
                'name': product.name,
                'price': product.price,
                'category': product.category.name
            })
        return res
    
    def post(self):
        # Create a new product
        # Return the ID/Object of newly created product
        return
    
    def put(self, id):
        # Update the product corresponding provided id
        # Return the the json corresponding updated product
        return

    def delete(self, id):
        # Delete the product corresponding provided id.
        # Return success or errors message
        return
    
product_view = ProductView.as_view('product_view')
app.add_url_rule('/products/', view_func=product_view, methods=['GET', 'POST'])
app.add_url_rule('/products/<int:id>', view_func=product_view, methods=['GET','PUT', 'DELETE'])

