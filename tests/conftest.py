import pytest

from app import create_app, db
from app.models import Usuario


@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        usuario = Usuario(nome="Administrador", email="admin@teste.com", senha_hash="")
        usuario.definir_senha("123456")
        db.session.add(usuario)
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def autenticado(client):
    client.post("/login", data={"email": "admin@teste.com", "senha": "123456"})
    return client
