'''Change login.html span attribute
data-approvalprompt to not force in production!
'''

from flask import Flask, render_template
from flask import request, redirect, url_for, flash, abort
from flask import jsonify
from flask import session as login_session
from flask import make_response
from flask.ext.seasurf import SeaSurf
app = Flask(__name__)
csrf = SeaSurf(app)

from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests

G_CLIENT_ID = json.loads(
    open('g_client_secrets.json', 'r').read())['web']['client_id']
G_APPLICATION_NAME = "My Catalog App"
F_APPLICATION_ID = json.loads(
    open('fb_client_secrets.json', 'r').read())['web']['app_id']
F_APPLICATION_NAME = "My Catalog App"

db = 'catalog'
psql_user = 'vagrant'
psql_pass = 'vagrant'
conn_str = 'postgresql+psycopg2://{u}:{p}@localhost/catalogwithusers'.format(
    u=psql_user, p=psql_pass)

engine = create_engine(conn_str)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def showMain():
    return render_template('main.html', user_logged_in=isUserLogedIn(login_session))


@csrf.exempt
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, user_logged_in=isUserLogedIn(login_session))


@csrf.exempt
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data

    # Exchange client token for long-lived server-side token with GET /oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # Strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print "url sent for API access: %s" % url
    print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # See if user exists
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    
    login_session['user_id'] = user_id

    # Generate output
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print login_session
    print "done!"
    return output


@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('g_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != G_CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # See if user exists
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    
    login_session['user_id'] = user_id

    # Generate output
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/disconnect')
def disconnect():
    print "abc"
    print login_session
    access_token = login_session['access_token']
    print login_session
    print "Access token: %s" % access_token
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if 'provider' in login_session:
        print login_session
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
    else:
        flash("You were not logged in to begin with!")
    return redirect(url_for('showCatalog'))

# JSON APIs to view Catalog Information
@app.route('/catalog/i<int:item_id>/JSON')
def itemJSON(item_id):
    '''Returns JSON of one item'''
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)

@app.route('/catalog/c<int:category_id>/JSON')
def itemsJSON(category_id):
    '''Returns JSON of all items under one category'''
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/catalog/JSON')
def categoryJSON():
    '''Returns JSON of all categories'''
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])

# Show catalog
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).all()
    # only show last 10 items
    items = session.query(Item).order_by(desc('id')).limit(10)
    return render_template('catalog.html', categories=categories, items=items, user_logged_in=isUserLogedIn(login_session))

# Show all items in a category
@app.route('/catalog/c<int:category_id>/')
def showItems(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    return render_template('category.html', categories=categories,
        category=category, items=items, user_logged_in=isUserLogedIn(login_session))

# Show an item information
@app.route('/catalog/i<int:item_id>/')
def showItem(item_id):
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id = item_id).one()
    creator = getUserInfo(item.user_id)
    user_is_creator = False
    if 'user_id' in login_session:
        if creator.id == login_session['user_id']:
            user_is_creator = True
    return render_template('item.html', categories=categories, item=item, user_logged_in=isUserLogedIn(login_session), user_is_creator=user_is_creator)

# Create new item
@app.route('/catalog/newItem/', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    if request.method == 'POST':
        result = session.query(Category.id).all()
        category_ids = [r[0] for r in result]
        newItem = Item(name=request.form['name'],
            description=request.form['desc'],
            image=request.form['img'],
            category_id=request.form['cat'],
            user_id=login_session['user_id']
            )
        session.add(newItem)
        session.commit()
        flash("New item created!")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('new_item.html', user_logged_in=isUserLogedIn(login_session),
            categories=categories)

# Edit an item
@app.route('/catalog/i<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id = item_id).one()
    creator = getUserInfo(item.user_id)
    if 'user_id' in login_session:
        if creator.id != login_session['user_id']:
            flash("You do not have permission to edit this item!")
            return redirect(url_for('showItem', item_id=item.id))
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
        return render_template('edit_item.html', item=item, user_logged_in=isUserLogedIn(login_session),
            categories=categories)

# Delete an item
@app.route('/catalog/i<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id = item_id).one()
    creator = getUserInfo(item.user_id)
    if 'user_id' in login_session:
        if creator.id != login_session['user_id']:
            flash("You do not have permission to delete this item!")
            return redirect(url_for('showItem', item_id=item.id))
            # OR THIS:
            #return "<script>function myFunction() {alert('You are not authorized to delete this item!');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item {} deleted!".format(item.name))
        return redirect(url_for('showCatalog'))
    else:
        return render_template('delete_item.html', item=item, user_logged_in=isUserLogedIn(login_session))

# HELPER FUNCTIONS
def isUserLogedIn(login_session):
    if 'username' in login_session:
        return True
    else:
        return False

def getUserId(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

def getUserInfo(user_id):
    print user_id
    user = session.query(User).filter_by(id=user_id).one()
    return user

def createUser(login_session):
    newUser = User(name = login_session['username'],
        email = login_session['email'],
        picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

if __name__ == '__main__':
    # set to False on production version
    app.debug = False
    app.secret_key = 'super_secret_key'
    app.run(host = '0.0.0.0', port = 8000)
