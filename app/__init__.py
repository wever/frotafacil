import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = "main.login"
login_manager.login_message = "Faça login para continuar."
login_manager.login_message_category = "warning"


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-change-this-key"),
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL", f"sqlite:///{os.path.join(app.instance_path, 'gestao.db')}"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .models import Usuario
    from .routes import bp

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    app.register_blueprint(bp)

    @app.template_filter("moeda")
    def moeda(valor):
        numero = float(valor or 0)
        texto = f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {texto}"

    @app.template_filter("imagem_produto")
    def imagem_produto(codigo):
        prefixo = (codigo or "").upper().split("-")[0]
        imagens = {
            "PAT": "images/patinete.svg",
            "BIC": "images/bicicleta.svg",
            "EBI": "images/bicicleta-eletrica.svg",
        }
        return imagens.get(prefixo, "images/mobilidade.svg")

    with app.app_context():
        db.create_all()

    return app
