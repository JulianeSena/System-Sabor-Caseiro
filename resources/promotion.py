from flask_restful import Resource, reqparse
from models.promotion import PromotionModel
from resources.user import manager_required
from flask_jwt_extended import jwt_required

# Parser para criar uma promoção
parser = reqparse.RequestParser()
parser.add_argument('titulo', type=str, required=True, help="O campo 'titulo' é obrigatório.")
parser.add_argument('descricao', type=str, required=False, help="Descrição da promoção.")

# Parser para atualizar uma promoção (incluindo ativação)
update_parser = reqparse.RequestParser()
update_parser.add_argument('titulo', type=str)
update_parser.add_argument('descricao', type=str)
update_parser.add_argument('is_ativa', type=bool, help="Define se a promoção está ativa ou não.")

class Promotion(Resource):
    @manager_required()
    def get(self, promocao_id):
        promocao = PromotionModel.find_by_id(promocao_id)
        if promocao:
            return promocao.json()
        return {'message': 'Promoção não encontrada.'}, 404

    @manager_required()
    def put(self, promocao_id):
        promocao = PromotionModel.find_by_id(promocao_id)
        if not promocao:
            return {'message': 'Promoção não encontrada.'}, 404

        dados = update_parser.parse_args()
        
        # Atualiza os campos apenas se eles foram fornecidos no request
        if dados.get('titulo') is not None:
            promocao.titulo = dados['titulo']
        if dados.get('descricao') is not None:
            promocao.descricao = dados['descricao']
        if dados.get('is_ativa') is not None:
            promocao.is_ativa = dados['is_ativa']
        
        try:
            promocao.save_to_db()
        except:
            return {'message': 'Ocorreu um erro ao atualizar a promoção.'}, 500
        
        return promocao.json(), 200

    @manager_required()
    def delete(self, promocao_id):
        promocao = PromotionModel.find_by_id(promocao_id)
        if not promocao:
            return {'message': 'Promoção não encontrada.'}, 404
        
        try:
            promocao.delete_from_db()
        except:
            return {'message': 'Ocorreu um erro ao deletar a promoção.'}, 500
        
        return {'message': 'Promoção deletada com sucesso.'}, 200

class PromotionList(Resource):
    @manager_required()
    def get(self):
        """Lista todas as promoções para o painel do gerente/admin."""
        return {'promocoes': [p.json() for p in PromotionModel.find_all()]}, 200

    @manager_required()
    def post(self):
        """Cria uma nova promoção (inicia como inativa)."""
        dados = parser.parse_args()
        promocao = PromotionModel(**dados)
        try:
            promocao.save_to_db()
        except:
            return {'message': 'Ocorreu um erro ao salvar a promoção.'}, 500
        return promocao.json(), 201

class ActivePromotions(Resource):
    @jwt_required()
    def get(self):
        """Lista apenas as promoções ativas, visível para clientes logados."""
        return {'promocoes_ativas': [p.json() for p in PromotionModel.find_all_active()]}, 200
