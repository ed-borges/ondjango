# Trilha piloto: Python do básico ao avançado

Uma primeira versão em português e inglês, organizada em três cursos no catálogo e numa página de trilha. A ordem recomendada é básico → intermédio → avançado; a plataforma ainda não impõe pré-requisitos. Cada curso contém quatro aulas textuais e um exercício por aula. Os enunciados, exemplos e testes são um ponto de partida para revisão pedagógica, não uma formação exaustiva.

| Nível | Aulas | Competências praticadas |
| --- | --- | --- |
| Básico | Saída; variáveis e entrada; condições; ciclos | Escrever instruções, ler inteiros, tomar decisões e acumular valores. |
| Intermédio | Listas; dicionários; funções; exceções | Processar coleções, contar ocorrências, reutilizar lógica e tratar erros. |
| Avançado | Geradores; JSON; datas; Decimal | Produzir sequências iterativamente e trabalhar com dados estruturados, intervalos e precisão decimal. |

## Como disponibilizar

Depois das migrações, executar `python manage.py seed_python_track`. O comando cria e publica cada curso que ainda não existe, incluindo aulas e exercícios, e cria a trilha se ainda não existir; nunca substitui cursos ou trilhas existentes. Para alterar conteúdos depois da criação, utilizar o painel administrativo. Novos cursos incluem versões em português e inglês. Para instalações onde os cursos já existiam, executar `python manage.py translate_python_track`; o comando só preenche traduções vazias quando os conteúdos originais ainda correspondem aos dados de origem e nunca substitui edições. As duas versões precisam de revisão pedagógica antes do lançamento.

O aluno pode ler as aulas e editar exercícios. **A execução e avaliação automática continuam indisponíveis até um serviço de execução isolado ser configurado e validado.** Os testes privados são guardados no servidor e não são enviados ao catálogo público. A conclusão de aulas ainda é manual e não exige aprovação no exercício.

## Próximos passos pedagógicos

Rever a sequência e os exercícios com utilizadores reais, ampliar explicações e projetos, rever os conteúdos em português e inglês e validar todos os exercícios no executor real antes de os usar numa avaliação. A página da trilha apresenta os níveis em ordem e soma as aulas concluídas, mas não oferece desbloqueio sequencial, certificados ou conclusão automática. O progresso das aulas é manual; não depende da execução dos exercícios.
