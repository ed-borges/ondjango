# Ondjango

Protótipo de uma plataforma de aprendizagem online para Angola, agora servido por Django.

## Executar localmente

Requisitos: Python 3.10 ou superior.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abre http://127.0.0.1:8000/. Para testar: `python manage.py test`.

## Estado atual

O Django serve o protótipo existente de catálogo, pesquisa, filtros e aulas demonstrativas. Os dados dos cursos continuam no JavaScript e o progresso fica apenas no navegador. Ainda não existem contas de aluno, cursos na base de dados ou sincronização entre dispositivos. SQLite é utilizado para desenvolvimento; a configuração fornecida não está pronta para produção.

A direção técnica está descrita em [docs/arquitetura.md](docs/arquitetura.md).
