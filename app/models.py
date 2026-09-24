from datetime import date
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    documento = db.Column(db.String(20), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    locacoes = db.relationship("Locacao", back_populates="cliente")


class Equipamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)
    descricao = db.Column(db.String(120), nullable=False)
    valor_diaria = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="disponivel")
    locacoes = db.relationship("Locacao", back_populates="equipamento")


class Locacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    equipamento_id = db.Column(db.Integer, db.ForeignKey("equipamento.id"), nullable=False)
    data_retirada = db.Column(db.Date, nullable=False)
    data_prevista = db.Column(db.Date, nullable=False)
    data_devolucao = db.Column(db.Date)
    valor_diaria = db.Column(db.Numeric(10, 2), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="ativa")

    cliente = db.relationship("Cliente", back_populates="locacoes")
    equipamento = db.relationship("Equipamento", back_populates="locacoes")

    @staticmethod
    def calcular_total(inicio, fim, diaria):
        dias = max((fim - inicio).days, 1)
        return Decimal(str(diaria)) * dias

    @property
    def atrasada(self):
        return self.status == "ativa" and self.data_prevista < date.today()

