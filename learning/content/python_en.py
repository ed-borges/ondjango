"""English translations for the Python pilot track, in the original lesson order."""

TRANSLATIONS = {
    'python-basico': {
        'title': 'Python: beginner level',
        'description': 'Start from scratch with output, variables, decisions and loops in Python.',
        'lessons': [
            ('Getting started and text output', '''Goal: understand what a program is and write your first Python instruction.

A program is a sequence of instructions. Python reads those instructions and produces a result. The print function writes text to the output:

print("Olá, Ondjango!")

Quotation marks delimit a string. Python is case-sensitive: print and Print are different. By default, print ends the line with a newline.

Try changing the text inside the quotation marks. In the exercise, follow the requested punctuation and spaces exactly. The Lab can evaluate your solution when an isolated runner is available.''', 'A greeting', 'Write a program that prints exactly Olá, Ondjango! on one line. You do not need to read input.'),
            ('Variables, input and numbers', '''Goal: receive values and perform integer arithmetic.

A variable associates a name with a value: age = 20. input() reads a line of text. To do integer arithmetic, convert the text with int():

a = int(input())
b = int(input())
print(a + b)

int("12") produces the number 12; without conversion, "1" + "2" produces the text "12". Use clear names and avoid additional input prompts in automatically evaluated exercises: tests compare the expected output.''', 'Add two numbers', 'Read two integers, one per line, and print their sum on one line. For example, 4 and 7 produce 11.'),
            ('Decisions with if and else', '''Goal: choose an action based on a condition.

A condition compares values and evaluates to True or False. In Python, indentation identifies the block:

number = int(input())
if number > 0:
    print("positive")
else:
    print("not positive")

The % operator returns the remainder. An integer is even when number % 2 == 0. The == operator compares values; a single = assigns a value. Test zero and negative numbers too.''', 'Even or odd', 'Read an integer. Print exactly par if it is even or impar if it is odd, lowercase and without an accent.'),
            ('Repeating with loops', '''Goal: repeat operations and accumulate results.

A for loop iterates over a sequence. range(1, n + 1) generates integers from 1 through n; the second limit is exclusive.

total = 0
for number in range(1, 4):
    total += number
print(total)  # 6

The accumulator starts at zero and is updated on each iteration. When n is zero, range(1, 1) is empty and the total remains zero. Incorrect indentation changes a block or causes an error.''', 'Sum from 1 to N', 'Read an integer N between 0 and 1000. Print the sum of integers from 1 through N inclusive. For N equal to 0, print 0.'),
        ],
    },
    'python-intermedio': {
        'title': 'Python: intermediate level', 'description': 'Explore lists, dictionaries, functions and error handling.',
        'lessons': [
            ('Lists and data processing', '''Goal: transform and iterate over a collection of values.

A list stores elements in order. Convert a line of space-separated integers with:

values = list(map(int, input().split()))
print(sum(values))

split() separates a line on whitespace; map applies int to each part; list materialises the values. You can also iterate with for and add elements using append. Consider empty lists when allowed and use len to count elements.''', 'Count positive values', 'Read a line of space-separated integers; the line may be empty. Print how many values are greater than zero.'),
            ('Dictionaries and counting', '''Goal: associate keys with values and count occurrences.

A dictionary lets you look up a value by key:

counts = {}
for word in ["sun", "rain", "sun"]:
    counts[word] = counts.get(word, 0) + 1
print(counts["sun"])  # 2

get(key, 0) returns zero when the key does not exist. Normalising text with lower() makes case-insensitive comparisons easier. Decide whether whitespace, punctuation and accents are part of the data, following the exercise rules.''', 'Count words', 'Read a line of space-separated words and a second line containing a word. Count occurrences of that word in the first line, ignoring case. Print only the number.'),
            ('Functions, parameters and return values', '''Goal: divide a program into reusable operations.

A function receives arguments and can return a value:

def double(value):
    return value * 2

result = double(3)
print(result)

return does not print: it provides a result to the caller. Separating computation from input/output makes code easier to test. A function can receive two parameters and choose a result with if. Consider equal values too.''', 'The larger of two values', 'Define a function maior(a, b) that returns the larger of two integers. Read two integers, one per line, and print the returned value.'),
            ('Errors and exceptions', '''Goal: handle a conversion that may fail.

When int receives text that does not represent an integer, it raises ValueError. Handle only that error with try and except:

try:
    number = int(input())
    print(number)
except ValueError:
    print("invalid")

Avoid a bare except: it may hide other problems. The else block can hold code for the successful case; finally is used for cleanup regardless of the outcome.''', 'Safe conversion', 'Read one line. If int() accepts it as an integer, print the integer multiplied by 2. Otherwise print exactly invalido, without an accent.'),
        ],
    },
    'python-avancado': {
        'title': 'Python: advanced level', 'description': 'Practice generators, JSON, dates and decimal arithmetic through concrete examples.',
        'lessons': [
            ('Generators and iterative processing', '''Goal: produce values gradually without building a whole list.

A function containing yield is a generator function. Each iteration asks for the next value:

def even_numbers(limit):
    for n in range(limit + 1):
        if n % 2 == 0:
            yield n

for value in even_numbers(4):
    print(value)

Generators are useful for large sequences because they produce items on demand. They are iterators: once consumed, they do not automatically return to the beginning.''', 'Sum even squares', 'Define a generator function quadrados_pares(n) that yields the squares of even integers from 1 through n inclusive. Read n between 0 and 1000 and print the sum of the yielded values.'),
            ('Structured data with JSON', '''Goal: read JSON data and access values safely.

JSON is a data exchange format. The json module turns a JSON string into a Python structure:

import json
data = json.loads('{"name": "Ana", "points": 3}')
print(data["name"])

JSON objects become dictionaries and JSON arrays become lists. The get method provides a default for missing keys. Do not use eval to interpret JSON: it executes Python expressions and is not a safe data parser.''', 'A person’s points', 'Read one line containing a valid JSON object. The key pontos, if present, contains an integer. Print the value of pontos; if the key is absent, print 0.'),
            ('Dates and intervals', '''Goal: convert dates and calculate intervals in days.

The datetime module works with dates without manually calculating months and years:

from datetime import date
start = date.fromisoformat("2024-02-28")
end = date.fromisoformat("2024-03-01")
print((end - start).days)  # 2

fromisoformat accepts YYYY-MM-DD dates. Subtracting dates produces a timedelta whose days attribute gives the number of days. The difference can be negative when the second date is earlier.''', 'Days between dates', 'Read two valid dates in YYYY-MM-DD format, one per line. Print the difference in days: the second date minus the first.'),
            ('Decimal precision and rounding', '''Goal: calculate decimal values without relying on the binary representation of float.

For monetary amounts, Decimal is often more suitable than float. Construct values from text to avoid introducing a binary approximation:

from decimal import Decimal, ROUND_HALF_UP
value = Decimal("12.345")
print(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

quantize fixes the number of decimal places and rounding rule. Applications may require different rules; specify one explicitly before calculating. Keeping precision in stored values and formatting for display helps avoid accumulated errors.''', 'Rounded total', 'Read two non-negative decimal values, one per line. Add them using Decimal and print the result with exactly two decimal places, using ROUND_HALF_UP.'),
        ],
    },
}
