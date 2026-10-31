# Ondjango — direção técnica

## Decisão

A plataforma será desenvolvida em Python com Django. Começamos com uma aplicação monolítica para reduzir a complexidade operacional da equipa. O Django serve o protótipo visual existente; a sua interface ainda usa JavaScript no navegador.

## Estado atual

O catálogo e as aulas são dados de demonstração no JavaScript e o progresso é local ao navegador. SQLite está configurado para desenvolvimento. Ainda não existe uma implementação de contas de aluno, conteúdo ou progresso persistidos no servidor.

## Próximas etapas propostas

1. Modelos de cursos e aulas no Django e gestão de conteúdo no painel administrativo.
2. Contas de aluno e início de sessão, com testes de segurança.
3. Progresso persistido na base de dados, associado a cada aluno.
4. PostgreSQL, armazenamento de ficheiros, HTTPS, backups e configuração segura antes da implantação.
5. Definir conteúdos, vídeo, exercícios, pagamentos e certificados de acordo com as prioridades do produto.

Para Angola, priorizar português, interface responsiva e baixo consumo de dados em ligações móveis. As opções de pagamento e requisitos legais devem ser validados antes do lançamento.
