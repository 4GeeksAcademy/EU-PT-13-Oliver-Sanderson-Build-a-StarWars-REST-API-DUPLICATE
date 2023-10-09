"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet
#from models import Person


characters = {1:{"name": "Luke"}, 2:{"name": "Yoda"}}
planets = {1:{"name": "Earth"}, 2:{"name": "Mars"}}
users = {1:{"username": "Bitter", "email": "123@email.com", "favorites": []}, 2: {"username": "Bitter", "email": "123@email.com", "favorites": []}}



app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# @app.route('/user', methods=['GET'])
# def handle_hello():

#     response_body = {
#         "msg": "Hello, this is your GET /user response "
#     }

#     return jsonify(response_body), 200






@app.route("/people", methods=['GET'])
def handle_people():
    return jsonify(characters)

@app.route("/people/<int:id>", methods=['GET'])
def handle_people_specific(id):
    return jsonify(characters[id])

@app.route("/planets", methods=['GET'])
def handle_planets():
    # return jsonify(planets)
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200

@app.route("/planets/<int:id>", methods=['GET'])
def handle_planet_specific(id):
    return jsonify(planets[id])

@app.route("/users", methods=['GET'])
def handle_users():
    # return jsonify(users)
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

@app.route("/users/favorites", methods=['GET'])
def handle_user_faves():
    return jsonify(users[1]["favorites"])

@app.route("/favorite/people/<int:id>", methods=['POST'])
def add_fave_person(id):
    users[1]["favorites"].append({"people":id})
    return f"Added favorite with id: {id}"

@app.route("/favorite/planet/<int:id>", methods=['POST'])
def add_fave_planet(id):
    users[1]["favorites"].append({"planet":id})
    return f"Added favorite with id: {id}"

@app.route("/favorite/people/<int:id>", methods=['DELETE'])
def del_fave_person(id):
    if {"people":id} in users[1]["favorites"]:
        users[1]["favorites"].remove({"people":id})
        return f"Deleted favorite with id: {id}"
    else:
        return f"Item doesnt exist to delete!"
    
@app.route("/favorite/planet/<int:id>", methods=['DELETE'])
def del_fave_planet(id):
    if {"planet":id} in users[1]["favorites"]:
        users[1]["favorites"].remove({"planet":id})
        return f"Deleted favorite with id: {id}"
    else:
        return f"Item doesnt exist to delete!"







# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
