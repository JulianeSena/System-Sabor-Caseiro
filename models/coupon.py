from sql_alchemy import banco
from datetime import datetime

class CuponModel(banco.Model):
    __tablename__ = 'cupons'

    cupom_id = banco.Column(banco.Integer, primary_key=True)
    data_marcacao = banco.Column(banco.DateTime, nullable=False, default=datetime.utcnow)
    preco_cupom = banco.Column(banco.Float, nullable=False)

    # relacao cupon -> cliente
    cliente_id = banco.Column(banco.Integer, banco.ForeignKey('cliente.cliente_id'), nullable=False)

    def __init__(self, cliente_id, preco_cupom):
        self.cliente_id = cliente_id
        self.preco_cupom = preco_cupom

    def json(self):
        return{
            'cupom_id': self.cupom_id,
            'data_marcacao': self.data_marcacao.isoformat(),
            'preco_cupom': self.preco_cupom
        }

    def save_cupom(self):
        banco.session.add(self)
        banco.session.commit()
        
            