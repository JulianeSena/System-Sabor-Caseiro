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


