'''Change login.html span attribute
data-approvalprompt to not force in production!
'''

from flask import Flask, render_template
from flask import request, redirect, url_for, flash, abort
from flask import session as login_session
from flask import make_response
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

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

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json',
            scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.ste2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={at}'.format(at=access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 50)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match giver user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's one."), 401)
        print "Token's client ID does not match app's one."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    poutput = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

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
