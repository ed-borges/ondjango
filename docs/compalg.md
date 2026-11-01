# Algoritmos com Compalg — preparação

Objetivo: permitir futuramente exercícios de algoritmos com a linguagem do [Compalg](https://github.com/Compalg/compalg), além das cinco linguagens existentes. Este incremento **não executa algoritmos** e não fornece ainda uma sandbox Compalg. Na área de autor já é possível escolher “Algoritmos (Compalg — em preparação)”; os exercícios aparecem no catálogo com o editor, mas sem botão de execução, mesmo quando o Judge0 está configurado. A API rejeita submissões dessa linguagem e não as envia ao Judge0.

## Análise inicial

A análise foi feita ao código upstream no commit `39ee897514943fffb705d9fde306b33500605526` da branch `master` (último push indicado pelo GitHub em fevereiro de 2015). O projeto é Java e usa Ant/NetBeans. O ponto de entrada indicado em `nbproject/project.properties` abre uma interface gráfica Swing; a classe `Portugol.Language.Consola.ConsoleIO` usa `JOptionPane` e `JTextArea` para entrada/saída. Não foi identificado um comando headless pronto para integração; isto não é prova de que não exista outra forma de usar as classes.

O GitHub identifica a licença como GPL-2.0; a licença incluída deve ser analisada na íntegra, juntamente com licenças de dependências e implicações de redistribuição/modificações, antes de copiar ou distribuir componentes. Nenhum código ou exemplo do Compalg foi incorporado neste projeto. Não assumimos que outras variantes de Portugol sejam compatíveis.

## Próximos passos antes da execução

1. Investigar a separação do analisador e interpretador da interface gráfica; desenhar e testar um adaptador headless para entrada e saída determinísticas e erros, sem confiar que `main` ou uma conversão para Java/C sejam seguros.
2. Verificar compatibilidade de compilação e dependências com Java atual, determinar cobertura da linguagem e preparar programas próprios de teste para entrada, saída, erros, ciclos e limites. Analisar licença e vulnerabilidades dos componentes.
3. Executar **análise e execução** apenas num serviço separado com isolamento por submissão, rede desativada, quotas de CPU, memória, processos, disco, tempo e saída, autenticação, TLS e controlo de concorrência. O Django não deve compilar nem executar código de alunos.
4. Validar independentemente isolamento, esgotamento de recursos e falhas; testar testes privados sem fuga de dados e fazer testes reais de ponta a ponta. Só disponibilizar a execução depois desta validação e de uma decisão explícita de ativação.

O Judge0 e a sua VM ainda não foram testados neste ambiente. O Compalg não é um ID padrão do Judge0 identificado nesta análise; não atribuir um ID arbitrário nem declarar suporte até existir um runtime compatível e verificado. A disponibilidade das cinco linguagens continua independente desta preparação.
