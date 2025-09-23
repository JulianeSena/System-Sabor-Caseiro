from sql_alchemy import banco

class UserModel(banco.Model):
    __tablename__ = 'cliente'

    cliente_id = banco.Column(banco.Integer, primary_key=True)
    nome = banco.Column(banco.String(40), unique=True, nullable=False)
    email = banco.Column(banco.String(60), unique=True, nullable=False)
    telefone = banco.Column(banco.Integer, unique=True, nullable=False)
    documento = banco.Column(banco.String(11), unique=True, nullable=False)
    senha = banco.Column(banco.String(120), nullable=False)
    role = banco.Column(banco.String(20), default='cliente', nullable=False) # 'cliente', 'gerente', 'admin'

    # cascade="all, delete-orphan": Se um cliente for deletado, todos os seus cupons também serão.
    cupons = banco.relationship('CuponModel', backref='cliente', lazy=True, cascade='all, delete-orphan')

    def __init__(self, nome, email, telefone, documento, senha, role='cliente'):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.documento = documento
        self.senha = senha
        self.role = role

    def json(self):
        total_de_cupons = len(self.cupons)
        cupons_no_cartao_atual = total_de_cupons % 10
        cupons_para_proximo_desconto = 10 - cupons_no_cartao_atual
        if cupons_para_proximo_desconto == 10:
            cupons_para_proximo_desconto = 0 # Se acabou de completar, não falta nenhum para o desconto atual

        return {
            'cliente_id': self.cliente_id,
            'nome': self.nome,
            'email': self.email,
            'cupons_total': total_de_cupons,
            'cupons_cartao_atual': cupons_no_cartao_atual,
            'cupons_para_proximo_desconto': cupons_para_proximo_desconto,
            'descontos_disponiveis': total_de_cupons // 10
        }

    @classmethod
    def find_cli_by_name(cls, nome):
        cliente_nome = cls.query.filter_by(nome=nome).first()
        if cliente_nome:
            return cliente_nome
        return None

    @classmethod
    def find_cli_by_doc(cls, documento):
        cliente_doc = cls.query.filter_by(documento=documento).first() # select * from clientes where documento = $documento 
        if cliente_doc:
            return cliente_doc
        return None


    @classmethod
    def find_cli_by_id(cls, cliente_id):
        cliente = cls.query.filter_by(cliente_id=cliente_id).first()
        if cliente:
            return cliente
        return None


    def save_client(self):
        banco.session.add(self)
        banco.session.commit()

    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()

   