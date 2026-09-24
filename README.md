# FrotaFácil

MVP acadêmico em Flask para locação de bicicletas, bicicletas elétricas e
patinetes a pessoas físicas.

## Funcionalidades

- autenticação de usuário;
- cadastro e listagem de clientes;
- catálogo visual e controle da situação dos produtos;
- locação com cálculo automático do valor;
- bloqueio de equipamento já alugado;
- devolução e liberação automática do equipamento;
- painel com indicadores e alertas de atraso;
- API JSON de equipamentos disponíveis;
- interface responsiva e acessível;
- testes automatizados das regras centrais.
- proteção CSRF nos formulários;
- workflow de testes no GitHub Actions.

## Executar no Linux

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python seed.py
.venv/bin/python run.py
```

Esses comandos funcionam no Bash, Zsh e Fish sem precisar ativar o ambiente.
Se preferir ativá-lo no Fish, use `source .venv/bin/activate.fish`.

Se você já executou a versão anterior do projeto, recrie apenas os dados de
demonstração com o catálogo de mobilidade:

```bash
.venv/bin/python seed.py --reset
```

Acesse `http://127.0.0.1:5000` e entre com:

- e-mail: `admin@frotafacil.com`
- senha: `admin123`

## Testes

```bash
.venv/bin/python -m pytest -q
```

## Controle de versão

O projeto já contém `.gitignore` e um workflow de testes. Para publicar em um
repositório novo:

```bash
git init -b main
git add .
git commit -m "Cria MVP do FrotaFácil"
git remote add origin URL_DO_REPOSITORIO
git push -u origin main
```

## API

Com o usuário autenticado:

```text
GET /api/equipamentos/disponiveis
```

## Estrutura

```text
app/                 aplicação Flask
  static/            CSS e JavaScript
  templates/         páginas HTML
tests/               testes automatizados
instance/            banco SQLite local (não versionado)
run.py               servidor de desenvolvimento
seed.py              dados de demonstração
```

## Implantação em nuvem

O projeto inclui um `Dockerfile` e pode ser implantado em qualquer serviço que
aceite contêineres. Configure `SECRET_KEY` com um valor longo e aleatório. A
variável `DATABASE_URL` pode apontar para PostgreSQL sem alterar os modelos.

Para testar o contêiner localmente:

```bash
docker build -t frotafacil .
docker run --rm -p 8000:8000 -e SECRET_KEY=troque-esta-chave frotafacil
```
