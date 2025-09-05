from flask_restful import Api, Resource, reqparse
from models.user import UserModel
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity, verify_jwt_in_request
from hmac import compare_digest
from blacklist import BLACKLIST
from functools import wraps


# Decorador para endpoints que exigem privilégios de administrador
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('is_admin'):
                return fn(*args, **kwargs)
            return {'message': 'Acesso restrito a administradores.'}, 403
        return decorator
    return wrapper



class User(Resource):
    @jwt_required()
    def get(self, cliente_id):
        current_user_id = get_jwt_identity()
        claims = get_jwt()

        # Um administrador pode ver qualquer usuário, um cliente só pode ver a si mesmo.
        if not (claims.get('is_admin') or str(cliente_id) == str(current_user_id)):
            return {'message': 'Acesso não autorizado.'}, 403

        cliente = UserModel.find_cli_by_id(cliente_id)
        if cliente:
            return cliente.json()
        return {'message': 'Cliente não foi encontrado'}, 404

    @admin_required()
    def delete(self, cliente_id):
        cliente = UserModel.find_cli_by_id(cliente_id)
        if cliente:
            try:
                cliente.delete_user()
            except:
                return {'message': "Ocorreu um erro interno tentando deletar o cliente"}, 500
            return {'message': "Cliente deletado"}
        return {'message': "Cliente não encontrado"}, 404    
    

class UserRegister(Resource):

    atribuicao = reqparse.RequestParser()
    atribuicao.add_argument('nome', type=str, required=True, help="O campo 'nome' não pode ser deixado em branco")
    atribuicao.add_argument('email', type=str, required=True, help="O campo 'email' não pode ser deixado em branco" )
    atribuicao.add_argument('telefone', type=int, required=True, help="O campo 'telefone' não pode ser deixado em branco")
    atribuicao.add_argument('documento', type=str, required=True, help="O campo 'CPF' não pode ser deixado em branco" )
    atribuicao.add_argument('senha', type=str, required=True, help="O campo 'senha' não pode ser deixado em branco" )
    atribuicao.add_argument('is_admin', type=bool, help="Define se o usuário é um administrador.")
    
    @admin_required()
    def post(self):
        dados = self.atribuicao.parse_args()

        if UserModel.find_cli_by_doc(dados['documento']):
            return {'message': "O documento '{}' ja existe no sistema".format(dados['documento'])}  
        
        # Garante que o campo is_admin seja booleano
        if dados.get('is_admin') is None:
            dados['is_admin'] = False

        cliente = UserModel(**dados)
        cliente.save_client()
        return {'message': "Cliente registrado no sistema com sucesso!"}, 201


class UserLogin(Resource):

    parser = reqparse.RequestParser()   
    parser.add_argument('documento', type=str, required=True, help="O campo 'CPF' não pode ser deixado em branco" )
    parser.add_argument('senha', type=str, required=True, help="O campo 'senha' não pode ser deixado em branco" )
    @classmethod
    def post(cls):
        dados = cls.parser.parse_args()

        cliente = UserModel.find_cli_by_doc(dados['documento'])

        # Este endpoint é para clientes (não administradores)
        if cliente and not cliente.is_admin and compare_digest(cliente.senha, dados['senha']):
            token_de_acesso = create_access_token(
                identity=str(cliente.cliente_id),
                additional_claims={'is_admin': False}
            )
            return {'acess_token': token_de_acesso}, 200
        return {'message': "Documento ou senha Incorreto"}, 401

class AdminLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('nome', type=str, required=True, help="O campo 'nome' não pode ser deixado em branco")
    parser.add_argument('senha', type=str, required=True, help="O campo 'senha' não pode ser deixado em branco" )


    @classmethod
    def post(cls):
        dados = cls.parser.parse_args()

        admin = UserModel.find_cli_by_name(dados['nome'])

        # Este endpoint é apenas para administradores
        if admin and admin.is_admin and compare_digest(admin.senha, dados['senha']):
            token_de_acesso = create_access_token(identity=str(admin.cliente_id), additional_claims={'is_admin': True})
            return {'acess_token': token_de_acesso}, 200
        return {'message': "Nome de administrador ou senha inválidos."}, 401

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti'] # token identifier 
        BLACKLIST.add(jwt_id)
        return {'message': "Cliente deslogado com sucesso!"}, 200
