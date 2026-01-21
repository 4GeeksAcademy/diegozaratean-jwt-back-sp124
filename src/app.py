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
from models import db, User
#from models import Person
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

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

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-sec1!TQQQ si ustede tiene una clave muy larag"  # Change this!
jwt = JWTManager(app)
# clave = calve cifrada
# casa = asdfasdfasdfausdfiasjdfahskfjdhasdkjfhjkashdfkjasdhfkj
# perro = adgagadfg
# casa = casasuper-secret algo que hace mas disificl decifar
# perro = perrosuper-secret algo que hace mas disificl decifar
# xxxxx = cualessuper-secret algo que hace mas disificl decifar
# xxxxxxxx = asdgafgafdgadfgadfgafdgafdg
# casa = asdfafs
# casa = rtyjrtjy
# casa = yjrtyjrtyj


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()
    print(email)
    print(user)
    if user is None:
        return jsonify({"msg": "the user is not in the system"}), 401
    print(user.serialize())
    print(user.email)
    if password != user.password:
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/secret', methods=['GET'])
@jwt_required()
def get_secret():

    response_body = {
        "msg": "Top secret ",
        "secretos":[
            "el 5g es para controlarnos",
            "que la tierra es plana",
            "las palomas son drones"
        ]
    }

    return jsonify(response_body), 200
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
