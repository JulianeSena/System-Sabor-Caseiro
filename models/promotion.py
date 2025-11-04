from sql_alchemy import banco
from datetime import datetime

class PromotionModel(banco.Model):
    __tablename__ = 'promocoes'

    promocao_id = banco.Column(banco.Integer, primary_key=True)
    titulo = banco.Column(banco.String(80), nullable=False)
    descricao = banco.Column(banco.String(255), nullable=True)
    is_ativa = banco.Column(banco.Boolean, default=False, nullable=False)
    data_criacao = banco.Column(banco.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, titulo, descricao=None):
        self.titulo = titulo
        self.descricao = descricao
        self.is_ativa = False # promos iniciam como inativas, tem q ativar pelo gerent

    def json(self):
        return {
            'promocao_id': self.promocao_id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'is_ativa': self.is_ativa,
            'data_criacao': self.data_criacao.isoformat()
        }

    @classmethod
    def find_by_id(cls, promocao_id):
        return cls.query.filter_by(promocao_id=promocao_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.order_by(cls.data_criacao.desc()).all()
    
    @classmethod
    def find_all_active(cls):
        return cls.query.filter_by(is_ativa=True).order_by(cls.data_criacao.desc()).all()

    def save_to_db(self):
        banco.session.add(self)
        banco.session.commit()

    def delete_from_db(self):
        banco.session.delete(self)
        banco.session.commit()
