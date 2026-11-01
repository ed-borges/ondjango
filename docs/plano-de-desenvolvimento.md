# Plano de desenvolvimento da Ondjango

Plano inicial para uma equipa de duas pessoas. As fases são propostas e podem ser ajustadas antes de cada início; não são estimativas de prazo. Cada fase só passa a concluída depois dos critérios de aceitação serem verificados.

## Situação atual

- **Existente, mas ainda em evolução:** catálogo e aulas no Django, administração, registo e início de sessão, progresso de alunos, tema escuro e interface PT/EN parcialmente traduzida.
- **Lab:** modelos de exercícios, editor e rascunhos locais, e adaptador experimental Judge0. Não existe executor real configurado ou validado; não está pronto para uso público.
- **Ainda não pronto para produção:** segurança e recuperação de contas, configurações de implantação, backups, conteúdos reais, traduções completas e testes de ponta a ponta.

## Fase 1 — Fundamentos e autoria de conteúdo

**Estado: implementação em revisão; aprovação pendente.** Consultar a [lista de aceitação](aceitacao-fase-1.md) antes de marcar a fase como concluída.

**Objetivo:** permitir que a equipa prepare e verifique um primeiro curso real, sem depender do Lab em produção.

- Melhorar a gestão de cursos, aulas e exercícios no Django admin, incluindo validação dos testes privados.
- Rever registo, início de sessão e progresso, e acrescentar cobertura para erros e segurança.
- Completar tradução da interface PT/EN e definir como armazenar traduções reais de cursos e aulas.
- Rever e ampliar a [trilha piloto de Python](trilha-python.md), incluindo qualidade pedagógica, direitos de utilização e tradução.

**Critérios de conclusão:** administrador consegue criar, rever e publicar um curso com aulas e exercícios; aluno consegue aceder às aulas e retomar progresso; interface e mensagens essenciais estão verificadas em PT/EN; testes passam. A execução continua desligada até à fase 2.

**Entregue:** gestão e validação de conteúdo, área de autor para cursos, aulas, exercícios e videoaulas, trilha piloto PT/EN, progresso e testes automatizados. Continuam pendentes a validação manual dos fluxos e a revisão pedagógica e de direitos do conteúdo. O executor permanece desligado.

## Fase 2 — Lab seguro e multilinguagem

**Estado: iniciada; executor real e verificação de segurança pendentes.** Ver [aceitação da fase 2](aceitacao-fase-2.md).

**Objetivo:** permitir testar exercícios num serviço de execução isolado e controlado.

- Escolher, implementar e operar uma sandbox externa isolada, com rede bloqueada por padrão e limites de tempo, CPU, memória, processos e saída. Verificar estes controlos independentemente da aplicação.
- Integrar, testar de ponta a ponta e validar versões e IDs de Python, JavaScript, Java, C# e Ruby. Preparar a integração segura de algoritmos com Compalg ([análise](compalg.md)); a execução ainda não está implementada. Não assumir que IDs de uma instalação servem para outra.
- Proteger contra abuso com autenticação, limites de utilização partilhados, observabilidade, retenção adequada e testes de segurança; garantir que testes privados não são expostos.
- Melhorar resultados e decidir se tentativas e rascunhos serão sincronizados. Definir custos e política de utilização.

**Critérios de conclusão:** as cinco linguagens executam exercícios reais e testes aprovados/reprovados num ambiente isolado; testes de segurança e de ponta a ponta passam; falhas e limites são tratados; operação e custos são conhecidos. Só então ativar para alunos.

## Fase 3 — Preparação para lançamento piloto

**Objetivo:** publicar uma versão limitada, segura e recuperável.

- Configurar PostgreSQL, alojamento, HTTPS, segredos, armazenamento de ficheiros, monitorização e backups com recuperação testada.
- Implementar recuperação de palavra-passe e verificação de email, proteção contra abuso e revisão de privacidade e obrigações legais.
- Testar acessibilidade, telemóveis, ligações lentas e fluxos PT/EN; publicar conteúdos reais revistos.

**Critérios de conclusão:** verificação de implantação e segurança concluída, recuperação de backup testada, fluxos críticos testados e piloto aprovado. Não tratar as configurações locais de desenvolvimento como produção.

## Fase 4 — Evolução após o piloto

Recolher feedback e priorizar histórico de tentativas, certificados, vídeo, pagamentos locais e outras funcionalidades. Validar necessidades, custos, segurança e requisitos legais antes de implementar.

## Forma de trabalho

Para cada incremento: definir alcance e critérios de aceitação; implementar e testar; demonstrar; registar limitações e decidir a próxima tarefa. Atualizar este documento quando o alcance mudar.
