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
from models import db, User, Planet, People, Favorites
#from models import Person


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


# PEOPLE HERE...

@app.route("/people", methods=['GET'])
def handle_people():
    people = People.query.all()
    return jsonify([pe.serialize() for pe in people]), 200

@app.route("/people/<int:id_recieved>", methods=['GET'])
def handle_people_specific(id_recieved):
    person = People.query.filter_by(id = int(id_recieved))
    return jsonify([per.serialize() for per in person]), 200


# PLANETS HERE...

@app.route("/planets", methods=['GET'])
def handle_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200

@app.route("/planets/<int:id_recieved>", methods=['GET'])
def handle_planet_specific(id_recieved):
    planet = Planet.query.filter_by(id = int(id_recieved))
    return jsonify([per.serialize() for per in planet]), 200


# USERS HERE...

@app.route("/users", methods=['GET'])
def handle_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


# FAVORITES HERE...

@app.route("/users/favorites", methods=['GET'])
def handle_user_faves():
    faves = Favorites.query.all()
    return jsonify([f.serialize() for f in faves]), 200

@app.route("/favorite/people/<int:id_recieved>", methods=['POST'])
def add_fave_person(id_recieved):
    request_body = request.get_json()
    user = User.query.filter_by(is_active=True).first() #sets user to active user to be saved into favorite
    new_fave = Favorites(type="people", name=request_body["name"], fave_id=id_recieved, url=request_body["url"], user_id=user.id)
    db.session.add(new_fave)
    db.session.commit()
    return f"Added favorite with id: {id_recieved}"

# EXAMPLE JSON FOR ABOVE:
# {
#     "name": "TestName",
#     "url": "TestURL"
# }

@app.route("/favorite/planet/<int:id_recieved>", methods=['POST'])
def add_fave_planet(id_recieved):
    request_body = request.get_json()
    user = User.query.filter_by(is_active=True).first() #sets user to active user to be saved into favorite
    new_fave = Favorites(type="planet", name=request_body["name"], fave_id=id_recieved, url=request_body["url"], user_id=user.id)
    db.session.add(new_fave)
    db.session.commit()
    return f"Added favorite with id: {id_recieved}"


# DELETE


@app.route("/favorite/people/<int:id_recieved>", methods=['DELETE'])
def del_fave_person(id_recieved):
    to_delete = Favorites.query.filter_by(type="people", fave_id=id_recieved).first()
    print(to_delete)
    if to_delete:
        db.session.delete(to_delete)
        db.session.commit()
        return f"Deleted favorite person with id: {id_recieved}"
    else:
        return f"Item doesnt exist to delete!"
    
@app.route("/favorite/planet/<int:id_recieved>", methods=['DELETE'])
def del_fave_planet(id_recieved):
    to_delete = Favorites.query.filter_by(type="planet", fave_id=id_recieved).first()
    if to_delete:
        db.session.delete(to_delete)
        db.session.commit()
        return f"Deleted favorite planet with id: {id_recieved}"  
    else:
        return f"Item doesnt exist to delete!"


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
