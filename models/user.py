from sql_alchemy import banco

class UserModel(banco.Model):
    __tablename__ = 'cliente'

    cliente_id = banco.Column(banco.Integer, primary_key=True)
    nome = banco.Column(banco.String(40), unique=True, nullable=False)
    email = banco.Column(banco.String(60), unique=True, nullable=False)
    telefone = banco.Column(banco.Integer, unique=True, nullable=False)
    documento = banco.Column(banco.String(11), unique=True, nullable=False)
    senha = banco.Column(banco.String(120), nullable=False)
    is_admin = banco.Column(banco.Boolean, default=False, nullable=False)

    def __init__(self, nome, email, telefone, documento, senha, is_admin=False):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.documento = documento
        self.senha = senha
        self.is_admin = is_admin

    def json(self):
        return {
            'cliente_id': self.cliente_id,
            'email': self.email
        }    

    @classmethod
    def find_cli_by_doc(cls, documento):
        cliente_doc = cls.query.filter_by(documento=documento).first() # select * from clientes where documento = $documento 
        if cliente_doc:
            return cliente_doc
        return None


    @classmethod
    def find_cli_by_id(cls, cliente_id):
        cliente_id = cls.query.filter_by(cliente_id=cliente_id).first()
        if cliente_id:
            return cliente_id
        return None


    def save_client(self):
        banco.session.add(self)
        banco.session.commit()

    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()

   