from flask_restful import Resource, reqparse
from models.user import UserModel
from models.coupon import CuponModel
from resources.user import admin_required
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import traceback


coupon_parser = reqparse.RequestParser()
coupon_parser.add_argument('preco_cupom', type=float, required=True, help="O campo 'preco_cupom' é obrigatório.")

class Coupon(Resource):
    @admin_required()
    def post(self, cliente_id):
        """
        Adiciona um novo cupom para um cliente.
        Apenas administradores podem realizar esta ação.
        """
        cliente = UserModel.find_cli_by_id(cliente_id)
        if not cliente:
            return {'message': 'Cliente não encontrado.'}, 404

        dados = coupon_parser.parse_args()
        
        novo_cupom = CuponModel(cliente_id=cliente_id, **dados)
        
        try:
            novo_cupom.save_cupom()
        except Exception as e:
            traceback.print_exc()
            return {'message': f'Ocorreu um erro interno ao salvar o cupom. {e}'}, 500

        return novo_cupom.json(), 201

class ClientCoupons(Resource):
    @jwt_required()
    def get(self, cliente_id):
        """
        - Administradores podem ver os cupons de qualquer cliente.
        - Clientes podem ver apenas os seus próprios cupons.
        """
        current_user_id = get_jwt_identity()
        claims = get_jwt()

        # Verifica se o usuário logado é admin ou se está tentando acessar seus próprios cupons
        if not (claims.get('role') == 'admin' or str(cliente_id) == str(current_user_id)):
            return {'message': 'Acesso não autorizado.'}, 403

        cliente = UserModel.find_cli_by_id(cliente_id)
        if not cliente:
            return {'message': 'Cliente não encontrado.'}, 404

        # Retorna a lista de cupons do cliente em formato JSON
        return {'cupons': [cupom.json() for cupom in cliente.cupons]}, 200
