from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from . import db
from .models import Cliente, Equipamento, Locacao, Usuario

bp = Blueprint("main", __name__)


def ler_data(valor):
    return datetime.strptime(valor, "%Y-%m-%d").date()


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        usuario = Usuario.query.filter_by(email=request.form["email"].strip().lower()).first()
        if usuario and usuario.verificar_senha(request.form["senha"]):
            login_user(usuario)
            return redirect(url_for("main.dashboard"))
        flash("E-mail ou senha inválidos.", "danger")
    return render_template("login.html")


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))


@bp.route("/")
@login_required
def dashboard():
    hoje = date.today()
    dados = {
        "disponiveis": Equipamento.query.filter_by(status="disponivel").count(),
        "alugados": Equipamento.query.filter_by(status="alugado").count(),
        "manutencao": Equipamento.query.filter_by(status="manutencao").count(),
        "atrasadas": Locacao.query.filter(
            Locacao.status == "ativa", Locacao.data_prevista < hoje
        ).count(),
    }
    receita = db.session.query(db.func.coalesce(db.func.sum(Locacao.valor_total), 0)).scalar()
    ultimas = Locacao.query.order_by(Locacao.id.desc()).limit(6).all()
    return render_template("dashboard.html", dados=dados, receita=receita, ultimas=ultimas)


@bp.route("/clientes", methods=["GET", "POST"])
@login_required
def clientes():
    if request.method == "POST":
        documento = request.form["documento"].strip()
        if Cliente.query.filter_by(documento=documento).first():
            flash("Já existe um cliente com esse documento.", "danger")
        else:
            db.session.add(Cliente(
                nome=request.form["nome"].strip(), documento=documento,
                telefone=request.form["telefone"].strip()
            ))
            db.session.commit()
            flash("Cliente cadastrado.", "success")
            return redirect(url_for("main.clientes"))
    return render_template("clientes.html", clientes=Cliente.query.order_by(Cliente.nome).all())


@bp.route("/equipamentos", methods=["GET", "POST"])
@login_required
def equipamentos():
    if request.method == "POST":
        codigo = request.form["codigo"].strip().upper()
        try:
            diaria = Decimal(request.form["valor_diaria"].replace(",", "."))
        except InvalidOperation:
            diaria = Decimal("0")
        if Equipamento.query.filter_by(codigo=codigo).first():
            flash("O código informado já está cadastrado.", "danger")
        elif diaria <= 0:
            flash("Informe um valor de diária válido.", "danger")
        else:
            db.session.add(Equipamento(
                codigo=codigo, descricao=request.form["descricao"].strip(),
                valor_diaria=diaria, status=request.form["status"]
            ))
            db.session.commit()
            flash("Equipamento cadastrado.", "success")
            return redirect(url_for("main.equipamentos"))
    return render_template(
        "equipamentos.html", equipamentos=Equipamento.query.order_by(Equipamento.codigo).all()
    )


@bp.route("/locacoes", methods=["GET", "POST"])
@login_required
def locacoes():
    if request.method == "POST":
        equipamento = db.get_or_404(Equipamento, int(request.form["equipamento_id"]))
        inicio = ler_data(request.form["data_retirada"])
        fim = ler_data(request.form["data_prevista"])
        if equipamento.status != "disponivel":
            flash("O equipamento não está disponível.", "danger")
        elif fim < inicio:
            flash("A devolução prevista não pode ser anterior à retirada.", "danger")
        else:
            total = Locacao.calcular_total(inicio, fim, equipamento.valor_diaria)
            locacao = Locacao(
                cliente_id=int(request.form["cliente_id"]), equipamento_id=equipamento.id,
                data_retirada=inicio, data_prevista=fim, valor_diaria=equipamento.valor_diaria,
                valor_total=total, status="ativa"
            )
            equipamento.status = "alugado"
            db.session.add(locacao)
            db.session.commit()
            flash("Locação registrada.", "success")
            return redirect(url_for("main.locacoes"))
    return render_template(
        "locacoes.html",
        locacoes=Locacao.query.order_by(Locacao.id.desc()).all(),
        clientes=Cliente.query.order_by(Cliente.nome).all(),
        equipamentos=Equipamento.query.filter_by(status="disponivel").order_by(Equipamento.codigo).all(),
        hoje=date.today().isoformat(),
    )


@bp.post("/locacoes/<int:locacao_id>/devolver")
@login_required
def devolver(locacao_id):
    locacao = db.get_or_404(Locacao, locacao_id)
    if locacao.status != "ativa":
        flash("Essa locação já foi encerrada.", "warning")
    else:
        locacao.status = "encerrada"
        locacao.data_devolucao = date.today()
        locacao.equipamento.status = "disponivel"
        db.session.commit()
        flash("Devolução registrada e equipamento liberado.", "success")
    return redirect(url_for("main.locacoes"))


@bp.get("/api/equipamentos/disponiveis")
@login_required
def api_disponiveis():
    itens = Equipamento.query.filter_by(status="disponivel").order_by(Equipamento.codigo).all()
    return jsonify([
        {"id": item.id, "codigo": item.codigo, "descricao": item.descricao,
         "valor_diaria": float(item.valor_diaria)} for item in itens
    ])

