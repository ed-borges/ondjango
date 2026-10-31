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
python manage.py seed_lab_demo  # opcional: adiciona um exercício demonstrativo
python manage.py createsuperuser  # opcional: acesso ao painel administrativo
python manage.py runserver
```

Abre http://127.0.0.1:8000/. Para testar: `python manage.py test`.

## Estado atual

Cursos e aulas são guardados na base de dados e geridos em `/admin/`. Apenas conteúdo publicado aparece no catálogo. O comando `seed_demo` adiciona exemplos sem substituir cursos existentes. O conteúdo inicial é demonstrativo e deve ser editado antes de usar em produção.

Os alunos podem criar uma conta, entrar e guardar aulas concluídas no servidor para consultar noutros dispositivos. Sem sessão, o progresso fica apenas no navegador e não é importado automaticamente para uma conta. SQLite é utilizado para desenvolvimento; a configuração fornecida não está pronta para produção. Recuperação de palavra-passe e verificação de email ainda não estão implementadas. Os administradores podem associar exercícios em Python, JavaScript, Java, C# ou Ruby às aulas e preencher versões de enunciado em português e inglês. Os alunos podem editar código e alternar entre enunciados em português e inglês, quando disponíveis. Rascunhos são guardados apenas no navegador e não são sincronizados; contas diferentes usam rascunhos separados. O seletor PT/EN traduz a interface principal no navegador; cursos e aulas não são traduzidos automaticamente e alguns textos de validação da conta continuam na língua do servidor. A preferência é guardada neste navegador. O Lab inclui uma integração experimental com um executor externo, desativada por defeito.

A direção técnica está descrita em [docs/arquitetura.md](docs/arquitetura.md).

## Executor do Lab (experimental)

A aplicação nunca executa código de alunos diretamente. A integração requer um serviço Judge0 separado, controlado pelo operador, com isolamento forte, autenticação, rede desativada, limites de recursos e proteção contra abuso. **Não está configurado neste ambiente e não foi testado com um executor real.** Não ativar em produção antes de rever e testar o isolamento, versões/IDs de linguagens e políticas de segurança.

Para um ambiente controlado, configurar `LAB_RUNNER_ENABLED=1`, `LAB_RUNNER_URL=https://...` e `LAB_RUNNER_TOKEN` no servidor. O endpoint Judge0 tem de suportar `wait=true`, aceitar o token em `X-Auth-Token` e suportar os IDs de linguagem 71, 63, 62, 51 e 72 para Python, JavaScript, Java, C# e Ruby, respetivamente. Os IDs dependem da instalação e precisam de ser verificados. A aplicação solicita limites e bloqueio de rede; é o executor, não Django, que os deve impor. Necessita de proteção de tráfego na infraestrutura, cache partilhada e atómica para o limite de utilização e supervisão antes do lançamento.

No painel administrativo, o campo **testes privados** aceita JSON com até três objetos, por exemplo `[{34}]` (ver formato abaixo). Apenas são devolvidas contagens de testes aprovados, não os testes nem a saída. Só alunos autenticados podem submeter.

```json
[{"stdin": "", "expected_stdout": "Olá, Ondjango!\n"}]
```

O comando de demonstração adiciona um teste privado para instalações novas; não altera exercícios existentes.
