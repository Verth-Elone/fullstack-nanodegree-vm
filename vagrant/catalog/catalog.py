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
@app.route('/catalog')
def showCatalog():
	categories = session.query(Category).all()
	items = session.query(Item).all()
	return render_template('index.html', categories=categories, items=items)

@app.route('/catalog/<int:category_id>')
def showCategory(category_id):
	return "page to create show category items"

@app.route('/catalog/<int:category_id>/new', methods=['GET', 'POST'])
def newCategory(category_id):
	return "page to crate a new category"

@app.route('/catalog/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
	return "page to edit a category"

@app.route('/catalog/<int:category_id>/<int:item_id>')
def showItem(category_id, item_id):
	return "page to show an item"

@app.route('/catalog/<int:category_id>/<int:item_id>/new', methods=['GET', 'POST'])
def newItem(category_id, item_id):
	return "page to create a new item"

@app.route('/catalog/<int:category_id>/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(category_id, item_id):
	return "page to edit an item"


if __name__ == '__main__':
	# set to False on production version
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)