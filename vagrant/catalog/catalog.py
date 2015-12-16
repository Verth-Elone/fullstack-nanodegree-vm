from flask import Flask, render_template
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

db = 'catalog'
psql_user = 'vagrant'
psql_pass = 'vagrant'
conn_str = 'postgresql+psycopg2://{u}:{p}@localhost/catalog'.format(
    u=psql_user, p=psql_pass)

engine = create_engine(conn_str)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/index')
def showMain():
    return render_template('main.html')

@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template('catalog.html', categories=categories, items=items)

@app.route('/catalog/c<int:category_id>/')
def showCategory(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    return render_template('category.html', categories=categories,
        category=category, items=items)

@app.route('/catalog/category/new/', methods=['GET', 'POST'])
def newCategory():
    categories = session.query(Category).all()
    return render_template('category_new.html')

@app.route('/catalog/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    categories = session.query(Category).all()
    return "page to edit a category"

@app.route('/catalog/<int:category_id>/<int:item_id>/')
def showItem(category_id, item_id):
    categories = session.query(Category).all()
    return "page to show an item"

@app.route('/catalog/<int:category_id>/<int:item_id>/new/', methods=['GET', 'POST'])
def newItem(category_id, item_id):
    categories = session.query(Category).all()
    return "page to create a new item"

@app.route('/catalog/<int:category_id>/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    categories = session.query(Category).all()
    return "page to edit an item"


if __name__ == '__main__':
    # set to False on production version
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
