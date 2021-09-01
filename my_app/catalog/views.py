from flask import request, jsonify, Blueprint, render_template, flash, redirect
from flask.helpers import url_for
from my_app import db, app, redis
from my_app.catalog.models import Product, Category
from sqlalchemy.orm.util import join
from functools import wraps

catalog = Blueprint('catalog', __name__)



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
    if request.method == 'POST':
        name = request.form.get('name') 
        price = request.form.get('price') 
        categ_name = request.form.get('category') 
        category = Category.query.filter_by(name=categ_name).first() 
        if not category: 
            category = Category(categ_name) 
        product = Product(name, price, category) 
        db.session.add(product) 
        db.session.commit() 
        flash(f'The product {name} has been created', 'success')
        return redirect(url_for('catalog.product', id=product.id)) 
    return render_template('product-create.html')

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
    


@catalog.route('/category-create', methods=['POST',]) 
def create_category(): 
    name = request.form.get('name') 
    category = Category(name) 
    db.session.add(category) 
    db.session.commit() 
    return render_template('category.html', category=category)  

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