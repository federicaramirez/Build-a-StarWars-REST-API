"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os, json
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Favorite

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
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


#Endpoint obtiene todos los usuarios
@app.route('/user', methods=['GET'])
def get_user_all():

    all_users = User.query.all()

    print (all_users)

    results = list(map(lambda item: item.serialize(), all_users))

    return jsonify(results), 200


#Endpoint obtiene usuario por id
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):

    usuario = User.query.filter_by(id = user_id).first() #En este caso no necesita mapear, muestra uno solo.
    print(usuario)

    return jsonify(usuario.serialize()) , 200


#Crear usuarios 
@app.route('/user', methods=['POST'])
def create_user():
    body = json.loads(request.data)
    print(body)
    query_user = User.query.filter_by(email=body["email"]).first()

    favorite_user = Favorite.query.first()
    print(query_user)

#Excluir usuario ya ingresado discirminado por email
    if query_user is None:
        new_user = User(email=body["email"], password=body["password"], name=body["name"], is_active=bool(body["is_active"]))
        db.session.add(new_user)
        print()
        db.session.commit()
        new_table_favorite = Favorite(lista_favorite="")
        db.session.add(new_table_favorite)
        db.session.commit()

        #mensaje que vuelve al front
        response_body = {
            "msg": "created new user"
        }
        return jsonify(response_body), 200

    return jsonify("user exist"), 404



#Ruta para planeta
@app.route('/planet', methods=['GET'])
def get_planet_all():

    all_planet = Planets.query.all()

    print (all_planet)

    results = list(map(lambda item: item.serialize(), all_planet))

    return jsonify(results), 200

#Ruta para plenta individual

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):

    print(planet_id)
    
    planet = Planets.query.filter_by(id = planet_id).first() #En este caso no necesita mapear, muestra uno solo.
    print(planet)
    return jsonify(planet.serialize()) , 200


#Leer lista de favs, según el usuario
@app.route('/user/<int:user_id>/favorite', methods=['PUT'])
def get_favorites(user_id):
    #obtener su lista segun id

    body = json.loads(request.data)
    favorite_user = Favorite.query.filter_by(id = user_id).first()

    if favorite_user is None and body is None:       
        return jsonify({"msg": "There is no list for this user"}) , 404
    favorite_user.lista_favorite = dict(favorite_user.serialize())["lista_favorite"]+","+body["favorite"]
    db.session.commit()
    return jsonify({"msg": "the favorite has beend added exit"}), 200











# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


