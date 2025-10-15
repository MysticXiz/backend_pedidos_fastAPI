# Projeto FastAPI — Pedidos

Resumo
- Aplicação web API REST construída com FastAPI, SQLAlchemy (ORM) e Alembic (migrações).
- Autenticação por JWT (python-jose), senhas hashed com Argon2 (passlib[argon2]).
- Validações por Pydantic (v2) e email-validator.

Objetivo
- Fornecer endpoints para autenticação (signup/signin/refresh) e gestão de pedidos (routes/orders.py).
- Estrutura simples e modular, adequada para evoluir para microserviço.

Principais tecnologias
- Python 3.8+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- python-jose (JWT)
- passlib[argon2] (hash de senha)
- email-validator (validação de e-mail)
- python-dotenv (carregar .env)
- uvicorn (servidor ASGI)

Estrutura do projeto (resumo)
- main.py — ponto de entrada; configura app FastAPI, contextos e handlers globais.
- core/dependencies.py — dependências reutilizáveis (ex.: get_session, verify_token).
- database/models/models.py — modelos SQLAlchemy (User, Order, etc).
- schemas/schemas.py — modelos Pydantic (UserSchema, LoginSchema, OrderSchema).
- routes/auth.py — endpoints de autenticação (signup, signin, refresh, create-admin).
- routes/orders.py — endpoints de pedidos (CRUD).
- alembic.ini / alembic/ — configuração e scripts de migração.
- .env — variáveis sensíveis (não comitar em produção).
- requirements.txt — dependências do projeto.

Endpoints principais
- Auth
  - POST /auth/signup — cria usuário público (valida email, força regras de senha).
  - POST /auth/signin — login que retorna access_token e refresh_token.
  - POST /auth/refresh — renova access_token (necessita token válido).
  - POST /auth/create-admin — criar usuário admin (protegido).
- Orders (examples)
  - GET /orders — listar pedidos (protegido)
  - POST /orders — criar pedido (protegido)
  - GET /orders/{id} — obter pedido
  - PUT/PATCH /orders/{id} — atualizar pedido
  - DELETE /orders/{id} — remover pedido

Autenticação e segurança
- Tokens: JWT com claims mínimos { "sub": user_id, "exp": expiration }.
- Senhas: hasheadas com Argon2 (passlib[argon2]); comparar com argon2_context.verify.
- Boas práticas recomendadas:
  - Secrets (SECRET_KEY) e DATABASE_URL via .env.
  - Em produção, usar HTTPS e rotacionar SECRET_KEY periodicamente.
  - Em deploy, prefira psycopg2 (ou psycopg2-binary para dev) se usar PostgreSQL.

Validação de e-mail e senha
- Email: Pydantic EmailStr usado nos schemas; email-validator presente para normalizar/validar. O projeto também fornece validação explícita via email_validator no endpoint para retornar 400 com mensagem clara.
- Senha: validação aplicada no schema Pydantic (regras mínimas) e reforçada no endpoint (defesa em profundidade).
  - Recomendado padrão atual: mínimo 8 caracteres, letras maiúsculas/minúsculas, número e caractere especial.
  - Para validação por entropia, considerar zxcvbn-python.

Arquivo .env (exemplo)
- Crie um arquivo `.env` na raiz com as variáveis abaixo (NUNCA versionar com segredos reais):
  DATABASE_URL=postgresql://user:password@localhost:5432/dbname
  SECRET_KEY=troque_essa_chave_aleatoria
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=60
  # Outros: configurações de DB, SENTRY, etc.

Migrações (Alembic)
- Gerar revisão:
  alembic revision --autogenerate -m "mensagem"
- Aplicar migrações:
  alembic upgrade head

Execução local (Windows)
1. Criar e ativar virtualenv:
   powershell> python -m venv .venv
   powershell> .venv\Scripts\Activate

2. Instalar dependências:
   powershell> pip install -r requirements.txt

3. Preencher .env.

4. Rodar migrações (se aplicável):
   powershell> alembic upgrade head

5. Executar servidor dev:
   powershell> uvicorn main:app --reload

Tratamento de erros de validação (Pydantic/FastAPI)
- O projeto pode oferecer um exception handler em main.py para transformar erros de validação (422) em respostas 400 amigáveis quando o erro for no campo email ou senha. Isso melhora a experiência do cliente HTTP.

Dependências relevantes (resumo)
- python-jose[cryptography] — encode/decode JWT
- passlib[argon2] — Argon2 hashing
- email-validator — requerido por EmailStr
- psycopg2-binary — driver PostgreSQL (para desenvolvimento); em produção prefira psycopg2

Observações de desenvolvimento
- Testes: adicione pytest + pytest-asyncio para testes assíncronos das rotas.
- Lint/format: usar flake8 / ruff / black conforme preferência.
- Segurança: rever políticas CORS, rate limiting e proteção contra brute-force (ex.: limitar tentativas de login).
- Dados sensíveis: manter .env fora do repositório e usar secrets manager em produção.

Contribuição
- Abrir PRs para features e correções; seguir a mesma formatação de commits e rodar testes localmente antes de submeter.

Licença
- Adicionar arquivo LICENSE na raiz conforme desejar (MIT/Apache2 etc.).

Contato / próximos passos
- Revisar schemas e incluir validação de força de senha no Pydantic.
- Adicionar testes unitários para auth e endpoints críticos.
- Configurar CI (lint, testes, build de imagem) se for usar deployment automatizado.
