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
            if claims.get('role') == 'admin':
                return fn(*args, **kwargs)
            return {'message': 'Acesso restrito a administradores.'}, 403
        return decorator
    return wrapper

# Decorador para endpoints que exigem privilégios de gerente ou administrador
def manager_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            # Permite acesso se a role for 'gerente' ou 'admin'
            if claims.get('role') in ['gerente', 'admin']:
                return fn(*args, **kwargs)
            return {'message': 'Acesso restrito a gerentes ou administradores.'}, 403
        return decorator
    return wrapper


class User(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('nome', type=str, help="O campo 'nome' não pode ser nulo.")
    parser.add_argument('email', type=str, help="O campo 'email' não pode ser nulo.")
    parser.add_argument('telefone', type=int, help="O campo 'telefone' não pode ser nulo.")
    parser.add_argument('senha', type=str, help="O campo 'senha' não pode ser nulo.")

    @jwt_required()
    def get(self, cliente_id): # lista os clientes
        current_user_id = get_jwt_identity()
        claims = get_jwt()

        # Admin pode ver todos, cliente só pode ver a si mesmo. Gerente não acessa este endpoint.
        if not (claims.get('role') == 'admin' or str(cliente_id) == str(current_user_id)):
            return {'message': 'Acesso não autorizado.'}, 403

        cliente = UserModel.find_cli_by_id(cliente_id)
        if cliente:
            return cliente.json()
        return {'message': 'Cliente não foi encontrado'}, 404

    @jwt_required()
    def put(self, cliente_id): # atualizar os dados dos clientes
        current_user_id = get_jwt_identity()
        claims = get_jwt()

        # Um administrador pode editar qualquer usuário, um cliente só pode editar a si mesmo.
        if not (claims.get('role') == 'admin' or str(cliente_id) == str(current_user_id)):
            return {'message': 'Acesso não autorizado para editar este usuário.'}, 403

        cliente = UserModel.find_cli_by_id(cliente_id)
        if not cliente:
            return {'message': 'Cliente não encontrado.'}, 404

        dados = User.parser.parse_args()
        dados_validos = {chave: valor for chave, valor in dados.items() if valor is not None}

        if not dados_validos:
            return {'message': 'Nenhum dado fornecido para atualização.'}, 400

        for chave, valor in dados_validos.items():
            setattr(cliente, chave, valor)

        try:
            cliente.save_client()
        except Exception as e:
            return {'message': f"Ocorreu um erro interno ao tentar atualizar o cliente: {e}"}, 500
        
        return cliente.json(), 200

    @admin_required() # deletar dados dos clientes
    def delete(self, cliente_id):
        cliente = UserModel.find_cli_by_id(cliente_id)
        if cliente:
            try:
                cliente.delete_user()
            except Exception as e:
                return {'message': f"Ocorreu um erro interno ao tentar deletar o cliente: {e}"}, 500
            return {'message': "Cliente deletado com sucesso."}, 200
        return {'message': "Cliente não encontrado"}, 404    
    

class UserRegister(Resource):

    atribuicao = reqparse.RequestParser()
    atribuicao.add_argument('nome', type=str, required=True, help="O campo 'nome' não pode ser deixado em branco")
    atribuicao.add_argument('email', type=str, required=True, help="O campo 'email' não pode ser deixado em branco" )
    atribuicao.add_argument('telefone', type=int, required=True, help="O campo 'telefone' não pode ser deixado em branco")
    atribuicao.add_argument('documento', type=str, required=True, help="O campo 'CPF' não pode ser deixado em branco" )
    atribuicao.add_argument('senha', type=str, required=True, help="O campo 'senha' não pode ser deixado em branco" )
    atribuicao.add_argument('role', type=str, default='cliente', help="Define a função do usuário (cliente, gerente, admin).")
    
    @admin_required()
    def post(self):
        dados = self.atribuicao.parse_args()

        if dados['role'] not in ['cliente', 'gerente', 'admin']:
            return {'message': "A função '{}' é inválida.".format(dados['role'])}, 400

        if UserModel.find_cli_by_doc(dados['documento']):
            return {'message': "O documento '{}' ja existe no sistema".format(dados['documento'])}  

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
        if cliente and cliente.role == 'cliente' and compare_digest(cliente.senha, dados['senha']):
            token_de_acesso = create_access_token(
                identity=str(cliente.cliente_id),
                additional_claims={'role': 'cliente'}
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

        # Este endpoint é para administradores e gerentes
        if admin and admin.role in ['admin', 'gerente'] and compare_digest(admin.senha, dados['senha']):
            token_de_acesso = create_access_token(
                identity=str(admin.cliente_id),
                additional_claims={'role': admin.role}
            )
            return {'acess_token': token_de_acesso}, 200
        return {'message': "Nome de administrador ou senha inválidos."}, 401

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti'] # token identifier 
        BLACKLIST.add(jwt_id)
        return {'message': "Cliente deslogado com sucesso!"}, 200
