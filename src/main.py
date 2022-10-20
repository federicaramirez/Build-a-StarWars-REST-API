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
#import jwt
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

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
        new_user = User(email=body["email"], password=body["password"], name=body["name"], is_active=bool(body["is_active"]), id=len(User.query.all())+1)
        db.session.add(new_user)
        print()
        db.session.commit()
        new_table_favorite = Favorite(lista_favorite="", id=len(Favorite.query.all())+1)
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
    favorites_user = Favorite.query.filter_by(id = user_id).first()
    print(Favorite.query.filter_by(id = user_id).first())
    # #borrar si no esta en la lista
    if body["favorite"] in dict(favorites_user.serialize())["lista_favorite"]:
    #     #conseguimos el star de la base de datos 
        aux = dict(favorites_user.serialize())["lista_favorite"]
    #     #eliminamos el valor usando de referencia de separacion para crear un array
        aux = aux.split("$$"+body["favorite"])
    #     #convertir el array si el valor de vuelta en str, para mandarlo a la base de datos
        aux = ''.join(aux)
        favorites_user.lista_favorite = aux
        db.session.commit()
        return jsonify({"msg":"the favorite has been delated successfully"}), 200
    # #mandar un error si no existe la lista o contenido en el body 
    elif favorites_user is None and body is None:
        return jsonify({"msg": "There is no list for this user"}) , 404
    # #agregar si existe la lista pero no esta el contenido
    favorites_user. lista_favorite = dict(favorites_user.serialize())["lista_favorite"]+"$$"+body["favorite"]
    db.session.commit()
    return jsonify({"msg": "the favorite has beend added exit"}), 200


# Cree una ruta para autenticar a sus usuarios y devolver JWT. los
# La función create_access_token() se usa para generar realmente el JWT.
@app.route("/login", methods=["POST"])
def login():

    email = request.json.get("email", None) #Formas de recibir el front
    password = request.json.get("password", None) #Formas de recibir el front

    login_user = User.query.filter_by(email=email).first()
    if login_user is None:
        return jsonify({"msg": "User don't exist"}), 404
    elif email != login_user.email or password != login_user.password:
        return jsonify({"msg": "Bad email or password"}), 401

#crea el acceso y devuelve un token a las personas al loguearse
    access_token = create_access_token(identity=email)
    #Enviar el token segun usuario
    response_body = {
        "access_token": access_token,
        "user": login_user.serialize()  
    } #OBJETO
    return jsonify(response_body) 
    
# Proteja una ruta con jwt_required, que eliminará las solicitudes
# sin un JWT válido presente.  
@app.route("/profile", methods=["GET"])
@jwt_required() #Portero de nuestra ruta protegida
def protected():

    # Accede a la identidad del usuario actual con get_jwt_identity
    current_user = get_jwt_identity()
    # print(current_user)
    login_user = User.query.filter_by(email=current_user).first()

    if login_user is None:
        return jsonify({"msg": "User don't exist"}), 404
    response_body = {
        "user": login_user.serialize()
    }
    return jsonify(response_body), 200
    























# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


