from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from resources.user import User, UserRegister, UserLogin, AdminLogin, UserLogout, UserSearch
from resources.reports import DashboardReports, PrevisaoRefeicoes
from resources.promotion import Promotion, PromotionList, ActivePromotions
from resources.coupon import Coupon, ClientCoupons
from blacklist import BLACKLIST
from sql_alchemy import banco
from flask_cors import CORS
from flask_migrate import Migrate
#from resources.refeicao import RefeicaoEstatisticasResource



app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
banco.init_app(app)

migrate = Migrate(app, banco)

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
    # status code para "Unauthorized" é 401.
    return jsonify({'message': "Voce foi deslogado da sua conta"}), 401


api.add_resource(User, '/cliente/<int:cliente_id>') #editar clientes - listar, atualizar, deletar
api.add_resource(UserRegister, '/cadastro') # registrar cliente
api.add_resource(UserLogin, '/login/cliente') # login cliente
api.add_resource(UserLogout, '/logout') # cliente logout
api.add_resource(AdminLogin, '/admin/login') # adm login
api.add_resource(Coupon, '/cliente/<int:cliente_id>/cupom') # add cupoum para cliente
api.add_resource(ClientCoupons, '/cliente/<int:cliente_id>/cupons') # endpoint de visualizacao de cupom, se for cliente ira visualizar apenas os seus cupons
api.add_resource(DashboardReports, '/relatorios/dashboard') # endpoint para o dashboard do gerente
api.add_resource(PromotionList, '/promocoes') # Gerente/Admin: Criar e listar todas as promoções
api.add_resource(Promotion, '/promocoes/<int:promocao_id>') # Gerente/Admin: Ver, atualizar (ativar/desativar) e deletar promoção
api.add_resource(ActivePromotions, '/promocoes/ativas') # Cliente: Ver promoções ativas
api.add_resource(UserSearch, '/cliente/busca')
api.add_resource(PrevisaoRefeicoes, '/relatorios/previsao_refeicoes') # endpoint para previsao de refeicoes dos clientes




if __name__ == '__main__':
    app.run(debug=True)