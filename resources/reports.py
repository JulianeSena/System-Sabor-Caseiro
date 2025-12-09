from flask_restful import Resource
from sqlalchemy import func
from datetime import timedelta, datetime
from models.user import UserModel
from models.coupon import CuponModel
from resources.user import manager_required
from sql_alchemy import banco

class DashboardReports(Resource):
    @manager_required()
    def get(self):
    
        
        total_clientes = UserModel.query.filter_by(role='cliente').count()
        total_cupons = CuponModel.query.count()
        receita_total = banco.session.query(func.sum(CuponModel.preco_cupom)).scalar() or 0.0

        cupons_por_dia_query = (
            banco.session.query(
                func.date(CuponModel.data_marcacao).label('data'),
                func.count(CuponModel.cupom_id).label('quantidade')
            )
            .group_by(func.date(CuponModel.data_marcacao))
            .order_by(func.date(CuponModel.data_marcacao))
            .all()
        )
      
        cupons_por_dia = [{'data': r.data.format(), 'quantidade': r.quantidade} for r in cupons_por_dia_query]

    
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
    
class PrevisaoRefeicoes(Resource):
    @manager_required()
    def get(self):
        try:
            
            clientes = UserModel.query.filter_by(role='cliente').all()
            previsoes = []
            
            for cliente in clientes:
                
                cupons = CuponModel.query.filter_by(
                    cliente_id=cliente.cliente_id
                ).order_by(CuponModel.data_marcacao).all()
                
                total_refeicoes = len(cupons)
                
               
                if total_refeicoes >= 10:
                    previsoes.append({
                        'cliente_id': cliente.cliente_id,
                        'cliente_nome': cliente.nome,
                        'refeicoes_realizadas': total_refeicoes,
                        'refeicoes_faltantes': 0,
                        'status': 'Completado',
                        'data_previsao': None,
                        'intervalo_medio_dias': None,
                        'confiabilidade': 'N/A'
                    })
                    continue
                
                
                if total_refeicoes == 0:
                    previsoes.append({
                        'cliente_id': cliente.cliente_id,
                        'cliente_nome': cliente.nome,
                        'refeicoes_realizadas': 0,
                        'refeicoes_faltantes': 10,
                        'status': 'Sem dados',
                        'data_previsao': None,
                        'intervalo_medio_dias': None,
                        'confiabilidade': 'Insuficiente'
                    })
                    continue
                
                
                datas_refeicoes = [cupom.data_marcacao for cupom in cupons]
                
                
                if len(datas_refeicoes) > 1:
                    
                    intervalos = []
                    for i in range(1, len(datas_refeicoes)):
                        diferenca = (datas_refeicoes[i] - datas_refeicoes[i-1]).days
                        if diferenca > 0:  
                            intervalos.append(diferenca)
                    
                    
                    if intervalos:
                        intervalo_medio = sum(intervalos) / len(intervalos)
                    else:
                        
                        intervalo_medio = 1
                else:
                   
                    intervalo_medio = 1
                
                
                refeicoes_faltantes = 10 - total_refeicoes
                
               
                ultima_data = datas_refeicoes[-1]
                dias_faltantes = intervalo_medio * refeicoes_faltantes
                data_previsao = ultima_data + timedelta(days=dias_faltantes)
                
                
                if total_refeicoes >= 5:
                    confiabilidade = 'Alta'
                elif total_refeicoes >= 3:
                    confiabilidade = 'Média'
                else:
                    confiabilidade = 'Baixa'
                
                previsoes.append({
                    'cliente_id': cliente.cliente_id,
                    'cliente_nome': cliente.nome,
                    'refeicoes_realizadas': total_refeicoes,
                    'refeicoes_faltantes': refeicoes_faltantes,
                    'status': 'Em progresso',
                    'data_previsao': data_previsao.strftime('%Y-%m-%d'),
                    'intervalo_medio_dias': round(intervalo_medio, 2),
                    'confiabilidade': confiabilidade
                })
            
            
            previsoes_ativas = [p for p in previsoes if p['status'] == 'Em progresso']
            previsoes_ativas.sort(key=lambda x: x['data_previsao'])
            
           
            previsoes_completadas = [p for p in previsoes if p['status'] == 'Completado']
            previsoes_sem_dados = [p for p in previsoes if p['status'] == 'Sem dados']
            
            return {
                'resumo': {
                    'em_progresso': len(previsoes_ativas),
                    'completados': len(previsoes_completadas),
                    'sem_dados': len(previsoes_sem_dados)
                },
                'previsoes_proximas': previsoes_ativas[:10], 
                'todas_previsoes': previsoes_ativas + previsoes_completadas + previsoes_sem_dados
            }, 200
            
        except Exception as e:
            return {'message': str(e)}, 400 
