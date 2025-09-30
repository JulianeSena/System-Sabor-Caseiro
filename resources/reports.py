from flask_restful import Resource
from sqlalchemy import func

from models.user import UserModel
from models.coupon import CuponModel
from resources.user import manager_required
from sql_alchemy import banco

class DashboardReports(Resource):
    @manager_required()
    def get(self):
    
        # Consultas para agregar os dados
        total_clientes = UserModel.query.filter_by(role='cliente').count()
        total_cupons = CuponModel.query.count()
        receita_total = banco.session.query(func.sum(CuponModel.preco_cupom)).scalar() or 0.0

        # Consulta para cupons emitidos por dia
        cupons_por_dia_query = (
            banco.session.query(
                func.date(CuponModel.data_marcacao).label('data'),
                func.count(CuponModel.cupom_id).label('quantidade')
            )
            .group_by(func.date(CuponModel.data_marcacao))
            .order_by(func.date(CuponModel.data_marcacao))
            .all()
        )
        # Formata para um JSON mais amigável
        cupons_por_dia = [{'data': r.data.format(), 'quantidade': r.quantidade} for r in cupons_por_dia_query]

        # Consulta para os 5 clientes mais ativos
        top_5_clientes_query = (
            banco.session.query(UserModel.nome, func.count(CuponModel.cupom_id).label('total_cupons'))
            .join(CuponModel, UserModel.cliente_id == CuponModel.cliente_id)
            .group_by(UserModel.nome)
            .order_by(func.count(CuponModel.cupom_id).desc())
            .limit(5)
            .all()
        )
        top_5_clientes = [{'nome': r.nome, 'total_cupons': r.total_cupons} for r in top_5_clientes_query]

        return {
            'sumario': {'total_clientes': total_clientes, 'total_cupons_emitidos': total_cupons, 'receita_total': round(receita_total, 2)},
            'cupons_por_dia': cupons_por_dia,
            'top_5_clientes': top_5_clientes
        }, 200
