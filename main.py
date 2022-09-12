import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from constants import OFFERS_FILE_PATCH, ORDERS_FILE_PATCH, USERS_FILE_PATCH
from utils import load_file

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, db.CheckConstraint("age > 18"))
    email = db.Column(db.String(100), unique=True)
    role = db.Column(db.String(100))
    phone = db.Column(db.String(12), unique=True)

    orders = relationship("Order")
    offers = relationship("Offer")


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(300))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("offer.executor_id"))

    user = relationship("User")
    # offer = relationship("Offer")


class Offer(db.Model):
    __tablename__ = "offer"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    user = relationship("User")
#     order = relationship("Order")

db.drop_all()
db.create_all()

user_1 = User(id=1, first_name="Hudson", last_name="Pauloh", age=31, email="elliot16@mymail.com", role="customer",
              phone="6197021684")
# list_users = []
# for i in load_file(USERS_FILE_PATCH):
#     list_users.append(
#         User(id=i['id'], first_name=i['first_name'], last_name=i['last_name'], age=i['age'], email=i['email'],
#              role=i['role'], phone=i['phone']))
#     print(i)
#     users_list = User()
# print(users_list)

# with db.session.begin():
#     db.session.add(load_file(ORDERS_FILE_PATCH))
#     db.session.add(load_file(OFFERS_FILE_PATCH))
#     db.session.add(load_file(USERS_FILE_PATCH))

db.session.commit()


@app.route('/users')
def users_page():
    user_list = User.query.all()
    print(user_list)
    user_response = []
    for user in user_list:
        user_response.append({
            "id": user.id,
            "name": user.name,
            "age": user.age,
        })
    return json.dumps(user_response)


if __name__ == '__main__':
    app.run(debug=True)
