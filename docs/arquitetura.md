# Ondjango — direção técnica

## Decisão

A plataforma será desenvolvida em Python com Django. Começamos com uma aplicação monolítica para reduzir a complexidade operacional da equipa. O Django serve o protótipo visual existente; a sua interface ainda usa JavaScript no navegador.

## Estado atual

Cursos e aulas são guardados na base de dados e geridos no painel administrativo. Apenas conteúdo publicado é disponibilizado no catálogo. O comando `seed_demo` cria conteúdo de demonstração opcional. O registo e a autenticação usam Django; o progresso de alunos autenticados é guardado por aula e por conta. Sem sessão, o progresso é local e não é transferido automaticamente para a conta. SQLite está configurado para desenvolvimento.

## Próximas etapas propostas

1. Evoluir a gestão de cursos e aulas, com conteúdo real e editor adequado.
2. Reforçar as contas com recuperação de palavra-passe, verificação de email e controlos contra abuso antes do lançamento.
3. Evoluir a experiência de progresso e avaliar a importação explícita do progresso local.
4. PostgreSQL, armazenamento de ficheiros, HTTPS, backups e configuração segura antes da implantação.
5. Definir conteúdos, vídeo, exercícios, pagamentos e certificados de acordo com as prioridades do produto.

A interface suporta português e inglês, com português como idioma inicial. Cursos, aulas, trilhas e exercícios suportam traduções inglesas opcionais; quando ausentes, o conteúdo recorre ao português, com aviso na aula. A interface e as traduções precisam de validação manual. Para Angola, priorizar uma interface responsiva e baixo consumo de dados em ligações móveis. As opções de pagamento e requisitos legais devem ser validados antes do lançamento.

## Laboratório de exercícios multilinguagem

O laboratório deve ligar exercícios a aulas e suportar várias linguagens de programação, com editor, execução, testes e resultados claros. As linguagens iniciais escolhidas são Python, JavaScript, Java, C# e Ruby. Os tipos de exercício e as versões de cada linguagem ainda serão definidos. Os administradores podem criar exercícios associados às aulas nas cinco linguagens, com enunciados em português e inglês opcionais. Apenas exercícios publicados em aulas e cursos publicados aparecem no catálogo, com seleção de idioma do enunciado quando a tradução existe. O editor guarda rascunhos apenas no navegador, separados por conta ou visitante; não há sincronização de rascunhos. Testes privados nunca são devolvidos na API pública. A página Lab é uma pré-visualização. O editor tem integração experimental com um serviço Judge0 externo, mas o executor está desativado por defeito e não existe serviço configurado ou validado neste ambiente.

Código submetido por alunos não deve ser executado no processo Django ou diretamente no servidor da aplicação. Antes de disponibilizar execução, escolher e testar um serviço de execução isolado, com isolamento forte por execução, limites de tempo, CPU, memória, processos e saída, bloqueio de rede por padrão, limpeza dos ambientes, autenticação, limites de utilização e monitorização. Testes privados não devem ser expostos ao aluno. Considerar custos, latência e ligações móveis em Angola.

### Ordem proposta de implementação

1. Internacionalização da interface em português e inglês, com seletor de idioma e persistência da preferência.
2. Evoluir os modelos de exercícios existentes para apresentar as traduções e manter os testes privados no servidor.
3. Escolha e integração de um executor isolado para as cinco linguagens, com limites e testes de segurança.
4. Editor, submissão de soluções, visualização de resultados e histórico de tentativas.

Existe um seletor PT/EN para a interface principal e conteúdo traduzível, com preferência neste navegador. A trilha piloto inclui traduções que precisam de revisão; outros cursos podem ainda não estar traduzidos. O adaptador de execução e avaliação está implementado, mas depende de um Judge0 externo, configurado e verificado pelo operador. Os testes automatizados usam simulação: as cinco linguagens ainda não foram validadas num executor real.

## Videoaulas

A área de autor exige a permissão `learning.can_author` e limita a edição aos cursos pertencentes ao utilizador. Administradores mantêm acesso amplo através do admin; não conceder privilégios de administrador a autores normais. O autor pode associar uma URL externa ou enviar MP4/WebM até 100 MB. Ficheiros são armazenados localmente em diretório privado e servidos pela aplicação apenas para aulas e cursos publicados ou ao autor do rascunho. O aluno decide quando carregar. Links privados e parâmetros de acesso do Vimeo não são suportados. A verificação de upload é superficial e o armazenamento local é apenas para desenvolvimento; proteção, quotas, análise, backups e alojamento persistente são necessários antes de produção. Verificar disponibilidade, incorporação, direitos e privacidade antes de publicar.
