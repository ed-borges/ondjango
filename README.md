# Ondjango

Protótipo de uma plataforma de aprendizagem online para Angola, agora servido por Django.

## Executar localmente

Requisitos: Python 3.10 ou superior.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_python_track  # opcional: cria a trilha piloto em PT/EN
python manage.py translate_python_track  # opcional: traduz conteúdos piloto existentes e não editados
python manage.py seed_demo  # opcional: adiciona cursos de demonstração
python manage.py seed_lab_demo  # opcional: adiciona um exercício demonstrativo
python manage.py createsuperuser  # opcional: acesso ao painel administrativo
python manage.py runserver
```

Abre http://127.0.0.1:8000/. Para testar: `python manage.py test`.

## Estado atual

Cursos e aulas são guardados na base de dados e geridos em `/admin/`. Apenas conteúdo publicado aparece no catálogo. O comando `seed_demo` adiciona exemplos sem substituir cursos existentes. O conteúdo inicial é demonstrativo e deve ser editado antes de usar em produção.

Os alunos podem criar uma conta, entrar e guardar aulas concluídas no servidor para consultar noutros dispositivos. Sem sessão, o progresso fica apenas no navegador e não é importado automaticamente para uma conta. SQLite é utilizado para desenvolvimento; a configuração fornecida não está pronta para produção. Recuperação de palavra-passe e verificação de email ainda não estão implementadas. Os administradores podem associar exercícios em Python, JavaScript, Java, C# ou Ruby às aulas e preencher versões de enunciado em português e inglês. Os alunos podem editar código e alternar entre enunciados em português e inglês, quando disponíveis. Rascunhos são guardados apenas no navegador e não são sincronizados; contas diferentes usam rascunhos separados. O seletor PT/EN traduz a interface principal no navegador. Cursos, aulas e trilhas podem ter traduções inglesas geridas no admin; quando não existem, a aula é apresentada em português com aviso. A tradução da interface ainda requer revisão manual. A preferência é guardada neste navegador. O Lab inclui uma integração experimental com um executor externo, desativada por defeito.

A [trilha piloto de Python](docs/trilha-python.md) cobre básico, intermédio e avançado e pode ser aberta em “Trilhas de aprendizagem”. Administradores podem gerir trilhas e ordenar os seus cursos no painel.

Consulta a [lista de aceitação da fase 1](docs/aceitacao-fase-1.md), o [plano de desenvolvimento por fases](docs/plano-de-desenvolvimento.md) e a [direção técnica](docs/arquitetura.md).

## Videoaulas

Um autor com acesso ao painel administrativo pode abrir **Aulas**, criar ou editar uma aula e preencher o campo opcional **link da videoaula**. São aceites links HTTPS normais do YouTube e Vimeo e links diretos HTTPS para ficheiros MP4 ou WebM. A aula e o curso precisam estar publicados para o aluno os ver. O texto continua obrigatório.

O vídeo só é carregado quando o aluno seleciona “Carregar vídeo”, permitindo-lhe escolher se quer usar dados móveis. A reprodução depende da disponibilidade do alojamento, das permissões de incorporação e do acesso do aluno; o operador deve confirmar os direitos de utilização. Links privados/protegidos por palavra-passe e links Vimeo não listados com parâmetros de acesso não são suportados. O URL direto e os seus parâmetros ficam visíveis aos alunos: não incluir segredos. Os provedores externos recebem dados de acesso quando o vídeo é carregado.

### Área de autor e upload (desenvolvimento)

Um administrador pode conceder a um utilizador a permissão **“Pode criar e gerir os próprios cursos”** no painel de utilizadores do Django. Sem esta permissão o utilizador não acede à área de autor. Não é necessário atribuir acesso ao admin: autores normais não devem receber permissões administrativas ou `is_staff`. Administradores mantêm os privilégios amplos do Django admin. Cursos antigos não têm autor atribuído automaticamente; um administrador pode atribuí-los editando o curso no admin.

O autor autenticado encontra **Área do autor** no menu e pode criar/editar os seus próprios cursos e aulas, publicar ou despublicar, adicionar um link de vídeo ou enviar um ficheiro MP4/WebM até 100 MB. O mesmo campo não aceita link e ficheiro ao mesmo tempo. O autor pode também criar e editar exercícios nas suas aulas, incluindo enunciados PT/EN e testes privados. O painel dispõe de seleção PT/EN, mas a tradução e acessibilidade ainda precisam de revisão no navegador. A eliminação de cursos e revisão editorial não estão implementadas. Publicar disponibiliza imediatamente o conteúdo.

Os ficheiros são guardados localmente em `private_videos/` (fora de ficheiros estáticos e ignorado pelo Git). São servidos pela aplicação apenas para aulas e cursos publicados ou ao autor do rascunho; a ligação externa, por sua vez, depende das permissões do fornecedor. Substituir/remover um vídeo ou eliminar a aula agenda a remoção do ficheiro após a transação ser confirmada.

**Não está pronto para produção.** A validação verifica apenas tamanho, extensão e assinatura inicial; não garante que o ficheiro seja seguro ou reproduzível. O limite é aplicado após a receção do upload: um proxy deve impor limites antes do Django. Antes do lançamento, configurar armazenamento privado persistente, proteção de conteúdo, análise de ficheiros, quotas, limites de tráfego, transcodificação, backups, limpeza de ficheiros órfãos e entrega eficiente de vídeo. Os ficheiros locais podem ser perdidos entre ambientes ou implantações.

## Executor do Lab (experimental)

A aplicação nunca executa código de alunos diretamente. A integração requer um serviço Judge0 separado, controlado pelo operador, com isolamento forte, autenticação, rede desativada, limites de recursos e proteção contra abuso. **Não está configurado neste ambiente e não foi testado com um executor real.** Não ativar em produção antes de rever e testar o isolamento, versões/IDs de linguagens e políticas de segurança.

Para um ambiente controlado, configurar `LAB_RUNNER_ENABLED=1`, `LAB_RUNNER_URL=https://...` e `LAB_RUNNER_TOKEN` no servidor. O endpoint Judge0 tem de suportar `wait=true`, aceitar o token em `X-Auth-Token` e suportar os IDs de linguagem 71, 63, 62, 51 e 72 para Python, JavaScript, Java, C# e Ruby, respetivamente. Os IDs dependem da instalação e precisam de ser verificados. A aplicação solicita limites e bloqueio de rede; é o executor, não Django, que os deve impor. Necessita de proteção de tráfego na infraestrutura, cache partilhada e atómica para o limite de utilização e supervisão antes do lançamento.

No painel administrativo, o campo **testes privados** aceita JSON com até três objetos, com as chaves `stdin` e `expected_stdout` (ver formato abaixo). Apenas são devolvidas contagens de testes aprovados, não os testes nem a saída. Só alunos autenticados podem submeter.

```json
[{"stdin": "", "expected_stdout": "Olá, Ondjango!\n"}]
```

O comando de demonstração adiciona um teste privado para instalações novas; não altera exercícios existentes.
