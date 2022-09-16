import json

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from constants import USERS_PATCH, ORDERS_PATCH, OFFERS_PATCH
from utils import get_json, convert_to_date

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, db.CheckConstraint("age > 17"))
    email = db.Column(db.String(100), unique=True)
    role = db.Column(db.String(100))
    phone = db.Column(db.String(12), unique=True)

    def users_to_dict(self):
        """Serialize implementation model Users"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "email": self.email,
            "role": self.role,
            "phone": self.phone
        }


class Order(db.Model):
    """SQLAlchemy model for orders"""
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer)
    customer = db.relationship('User', foreign_keys=[customer_id])

    def orders_to_dict(self):
        """
    Serialize implementation model Orders
    """
        return {
            "id": self.id,
            "name": self.name,
            "descriptio n": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "address": self.address,
            "price": self.price,
            "customer_id": self.customer_id,
            "executor_id": self.executor_id

        }


class Offer(db.Model):
    """SQLAlchemy model for offers"""
    __tablemname__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    order = db.relationship('Order')
    executor = db.relationship('User')

    def offers_to_dict(self):
        """
            Serialize implementation model Offer
            """
        return {
            "id": self.id,
            "order_id": self.order_id,
            "executor_id": self.executor_id,

        }


db.drop_all()
db.create_all()


#
#
def creating_user_instances():
    users_list = []
    for i in get_json(USERS_PATCH):
        users_list.append(User(
            id=i.get('id'),
            first_name=i.get('first_name'),
            last_name=i.get('last_name'),
            age=i.get('age'),
            email=i.get('email'),
            role=i.get('role'),
            phone=i.get('phone')))
    return users_list


def creating_orders_instances():
    orders_list = []
    for i in get_json(ORDERS_PATCH):
        orders_list.append(Order(
            id=i.get('id'),
            name=i.get('name'),
            description=i.get('description'),
            start_date=convert_to_date(i.get('start_date')),
            end_date=convert_to_date(i.get('end_date')),
            address=i.get('address'),
            price=i.get('price'),
            customer_id=i.get('customer_id'),
            executor_id=i.get('executor_id')))
    return orders_list


def creating_offers_instances():
    offers_list = []
    for i in get_json(OFFERS_PATCH):
        offers_list.append(Offer(
            id=i.get('id'),
            order_id=i.get('order_id'),
            executor_id=i.get('executor_id')))
    return offers_list


with db.session.begin():
    db.session.add_all(creating_orders_instances())
    db.session.add_all(creating_offers_instances())
    db.session.add_all(creating_user_instances())
db.session.commit()


#  API views
@app.route("/users", methods=['GET', 'POST'])
def get_users_page():
    if request.method == "GET":
        result = []
        users = db.session.query(User).all()
        for item in users:
            result.append(User.users_to_dict(item))
        return jsonify(result)

    elif request.method == "POST":
        insert_date = request.get_json()
        new_user = User(
            first_name=insert_date.get('first_name'),
            last_name=insert_date.get('last_name'),
            age=insert_date.get('age'),
            email=insert_date.get('email'),
            role=insert_date.get('role'),
            phone=insert_date.get('phone')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.users_to_dict()), '201'


@app.route('/users/<int:pk>', methods=['GET', 'PUT', 'DELETE'])
def get_one_user(pk):
    user = db.session.query(User).get(pk)
    if not user:
        return jsonify({"ValueError": "User not found"}), '404'
    if request.method == "GET":
        return jsonify(user.users_to_dict())
    if request.method == "PUT":
        insert_date = request.get_json()
        user.first_name = insert_date.get('first_name')
        user.last_name = insert_date.get('last_name')
        user.age = insert_date.get('age')
        user.email = insert_date.get('email')
        user.role = insert_date.get('role')
        user.phone = insert_date.get('phone')
        db.session.add(user)
        db.session.commit()
        return jsonify(user.users_to_dict()), '201'
    if request.method == "DELETE":
        db.session.delete(user)
        db.session.commit()
        return jsonify({"User": "deleted successfully"}), '204'


@app.route("/orders", methods=['POST', 'GET'])
def get_orders_page():
    if request.method == "GET":
        result = []
        all_orders = db.session.query(Order).all()
        for order in all_orders:
            result.append(order.orders_to_dict())
        return jsonify(result)
    if request.method == "POST":
        insert_date = request.get_json()
        new_order = Order(
            name=insert_date.get("name"),
            description=insert_date.get("description"),
            start_date=convert_to_date(insert_date.get("start_date")),
            end_date=convert_to_date(insert_date.get("end_date")),
            address=insert_date.get("address"),
            price=insert_date.get("price"),
            customer_id=insert_date.get("customer_id"),
            executor_id=insert_date.get("executor_id"),

        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify(new_order.orders_to_dict()), '201'


@app.route('/orders/<int:pk>', methods=['GET', 'PUT', 'DELETE'])
def get_one_order(pk):
    order = db.session.query(Order).get(pk)
    if not order:
        return jsonify({"ValueError": "Order not found"}), '404'
    if request.method == 'GET':
        return jsonify(order.orders_to_dict())
    if request.method == 'PUT':
        insert_date = request.get_json()
        order.name = insert_date.get("name")
        order.description = insert_date.get("description")
        order.start_date = convert_to_date(insert_date.get("start_date"))
        order.end_date = convert_to_date(insert_date.get("end_date"))
        order.address = insert_date.get("address")
        order.price = insert_date.get("price")
        order.customer_id = insert_date.get("customer_id")
        order.executor_id = insert_date.get("executor_id")
        db.session.add(order)
        db.session.commit()
        return jsonify(order.orders_to_dict()), '201'
    if request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return jsonify({"Order": "deleted successfully"}), '204'


@app.route('/offers', methods=['GET', 'POST'])
def get_offers_page():
    if request.method == 'GET':
        result = []
        all_offers = db.session.query(Offer).all()
        for offer in all_offers:
            result.append(offer.offers_to_dict())
        return jsonify(result)
    if request.method == 'POST':
        insert_date = request.get_json()
        new_offer = Offer(
            order_id=insert_date.get("order_id"),
            executor_id=insert_date.get("executor_id")
        )
        db.session.add(new_offer)
        db.session.commit()
        return jsonify(new_offer.offers_to_dict()), '201'


@app.route('/offers/<int:pk>', methods=['GET', 'PUT', 'DELETE'])
def get_one_offer(pk):
    offer = db.session.query(Offer).get(pk)
    if not offer:
        return jsonify({"ValueError": "Offer not found"}), '404'
    if request.method == 'GET':
        return jsonify(offer.offers_to_dict())
    if request.method == 'PUT':
        insert_date = request.get_json()
        offer.order_id = insert_date.get("order_id")
        offer.executor_id = insert_date.get("executor_id")
        db.session.add(offer)
        db.session.commit()
        return jsonify(offer.offers_to_dict()), '201'
    if request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        return jsonify({"Offer": "deleted successfully"}), '204'


if __name__ == '__main__':
    app.run()
