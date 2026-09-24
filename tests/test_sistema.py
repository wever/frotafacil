from datetime import date
from decimal import Decimal

from app import db
from app.models import Cliente, Equipamento, Locacao


def test_calculo_da_locacao():
    assert Locacao.calcular_total(date(2026, 9, 1), date(2026, 9, 4), 200) == Decimal("600")
    assert Locacao.calcular_total(date(2026, 9, 1), date(2026, 9, 1), 200) == Decimal("200")


def test_login_invalido(client):
    resposta = client.post("/login", data={"email": "x@x.com", "senha": "errada"})
    assert "E-mail ou senha inválidos" in resposta.get_data(as_text=True)


def test_locacao_bloqueia_e_devolucao_libera(app, autenticado):
    with app.app_context():
        cliente = Cliente(nome="Pessoa Teste", documento="123", telefone="34999999999")
        equipamento = Equipamento(codigo="PAT-01", descricao="Patinete elétrico", valor_diaria=30, status="disponivel")
        db.session.add_all([cliente, equipamento])
        db.session.commit()
        cliente_id, equipamento_id = cliente.id, equipamento.id

    resposta = autenticado.post("/locacoes", data={
        "cliente_id": cliente_id, "equipamento_id": equipamento_id,
        "data_retirada": "2026-09-01", "data_prevista": "2026-09-03"
    })
    assert resposta.status_code == 302

    with app.app_context():
        equipamento = db.session.get(Equipamento, equipamento_id)
        locacao = Locacao.query.one()
        assert equipamento.status == "alugado"
        assert locacao.valor_total == Decimal("60.00")
        locacao_id = locacao.id

    autenticado.post(f"/locacoes/{locacao_id}/devolver")
    with app.app_context():
        assert db.session.get(Equipamento, equipamento_id).status == "disponivel"
        assert db.session.get(Locacao, locacao_id).status == "encerrada"


def test_api_retorna_apenas_disponiveis(app, autenticado):
    with app.app_context():
        db.session.add_all([
            Equipamento(codigo="A", descricao="Disponível", valor_diaria=10, status="disponivel"),
            Equipamento(codigo="B", descricao="Alugado", valor_diaria=10, status="alugado"),
        ])
        db.session.commit()
    resposta = autenticado.get("/api/equipamentos/disponiveis")
    assert resposta.status_code == 200
    assert [item["codigo"] for item in resposta.get_json()] == ["A"]


def test_todas_as_paginas_principais_renderizam(autenticado):
    for rota in ["/", "/clientes", "/equipamentos", "/locacoes"]:
        resposta = autenticado.get(rota)
        assert resposta.status_code == 200
        assert "FrotaFácil" in resposta.get_data(as_text=True)


def test_catalogo_exibe_imagem_do_produto(app, autenticado):
    with app.app_context():
        db.session.add(Equipamento(
            codigo="PAT-009", descricao="Patinete de teste",
            valor_diaria=25, status="disponivel"
        ))
        db.session.commit()
    pagina = autenticado.get("/equipamentos").get_data(as_text=True)
    assert "images/patinete.svg" in pagina
    assert "Patinete de teste" in pagina
