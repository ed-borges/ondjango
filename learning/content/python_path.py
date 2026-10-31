"""Portuguese-language pilot curriculum; tests are private stdin/stdout pairs."""

TRACK = [
    {
        'slug': 'python-basico', 'title': 'Python: nível básico', 'level': 'Iniciante', 'color': 'orange',
        'description': 'Começa do zero com saída, variáveis, decisões e ciclos em Python.',
        'lessons': [
            {
                'title': 'Primeiros passos e saída de texto',
                'content': '''Objetivo: compreender o que é um programa e escrever a tua primeira instrução Python.

Um programa é uma sequência de instruções. Python lê essas instruções e produz um resultado. A função print escreve texto na saída:

print("Olá, Ondjango!")

As aspas delimitam uma string (texto). Python diferencia maiúsculas de minúsculas, por isso print e Print não são iguais. Por padrão, print termina a linha com uma mudança de linha.

Experimenta alterar o texto entre aspas. No exercício, respeita exatamente a pontuação e os espaços pedidos. O Lab poderá avaliar a solução quando o executor isolado estiver disponível.''',
                'exercise': ('Uma saudação', 'Escreve um programa que imprima exatamente Olá, Ondjango! numa linha. Não precisas de ler entrada.', '# Escreve o teu código aqui\n', [('', 'Olá, Ondjango!\n')]),
            },
            {
                'title': 'Variáveis, entrada e números',
                'content': '''Objetivo: receber valores e realizar operações com números inteiros.

Uma variável associa um nome a um valor: idade = 20. A função input() lê uma linha de texto. Para efetuar contas inteiras, converte o texto com int():

a = int(input())
b = int(input())
print(a + b)

A conversão int("12") produz o número 12; sem conversão, "1" + "2" produz o texto "12". Usa nomes claros e evita escrever mensagens adicionais ao ler entrada em exercícios automáticos: os testes comparam a saída esperada.''',
                'exercise': ('Somar dois números', 'Lê dois números inteiros, um por linha, e imprime a soma numa única linha. Exemplo: entrada 4 e 7 produz 11.', '# Lê dois inteiros e imprime a soma\n', [('4\n7\n', '11\n'), ('-5\n2\n', '-3\n'), ('0\n0\n', '0\n')]),
            },
            {
                'title': 'Decisões com if e else',
                'content': '''Objetivo: escolher uma ação com base numa condição.

Uma condição compara valores e resulta em True ou False. Em Python, o bloco é identificado pela indentação:

numero = int(input())
if numero > 0:
    print("positivo")
else:
    print("não positivo")

O operador % devolve o resto da divisão. Um inteiro é par quando numero % 2 == 0. O operador == compara valores; um único = atribui um valor a uma variável. Testa também zero e números negativos.''',
                'exercise': ('Par ou ímpar', 'Lê um inteiro. Imprime exatamente par se for par ou impar se for ímpar, sem acento e em minúsculas.', '# Lê um inteiro e determina a sua paridade\n', [('8\n', 'par\n'), ('-3\n', 'impar\n'), ('0\n', 'par\n')]),
            },
            {
                'title': 'Repetição com ciclos',
                'content': '''Objetivo: repetir operações e acumular resultados.

O ciclo for percorre uma sequência. range(1, n + 1) gera inteiros de 1 até n, incluindo n; o segundo limite de range é exclusivo.

soma = 0
for numero in range(1, 4):
    soma += numero
print(soma)  # 6

O acumulador começa em zero e é atualizado a cada passagem. Quando n é zero, range(1, 1) é vazio e a soma continua zero. Indentação incorreta muda o bloco ou causa um erro.''',
                'exercise': ('Soma de 1 até N', 'Lê um inteiro N entre 0 e 1000. Imprime a soma dos inteiros de 1 até N, incluindo N. Para N igual a 0, imprime 0.', '# Usa um ciclo para calcular a soma\n', [('4\n', '10\n'), ('0\n', '0\n'), ('10\n', '55\n')]),
            },
        ],
    },
    {
        'slug': 'python-intermedio', 'title': 'Python: nível intermédio', 'level': 'Intermédio', 'color': 'green',
        'description': 'Aprofunda listas, dicionários, funções e tratamento de erros.',
        'lessons': [
            {
                'title': 'Listas e processamento de dados',
                'content': '''Objetivo: transformar e percorrer uma coleção de valores.

Uma lista guarda elementos numa ordem. Para converter uma linha de inteiros separados por espaços:

valores = list(map(int, input().split()))
print(sum(valores))

split() separa a linha pelos espaços; map aplica int a cada parte; list materializa os valores. Também podes percorrer a lista com for e acrescentar elementos com append. Considera listas vazias quando o enunciado as permitir e usa a função len para contar elementos.''',
                'exercise': ('Contar positivos', 'Lê uma linha com inteiros separados por espaços; a linha pode estar vazia. Imprime quantos desses valores são maiores que zero.', '# Lê a linha e conta os valores positivos\n', [('1 -2 0 4\n', '2\n'), ('\n', '0\n'), ('-1 -9\n', '0\n')]),
            },
            {
                'title': 'Dicionários e contagem',
                'content': '''Objetivo: associar chaves a valores e contar ocorrências.

Um dicionário permite procurar um valor pela chave:

contagem = {}
for palavra in ["sol", "chuva", "sol"]:
    contagem[palavra] = contagem.get(palavra, 0) + 1
print(contagem["sol"])  # 2

get(chave, 0) devolve zero quando a chave ainda não existe. Normalizar texto com lower() facilita comparações sem diferenciar letras maiúsculas. Decide sempre se espaços, pontuação e acentos fazem parte dos dados; segue a regra explícita do exercício.''',
                'exercise': ('Contar palavras', 'Lê uma linha de palavras separadas por espaços e uma segunda linha com uma palavra. Conta as ocorrências dessa palavra na primeira linha, ignorando maiúsculas e minúsculas. Imprime apenas o número.', '# Conta a palavra pedida\n', [('Sol chuva sol\nSOL\n', '2\n'), ('um dois\ntres\n', '0\n'), ('\nola\n', '0\n')]),
            },
            {
                'title': 'Funções, parâmetros e retorno',
                'content': '''Objetivo: dividir um programa em operações reutilizáveis.

Uma função recebe argumentos e pode devolver um valor com return:

def dobro(valor):
    return valor * 2

resultado = dobro(3)
print(resultado)

return não imprime: entrega o resultado a quem chamou a função. Manter cálculo e entrada/saída separados facilita testar o código. Uma função pode receber dois parâmetros e escolher o resultado com if. Identifica o comportamento esperado também quando os valores são iguais.''',
                'exercise': ('O maior de dois valores', 'Define uma função maior(a, b) que devolva o maior dos dois inteiros. Lê dois inteiros, um por linha, e imprime o valor devolvido.', '# Define maior(a, b), lê os valores e imprime o resultado\n', [('5\n2\n', '5\n'), ('-7\n-2\n', '-2\n'), ('3\n3\n', '3\n')]),
            },
            {
                'title': 'Erros e exceções',
                'content': '''Objetivo: lidar com uma conversão que pode falhar.

Quando int recebe texto que não representa um inteiro, lança ValueError. Podes tratar apenas esse erro com try e except:

try:
    numero = int(input())
    print(numero)
except ValueError:
    print("inválido")

Evita except sem especificar a exceção: isso pode esconder outros problemas. O bloco else pode conter código que deve ser executado quando não houve erro; finally serve para limpeza, independentemente do resultado.''',
                'exercise': ('Conversão segura', 'Lê uma linha. Se representar um inteiro aceite por int(), imprime esse inteiro multiplicado por 2. Caso contrário, imprime exatamente invalido, sem acento.', '# Converte a entrada e trata ValueError\n', [('21\n', '42\n'), ('abc\n', 'invalido\n'), ('-2\n', '-4\n')]),
            },
        ],
    },
    {
        'slug': 'python-avancado', 'title': 'Python: nível avançado', 'level': 'Avançado', 'color': 'blue',
        'description': 'Pratica geradores, JSON, datas e cálculos decimais com casos concretos.',
        'lessons': [
            {
                'title': 'Geradores e processamento iterativo',
                'content': '''Objetivo: produzir valores gradualmente sem construir uma lista inteira.

Uma função com yield é uma função geradora. Cada iteração pede o próximo valor:

def pares(limite):
    for n in range(limite + 1):
        if n % 2 == 0:
            yield n

for valor in pares(4):
    print(valor)

Geradores são úteis ao processar sequências grandes, pois produzem elementos conforme necessário. No entanto, são iteradores: depois de consumidos, não regressam automaticamente ao início.''',
                'exercise': ('Somar quadrados pares', 'Define uma função geradora quadrados_pares(n) que produza os quadrados dos inteiros pares de 1 até n, incluindo n. Lê n entre 0 e 1000 e imprime a soma dos valores gerados.', '# Define o gerador e imprime a soma\n', [('6\n', '56\n'), ('1\n', '0\n'), ('4\n', '20\n')]),
            },
            {
                'title': 'Dados estruturados com JSON',
                'content': '''Objetivo: ler dados JSON e aceder a valores com segurança.

JSON é um formato de troca de dados. O módulo json converte uma string JSON numa estrutura Python:

import json
dados = json.loads('{"nome": "Ana", "pontos": 3}')
print(dados["nome"])

Objetos JSON tornam-se dicionários e listas JSON tornam-se listas. O método get permite definir um valor por defeito para chaves ausentes. Não uses eval para interpretar JSON: ele executa expressões Python e não é um analisador seguro de dados.''',
                'exercise': ('Pontos de uma pessoa', 'Lê uma linha contendo um objeto JSON válido. A chave pontos, se existir, contém um inteiro. Imprime o valor de pontos; se a chave não existir, imprime 0.', '# Usa json.loads para ler o objeto\n', [('{"nome":"Ana","pontos":12}\n', '12\n'), ('{"nome":"João"}\n', '0\n'), ('{"pontos":-3}\n', '-3\n')]),
            },
            {
                'title': 'Datas e intervalos',
                'content': '''Objetivo: converter datas e calcular intervalos em dias.

O módulo datetime trabalha com datas sem recorrer a cálculos manuais de meses e anos:

from datetime import date
inicio = date.fromisoformat("2024-02-28")
fim = date.fromisoformat("2024-03-01")
print((fim - inicio).days)  # 2

fromisoformat aceita datas no formato AAAA-MM-DD. Subtrair duas datas produz um timedelta; o atributo days informa o número de dias. A diferença pode ser negativa se a segunda data for anterior à primeira.''',
                'exercise': ('Dias entre datas', 'Lê duas datas válidas no formato AAAA-MM-DD, uma por linha. Imprime a diferença em dias da segunda data menos a primeira.', '# Usa datetime.date para calcular o intervalo\n', [('2024-02-28\n2024-03-01\n', '2\n'), ('2025-01-02\n2025-01-01\n', '-1\n'), ('2026-01-01\n2026-01-01\n', '0\n')]),
            },
            {
                'title': 'Precisão decimal e arredondamento',
                'content': '''Objetivo: calcular valores decimais sem depender da representação binária de float.

Para valores monetários, Decimal é frequentemente mais adequado que float. Constrói o valor a partir de texto para evitar introduzir uma aproximação binária:

from decimal import Decimal, ROUND_HALF_UP
valor = Decimal("12.345")
print(valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

quantize fixa o número de casas decimais e a regra de arredondamento. Diferentes aplicações podem exigir outras regras; define explicitamente a regra antes de calcular. Guardar valores com precisão e formatar na apresentação ajuda a evitar erros acumulados.''',
                'exercise': ('Total arredondado', 'Lê dois valores decimais não negativos, um por linha. Soma-os com Decimal e imprime o resultado com exatamente duas casas decimais, usando ROUND_HALF_UP.', '# Usa Decimal e arredonda a soma com ROUND_HALF_UP\n', [('1.005\n0\n', '1.01\n'), ('2.10\n3.25\n', '5.35\n'), ('0\n0\n', '0.00\n')]),
            },
        ],
    },
]
