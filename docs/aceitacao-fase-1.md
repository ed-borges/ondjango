# Fase 1 — validação de aceitação

Estado: **implementação em revisão; ainda não aprovada como concluída**. Esta lista separa verificações automatizadas de revisões humanas que ainda precisam de acontecer.

## Verificado por testes automatizados

- Publicação e ocultação de cursos, aulas, exercícios e trilhas; campos PT/EN disponíveis no catálogo.
- Registo, início e fim de sessão; isolamento de progresso por utilizador e consulta numa segunda sessão; proteção CSRF nos pedidos de progresso.
- Validação de testes privados no admin e ausência destes dados no catálogo público.
- Trilha de Python com três níveis, doze aulas e doze exercícios; casos de teste comparados com soluções de referência confiáveis. O processo de criação e o de tradução preservam alterações existentes.
- Resposta do servidor para validação de palavra-passe em PT e EN.

Estes testes não substituem testes no navegador, revisão de conteúdo ou validação do executor real. O processo do servidor não executa código submetido por alunos nos testes da fase 1.

## Revisões manuais pendentes

1. Com cursos semeados, abrir a trilha em telemóvel e computador; verificar ordem, progresso, navegação, contraste e estados vazios.
2. Criar conta, iniciar sessão, concluir uma aula e confirmar o progresso numa sessão noutro dispositivo. Verificar também as mensagens de erro de autenticação e o regresso à aplicação após sair.
3. Alternar PT/EN nas páginas principais e de conta; conferir enunciados, avisos e valores acessíveis. O conteúdo sem tradução inglesa regressa ao português e apresenta aviso na aula.
4. Rever pedagogicamente as 12 aulas e exercícios, as duas línguas e a adequação ao público angolano; confirmar direitos de utilização e aprovar o conteúdo para publicação.
5. Confirmar que o Lab é apresentado como indisponível quando o executor está desativado e que não é possível avaliar exercícios nesse estado.

Registar os resultados e eventuais correções antes de assinalar a fase como concluída. Recuperação de palavra-passe, verificação de email e a preparação de produção pertencem à fase 3; o executor seguro é da fase 2.
