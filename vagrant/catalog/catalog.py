from flask import Flask, render_template, request, redirect, url_for, flash, abort
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy import desc
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
    # only show last 10 items
    items = session.query(Item).order_by(desc('id')).limit(10)
    return render_template('catalog.html', categories=categories,
        items=items)

@app.route('/catalog/c<int:category_id>/')
def showItems(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    return render_template('category.html', categories=categories,
        category=category, items=items)

@app.route('/catalog/i<int:item_id>/')
def showItem(item_id):
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id = item_id).one()
    return render_template('item.html', categories=categories, item=item)

@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    if request.method == 'POST':
        result = session.query(Category.id).all()
        category_ids = [r[0] for r in result]
        if int(request.form['cat']) not in category_ids:
            flash("Creation of item failed! Not a valid category!")
        else:
            newItem = Item(name=request.form['name'],
                description=request.form['desc'],
                image=request.form['img'],
                category_id=int(request.form['cat'])
                )
            session.add(newItem)
            session.commit()
            flash("New item created!")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('new_item.html')

@app.route('/catalog/i<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(item_id):
    '''Ren
    '''
    item = session.query(Item).filter_by(id = item_id).one()
    if request.method == 'POST':
        result = session.query(Category.id).all()
        category_ids = [r[0] for r in result]
        if int(request.form['cat']) not in category_ids:
            flash("Creation of item failed! Not a valid category!")
        else:
            if request.form['name']:
                item.name = request.form['name']
            if request.form['desc']:
                item.description = request.form['desc']
            if request.form['img']:
                item.image = request.form['img']
            if request.form['cat']:
                item.category_id = int(request.form['cat'])
            session.add(item)
            session.commit()
            flash("Item edited successfully!")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('edit_item.html', item=item)

@app.route('/catalog/i<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item {} deleted!".format(item.name))
        return redirect(url_for('showCatalog'))
    else:
        return render_template('delete_item.html', item=item)


if __name__ == '__main__':
    # set to False on production version
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host = '0.0.0.0', port = 8000)
