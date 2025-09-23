from getpass import getpass
from app import app
from models.user import UserModel
from sql_alchemy import banco

def create_first_admin():
    """Cria o primeiro usuário administrador via linha de comando."""
    with app.app_context():
        banco.create_all()

        # Verifica se um administrador já existe
        if UserModel.query.filter_by(role='admin').first():
            print("Um administrador já existe no sistema.")
            return

        # Coleta os dados para o novo administrador
        print("--- Criando o primeiro administrador ---")
        nome = input("Nome do administrador: ")
        email = input("Email do administrador: ")
        telefone = input("Telefone do administrador: ")
        documento = input("Documento (CPF) do administrador: ")
        senha = getpass("Senha do administrador: ")

        if UserModel.find_cli_by_doc(documento):
            print(f"Já existe um usuário com o documento {documento}.")
            return

        admin_user = UserModel(
            nome=nome, email=email, telefone=int(telefone),
            documento=documento, senha=senha, role='admin'
        )
        try:
            admin_user.save_client()
            print("\nAdministrador criado com sucesso!")
        except Exception as e:
            print(f"\nOcorreu um erro: {e}")

if __name__ == '__main__':
    create_first_admin()