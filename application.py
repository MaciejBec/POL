import json
import secrets
from collections import defaultdict
from functools import wraps

import requests
from flask import Flask, render_template, request, make_response, session, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from werkzeug.utils import redirect


from forms import Itemform

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://udacity:udacity@localhost/udacity'
db = SQLAlchemy(app)

# Get google client_id for this app from json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('user_google_id'):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapper


@app.route('/logout', methods=["POST"])
def logout():
    session.pop('access_token', None)
    session.pop('user_google_id', None)
    session.pop('username', None)
    session.pop('picture', None)
    session.pop('email', None)
    session.pop('username', None)
    return "Success"


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        state = secrets.token_hex(32)
        session['state'] = state
        return render_template('login.html', STATE=state)
    # try:
    # Check the state variable for extra security
    print("step 0")
    if session['state'] != request.args.get('state'):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print("step 1")
        return response

    # Retrieve the token sent by the client
    token = request.data
    print("step 2")

    # Request an access tocken from the google api
    idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)
    print("step 3")
    url = (
            'https://oauth2.googleapis.com/tokeninfo?id_token=%s'
            % token.decode(encoding='utf-8'))
    # h = httplib2.Http()
    result = requests.get(url).json()
    print("step 4")
    print(result['aud'])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    print("step 5")
    # Verify that the access token is used for the intended user.
    user_google_id = idinfo['sub']
    if result['sub'] != user_google_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print(result['sub'])
    # Verify that the access token is valid for this app.
    if result['aud'] != CLIENT_ID:
        print("step 5.5")
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    print("step 6")
    # Check if the user is already logged in
    stored_access_token = session.get('access_token')
    stored_user_google_id = session.get('user_google_id')
    if stored_access_token is not None and user_google_id == stored_user_google_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    print("step 7")
    # Store the access token in the session for later use.
    session['access_token'] = idinfo
    session['user_google_id'] = user_google_id
    # Get user info
    session['username'] = idinfo['name']
    session['picture'] = idinfo['picture']
    session['email'] = idinfo['email']

    return "Successfull"

    # except ValueError:
    #     # Invalid token
    #     print("invalid token")


@app.route("/")
def home():
    from models import Item, Category

    items = Item.query.limit(10)
    categories = Category.query.all()
    return render_template("home.html", categories=categories, items=items)


@app.route("/catalog.json")
def catalog_json():
    from models import Category

    data = defaultdict(list)
    categories = Category.query.all()
    for category in categories:
        data['category'].append(category.serialize)
    return jsonify(data)


@app.route("/category/<string:category>")
def category_view(category):
    from models import Category

    category = Category.query.filter(Category.name == category).first()
    items = category.item
    return render_template("category.html", category=category, items=items)


@app.route("/add-item", methods=["GET", "POST"])
@login_required
def add_item():
    from models import Item, Category

    form = Itemform()
    form.cat_id.choices = [(cat.id, cat.name) for cat in Category.query.all()]
    if form.validate_on_submit():
        item_new = Item(cat_id=form.data.get('cat_id'),
                        description=form.data.get('description'),
                        title=form.data.get('title')
                        )

        db.session.add(item_new)
        db.session.commit()

        return redirect('/')
    return render_template("add_item.html", form=form)


@app.route("/category/<string:category>/<string:title>/edit-item", methods=["GET", "POST"])
@login_required
def edit_item(category, title):
    from models import Item, Category

    cat = Category.query.filter(Category.name == category).first()
    item = Item.query.filter(Item.cat_id == cat.id, Item.title == title).first()

    form = Itemform(request.form, obj=item)
    form.cat_id.choices = [(cat.id, cat.name) for cat in Category.query.all()]
    if form.validate_on_submit():
        form.populate_obj(item)
        db.session.add(item)
        db.session.commit()

        return redirect('/category/{}'.format(category))
    return render_template("add_item.html", form=form)


@app.route("/category/<string:category>/<string:title>")
def item_view(category, title):
    from models import Item, Category

    cat = Category.query.filter(Category.name == category).first()
    item = Item.query.filter(Item.title == title, Item.cat_id == cat.id).first()
    return render_template("item.html", item=item)


@app.route("/category/<string:category>/<string:title>/delete", methods=["GET", "POST"])
@login_required
def item_del(category, title):
    from models import Item, Category

    cat = Category.query.filter(Category.name == category).first()
    item = Item.query.filter(Item.title == title, Item.cat_id == cat.id).first()
    if request.method == "POST":
        if int(request.form.get("del")):
            db.session.delete(item)
            db.session.commit()
            return redirect('/')
        else:
            return redirect('/')
    return render_template("delete.html", item=item)


@app.teardown_appcontext
def shutdown_session(expection=None):
    db.session.remove()


if __name__ == "__main__":
    # init_db()

    app.debug = True
    app.run(host="0.0.0.0", port=5000, threaded=False)
