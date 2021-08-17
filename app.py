import hmac
import sqlite3
import datetime
from flask_cors import CORS


from flask import Flask, request, jsonify, redirect
from flask_jwt import JWT, jwt_required, current_identity


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('online_shopping.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


# ---Creating User Table---
def init_user_table():
    conn = sqlite3.connect('online_shopping.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


# ---CREATING PRODUCTS TABLE---
def init_products_table():
    with sqlite3.connect('online_shopping.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS product (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "type TEXT NOT NULL,"
                     "images TEXT NOT NULL,"
                     "date_created TEXT NOT NULL)")
    print("products table created successfully.")


init_user_table()
init_products_table()

users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
CORS(app)

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
#@jwt_required()
def protected():
    return '%s' % current_identity


# ---Image Hosting---
@app.route('/image-hosting/')
def image_hosting():
    with sqlite3.connect("online_shopping.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT images FROM product WHERE id='2'")
        image = cursor.fetchone()
        for i in image:
            image1 = i
    return redirect(image1)


# ---User Registration---
@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("online_shopping.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password) VALUES(?, ?, ?, ?)", (first_name, last_name, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


# ---Creating Products---
@app.route('/create-product/', methods=["POST"])
#@jwt_required()
def create_product():
    response = {}

    if request.method == "POST":
        name = request.form['name']
        price = request.form['price']
        type_ = request.form['type']
        description = request.form['description']
        images = request.form['images']
        date_created = datetime.datetime.now()

        with sqlite3.connect('online_shopping.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO product ("
                           "name,"
                           "price,"
                           "description,"
                           "type,"
                           "images,"
                           "date_created) VALUES(?, ?, ?, ?, ?, ?)", (name, price, description, type_, images, date_created))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Product added succesfully"
        return response


# ---Get Products---
@app.route('/get-product/', methods=["GET"])
def get_product():
    response = {}
    with sqlite3.connect("online_shopping.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


# ---Sorting Products by Date---
@app.route('/sort-product/', methods=["GET"])
def sort_product():
    response = {}
    with sqlite3.connect("online_shopping.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product ORDER BY date_created")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


# ---Filtering Products by Type---
@app.route('/filter-product/<type>/', methods=["GET"])
def filter_product(type):
    response = {}
    with sqlite3.connect("online_shopping.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product WHERE type LIKE '%" + type + "%'")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return jsonify(response)


# ---Delete Products---
@app.route("/delete-product/<int:product_id>")
#@jwt_required()
def delete_post(product_id):
    response = {}
    with sqlite3.connect("online_shopping.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "product deleted successfully."
    return response


# ---Edit Products---
@app.route('/edit-product/<int:product_id>/', methods=["PUT"])
#@jwt_required()
def edit_post(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('online_shopping.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("name") is not None:
                put_data["name"] = incoming_data.get("name")
                with sqlite3.connect('online_shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET name =? WHERE id=?", (put_data["name"], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('online_shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET price =? WHERE id=?", (put_data["price"], product_id))
                    conn.commit()

                    response["price"] = "price updated successful"
                    response["status_code"] = 200

            if incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")
                with sqlite3.connect('online_shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET description =? WHERE id=?", (put_data["description"], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            if incoming_data.get("images") is not None:
                put_data["images"] = incoming_data.get("images")
                with sqlite3.connect('online_shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET images =? WHERE id=?",
                                   (put_data["images"], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200
    return response


# ---Get Product by ID---
@app.route('/get-product/<int:product_id>/', methods=["GET"])
def get_post(product_id):
    response = {}

    with sqlite3.connect("online_shopping.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product WHERE id=" + str(product_id))

        response["status_code"] = 200
        response["description"] = "product retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


if __name__ == "__main__":
    app.debug = True
    app.run()

