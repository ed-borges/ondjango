# Ondjango

Protótipo de uma plataforma de aprendizagem online para Angola, agora servido por Django.

## Executar localmente

Requisitos: Python 3.10 ou superior.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo  # opcional: adiciona cursos de demonstração
python manage.py createsuperuser  # opcional: acesso ao painel administrativo
python manage.py runserver
```

Abre http://127.0.0.1:8000/. Para testar: `python manage.py test`.

## Estado atual

Cursos e aulas são guardados na base de dados e geridos em `/admin/`. Apenas conteúdo publicado aparece no catálogo. O comando `seed_demo` adiciona exemplos sem substituir cursos existentes. O conteúdo inicial é demonstrativo e deve ser editado antes de usar em produção.

Os alunos podem criar uma conta, entrar e guardar aulas concluídas no servidor para consultar noutros dispositivos. Sem sessão, o progresso fica apenas no navegador e não é importado automaticamente para uma conta. SQLite é utilizado para desenvolvimento; a configuração fornecida não está pronta para produção. Recuperação de palavra-passe e verificação de email ainda não estão implementadas.

A direção técnica está descrita em [docs/arquitetura.md](docs/arquitetura.md).
