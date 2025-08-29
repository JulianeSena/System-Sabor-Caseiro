from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from resources.user import User, UserRegister, UserLogin, AdminLogin, UserLogout
from resources.coupon import Coupon
from blacklist import BLACKLIST
from sql_alchemy import banco


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
banco.init_app(app)

app.config['JWT_SECRET_KEY'] = 'adicionarchaveaenv'
app.config['JWT_BLACKLIST_ENABLED'] = True



api = Api(app)
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader #decorador recebe dois args
def verifica_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in BLACKLIST


@jwt.revoked_token_loader
def token_acess_invalid():
    # O status code para "Unauthorized" é 401.
    return jsonify({'message': "Voce foi deslogado da sua conta"}), 401


api.add_resource(User, '/cliente/<int:cliente_id>')
api.add_resource(UserRegister, '/cadastro')
api.add_resource(UserLogin, '/login/cliente')
api.add_resource(AdminLogin, '/admin/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(Coupon, '/cliente/<int:cliente_id>/cupom')
    



if __name__ == '__main__':
    app.run(debug=True)