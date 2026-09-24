from app import create_app, db
import argparse

from app.models import Cliente, Equipamento, Locacao, Usuario

parser = argparse.ArgumentParser(description="Cria dados de demonstração do FrotaFácil.")
parser.add_argument(
    "--reset", action="store_true",
    help="apaga os dados locais e recria a demonstração de mobilidade individual",
)
args = parser.parse_args()

app = create_app()
with app.app_context():
    if args.reset:
        Locacao.query.delete()
        Equipamento.query.delete()
        Cliente.query.delete()
        Usuario.query.delete()
        db.session.commit()
    if not Usuario.query.filter_by(email="admin@frotafacil.com").first():
        usuario = Usuario(nome="Administrador", email="admin@frotafacil.com", senha_hash="")
        usuario.definir_senha("admin123")
        db.session.add(usuario)
    if Cliente.query.count() == 0:
        db.session.add_all([
            Cliente(nome="Mariana Alves", documento="123.456.789-00", telefone="(34) 99999-1111"),
            Cliente(nome="João Ferreira", documento="987.654.321-00", telefone="(34) 99999-2222"),
        ])
    if Equipamento.query.count() == 0:
        db.session.add_all([
            Equipamento(codigo="PAT-001", descricao="Patinete elétrico urbano", valor_diaria=35, status="disponivel"),
            Equipamento(codigo="BIC-002", descricao="Bicicleta urbana com cesta", valor_diaria=28, status="disponivel"),
            Equipamento(codigo="EBI-003", descricao="Bicicleta elétrica", valor_diaria=55, status="disponivel"),
            Equipamento(codigo="PAT-004", descricao="Patinete elétrico dobrável", valor_diaria=40, status="manutencao"),
        ])
    db.session.commit()
    print("Demonstração de mobilidade criada. Login: admin@frotafacil.com / admin123")
