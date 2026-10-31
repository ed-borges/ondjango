# Judge0 com Docker — referência para testes isolados

**Não é uma implantação pronta para produção nem uma sandbox comprovadamente segura.** Esta configuração é baseada na [configuração upstream do Judge0 CE v1.13.1](https://github.com/judge0/judge0/blob/v1.13.1/docker-compose.yml) e na [release v1.13.1](https://github.com/judge0/judge0/releases/tag/v1.13.1). Não foi executada neste ambiente: não temos Docker, acesso ao Docker Hub nem um servidor Judge0. O funcionamento das imagens, versões, configurações e linguagens tem de ser verificado no servidor de teste.

## Aviso de segurança

O upstream utiliza **contentores privilegiados** para o servidor e os workers. Uma fuga pode comprometer o host; Docker, por si só, não é uma fronteira de segurança suficiente. Usar apenas numa **VM Linux dedicada, descartável, isolada de Django, dados de alunos, segredos de produção e redes internas**. Não aceitar código de alunos antes de uma revisão independente e testes de isolamento. A imagem 1.13.1 é uma referência fixa, não uma garantia de estar livre de vulnerabilidades; verificar advisories, origem e digests de todas as imagens antes de usar. O upstream descreve requisitos específicos de Linux/cgroups na release: validar com o responsável da VM antes de alterar kernel ou GRUB.

O ficheiro expõe a API apenas em `127.0.0.1:2358`, não publica Redis ou PostgreSQL e ativa autenticação. As opções desativam rede dos programas por configuração e funcionalidades como callbacks e ficheiros adicionais. Estes valores são **intenções, não provas**: confirmar na versão executada, incluindo teste real de bloqueio de rede e fuga de sandbox. Para a integração do Django, será necessário um canal privado com TLS e controlo de origem configurados separadamente; este repositório **não configura um proxy TLS ou firewall**.

A configuração gera segredos locais. O upstream escreve variáveis de ambiente em `/api/environment` e pode imprimi-las na inicialização: este Compose desativa os logs dos serviços para reduzir exposição acidental, sacrificando observabilidade. Os segredos também podem ser vistos por administradores Docker e existir dentro dos contentores. Nunca partilhar logs, inspeções, configurações ou dumps sem análise; criar uma estratégia segura de segredos e observabilidade antes de produção. A base de dados pode guardar código e dados submetidos; tratar os volumes como sensíveis.

## Preparar numa VM de teste

1. Instalar Docker Engine, Docker Compose plugin e Python 3 na VM dedicada. Validar acesso ao registo das imagens, integridade, advisories e compatibilidade com a versão de Linux e cgroups. Não executar no computador/servidor da aplicação.
2. Copiar a pasta `infra/judge0` para a VM. No diretório, gerar os segredos **localmente**, sem os enviar por chat nem os guardar no Git:

   ```sh
   python3 manage_config.py create
   python3 manage_config.py check
   ```

   O ficheiro `judge0.conf` é criado com permissões `0600`; o comando recusa substituí-lo. Restringir também acesso ao diretório e backups. Guardar segredos através de um gestor apropriado. `check` valida apenas alguns valores e permissões: não é uma auditoria de segurança.
3. Rever cuidadosamente os ficheiros. O wrapper impede arranque quando a verificação básica falha e limpa variáveis de ambiente que poderiam substituir as credenciais de PostgreSQL/Redis. Verificar a sintaxe sem imprimir o Compose resolvido, que contém segredos:

   ```sh
   ./compose.sh config --quiet
   ```

4. Só depois da revisão e **apenas para testes controlados**, iniciar serviços em segundo plano:

   ```sh
   ./compose.sh up -d db redis
   ./compose.sh up -d
   ./compose.sh ps
   ```

   A ordem não garante que a base esteja pronta: verificar o estado de saúde por meios protegidos e consultar a documentação upstream. Os logs estão desativados; preparar observabilidade segura separadamente. Não executar `docker compose config` sem `--quiet`, nem partilhar o resultado de `docker inspect`.
5. Na VM, executar `python3 smoke_test.py --confirm-vm` para verificar autenticação e os cinco runtimes com programas fixos. Consultar o [guia de teste local](../../docs/teste-local-fase2.md). Confirmar também que a porta não é acessível a partir de outras máquinas e testar limites e bloqueio de rede de forma independente. O smoke test não comprova segurança. Fazer testes apenas com código controlado e sem dados reais.
6. Configurar um **proxy privado com TLS válido** e firewall/controlo de origem. No ambiente Django de teste, usar `LAB_RUNNER_ENABLED=1`, `LAB_RUNNER_URL` com a URL HTTPS privada e `LAB_RUNNER_TOKEN` com o mesmo valor de `AUTHN_TOKEN`, injetado por um gestor de segredos. Confirmar os IDs e versões reais das cinco linguagens e configurar `LAB_LANGUAGE_IDS`. Não colocar tokens em ficheiros versionados, URLs ou conversas.
7. Depois de aprovação do isolamento, executar na aplicação `python manage.py verify_lab --confirm-isolated`. Usa cinco programas fixos; verifica conectividade/runtimes **não** segurança. Falhas podem resultar de IDs, versões, limites ou incompatibilidade de `wait=true`.

Parar o ambiente de teste com `./compose.sh down`. Este comando preserva o volume PostgreSQL; a sua eliminação é uma operação destrutiva e deve seguir a política de retenção/backups. Não executar testes de código não confiável nem ativar o Lab para alunos até cumprir [`docs/aceitacao-fase-2.md`](../../docs/aceitacao-fase-2.md).
