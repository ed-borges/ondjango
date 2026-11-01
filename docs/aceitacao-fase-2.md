# Fase 2 — Lab seguro e multilinguagem

**Estado: em desenvolvimento; não pronto para alunos.** A fase 1 mantém a sua própria revisão de aceitação pendente.

## Incremento implementado

- Preparação de exercícios de algoritmos com Compalg, sem execução: ver [análise e etapas pendentes](compalg.md). Compalg não é enviado ao Judge0, mesmo quando este está ligado.
- Adaptador Judge0 externo desativado por defeito; o Django não executa código de alunos.
- Mapeamento configurável e validado dos cinco IDs de linguagem; configuração incompleta mantém o Lab indisponível. É obrigatório verificar IDs e versões no serviço real.
- Limite de frequência por conta partilhado pela base de dados, com atualização condicional atómica; uma chamada reserva um intervalo de 30 segundos mesmo que o executor falhe. Não substitui limites globais, proteção por IP, quotas, verificação de contas ou controlo de concorrência.
- Falhas internas, respostas pendentes e estados desconhecidos do executor são tratados como falhas de serviço, não como testes reprovados. Entradas, saídas, testes privados e código não são devolvidos nos resultados.
- Configuração Docker de referência e preparação de segredos para uma VM isolada: ver [infra/judge0/README.md](../infra/judge0/README.md). Não foi executada nem auditada neste ambiente e utiliza contentores privilegiados.
- Teste local `smoke_test.py --confirm-vm` para programas fixos, com instruções em [teste local](teste-local-fase2.md). O teste foi verificado com respostas simuladas, não com Docker ou Judge0 real.
- Comando opcional `python manage.py verify_lab --confirm-isolated` envia dois testes por linguagem com programas fixos e inofensivos: resposta correta e resposta incorreta, exigindo os estados esperados. **Este comando não prova isolamento ou segurança.** Não deve ser usado até um operador aprovar o ambiente isolado.

Os testes automatizados simulam o executor. Não existe Docker/Podman nem um serviço Judge0 configurado neste ambiente; não foram realizados testes de execução reais, auditoria do isolamento ou testes de carga.

## Antes de ativar o Lab

1. Selecionar e implantar um serviço Judge0 separado, com isolamento forte por execução, autenticação, TLS, rede bloqueada por padrão e limites de tempo, CPU, memória, processos, armazenamento e saída impostos pelo executor.
2. Validar a segurança e os limites de forma independente; testar fuga de isolamento, rede, concorrência, abuso, limpeza e falhas. Não usar o processo Django como sandbox.
3. Confirmar versões e IDs das cinco linguagens na instalação real e configurar `LAB_LANGUAGE_IDS`. Ativar apenas para testes restritos e executar `verify_lab` após aprovação do isolamento.
4. Configurar PostgreSQL e limites globais/por IP e por conta na infraestrutura; adicionar controlo de concorrência, observabilidade, retenção e orçamento. O intervalo por conta não impede múltiplas contas ou execução sobreposta.
5. Validar exercícios de Python e casos de aprovação, erro, compilação e tempo limite para cada linguagem, em sessões reais, sem revelar testes privados. Adicionar histórico ou sincronização apenas após decisão sobre privacidade e retenção.
6. Rever direitos de conteúdo e completar revisão humana pendente da fase 1 antes do piloto.

Só considerar a fase concluída após os cinco runtimes e o suporte Compalg solicitado e os controlos de segurança passarem em infraestrutura real. Não publicar ou aceitar submissões de alunos enquanto isso não estiver comprovado.
