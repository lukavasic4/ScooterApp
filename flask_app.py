from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir,'db.sqlite')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Owner(db.Model):
    id_owner = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.DateTime)

    def __init__(self, first_name, last_name, date_of_birth):
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth

class OwnerSchema(ma.Schema):
    class Meta:
        fields = ('id_owner','first_name','last_name','date_of_birth')

owner_schema = OwnerSchema()
owners_schema = OwnerSchema(many=True)

class Scooter(db.Model):
    id_scooter = db.Column(db.Integer, primary_key=True, autoincrement=True)
    make = db.Column(db.String(20))
    model = db.Column(db.String(20))
    year_of_production = db.Column(db.Integer)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)

    def __init__(self, make, model, year_of_production, price, quantity):
        self.make = make
        self.model = model
        self.year_of_production = year_of_production
        self.price = price
        self.quantity = quantity


class ScooterSchema(ma.Schema):
    class Meta:
        fields =('id_scooter', 'make', 'model', 'year_of_production', 'price', 'quantity')
scooter_schema = ScooterSchema()
scooters_schema = ScooterSchema(many=True)

class Buying(db.Model):
    id_buying = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_owner = db.Column(db.Integer, db.ForeignKey('owner.id_owner'), nullable=False)
    id_scooter = db.Column(db.Integer, db.ForeignKey('scooter.id_scooter'), nullable=False)

    def __init__(self, id_scooter, id_owner):
        self.id_scooter = id_scooter
        self.id_owner = id_owner

class BuyingSchema(ma.Schema):
    class Meta:
        fields = ('id_scooter', 'id_owner')
buying_schema = BuyingSchema()
buyings_schema = BuyingSchema(many=True)

class Service(db.Model):
    id_service = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime)
    id_scooter = db.Column(db.Integer, db.ForeignKey('scooter.id_scooter'), nullable=False)

    def __init__(self, price, description, date, id_scooter):
        self.price = price
        self.description = description
        self.date = date
        self.id_scooter = id_scooter

class ServiceSchema(ma.Schema):
    class Meta:
        fields = ('price', 'description', 'date', 'id_scooter')
service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)

@app.route('/owner', methods=['POST'])
def add_owner():
   first_name = request.json['first_name']
   last_name = request.json['last_name']
   date = request.json['year_of_birth']
   year_of_birth = datetime.strptime(date,'%Y-%m-%d')

   new_owner = Owner(first_name, last_name, year_of_birth)
   db.session.add(new_owner)
   db.session.commit()
   return owner_schema.jsonify(new_owner), 201

@app.route('/scooter', methods=['POST'])
def add_scooter():
    make = request.json['make']
    model = request.json['model']
    year_of_production = request.json['year_of_production']
    price = request.json['price']
    quantity = request.json['quantity']

    new_scooter = Scooter(make, model, year_of_production, price, quantity)
    db.session.add(new_scooter)
    db.session.commit()
    return owner_schema.jsonify(new_scooter), 201

# Buy a Scooter
@app.route('/buying', methods=['POST'])
def buying_scooter():
    id_scooter = request.json['id_scooter']
    id_owner = request.json['id_owner']
    scooter = Scooter.query.get(id_scooter)
    scooter.quantity = scooter.quantity-1

    new_buying = Buying(id_scooter, id_owner)
    db.session.add(new_buying)
    db.session.commit()
    return buying_schema.jsonify(new_buying), 201

# List all owned Scooters by an owner
@app.route('/ownerScooters/<id>', methods=['GET'])
def selled_scooters(id):
    buying = db.session.query(Scooter).join(Buying, Scooter.id_scooter == Buying.id_scooter).filter(Buying.id_owner == id).all()
    result = scooters_schema.dump(buying)
    return jsonify(result)

@app.route('/buying', methods=['GET'])
def all_buying():
    buy = Buying.query.all()
    result = buyings_schema.dump(buy)
    return jsonify(result)

# Service/repair a Scooter
@app.route('/service', methods=['POST'])
def service_scooter():
    price = request.json['price']
    description = request.json['description']
    date = datetime.strptime(request.json['date'], '%Y-%m-%d')
    id_scooter = request.json['scooter']

    new_service = Service(price, description, date, id_scooter)
    db.session.add(new_service)
    db.session.commit()
    return service_schema.jsonify(new_service), 201

@app.route('/owner', methods=['GET'])
def get_all_owner():
    all_owner = Owner.query.all()
    result = owners_schema.dump(all_owner)
    return jsonify(result)

# List a service list of one of his specific Scooter
@app.route('/service/<id>', methods=['GET'])
def get_one_or_more_service(id):
    service = Service.query.filter(Service.id_scooter == id)
    result = services_schema.dump(service)
    return jsonify(result)

# List all Scooters available to buy
@app.route('/scooter', methods=['GET'])
def get_all_scooter():
    all_scooter = Scooter.query.filter(Scooter.quantity > 0)
    result = scooters_schema.dump(all_scooter)
    return jsonify(result)
if __name__ == '__main__':
    app.run(debug=True)