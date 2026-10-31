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

Para Angola, priorizar português, interface responsiva e baixo consumo de dados em ligações móveis. As opções de pagamento e requisitos legais devem ser validados antes do lançamento.
