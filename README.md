# JP - Język Programowania

- Radosław Kostrzewski, 310757
- Gitlab: @rkostrze

## Wymagania

- Język obiektowy
- Możliwość rozszerzania języka o nowe typy
- Wszystkie zmienne są nullowalne
- Typowanie dynamiczne i silne
- Obsługa wyjątków
  - Możliwość rzucenia wyjątku
  - Możliwość wyłapania wyjątku
    - Przechwycenie wyjątku bez dostępu do szczegółowych informacji
    - Przechwycenie wyjątku po jednym lub kilku typach z dostępem do szczegółowych informacji
- Każde wyrażenie musi zakończyć się średnikiem
- Gdy zmienna zostanie zadeklarowana ponownie w tym samym scopie zostanie ona zastąpiona nową wartością.
- Gdy funkcja zostanie zadeklarowana ponownie zostanie zgłoszony błąd
- Po wyjściu ze scopu identyfikator zostaje usunięty
- Wymagana jest funkcja main

### Wbudowane typy

- Podstawowe typy
  - int
  - float
  - str
  - bool
  - null
- Typy złożone
  - Array
    - Metody
      - add(element)
      - remove(element)
      - removeAt(index)
      - clear()
      - get(index)
      - set(index, element)
      - size()
      - contains(element)
      - indexOf(element)
  - Student(name, surname, age)

### Typy błędów

Każdy błąd posiada informacje o linii i kolumnie w których wystąpił.

- Error - Klasa bazowa
- ArgumentError
- TypeError
- ExpressionError
- VariableError
- RuntimeError
- PropertyError
- FunctionError
  
### Wbudowane funkcje

- print(args); - wypisuje na ekranie wartości przekazane jako argumenty oddzielone przecinkami

### Właściwości zmiennych

- Wszystkie zmienne są nullowalne
- Zmienne domyślnie są typu null i są mutowalne

### Operatory i ich priorytety

Priorytety operatorów w wyrażeniach są uporządkowane od najwyższego do najniższego.
Priorytety operatorów są uzależnione on zakresu w jakim się znajdują.

1. Operator dostępu do elementu obiektu (., ?.)
2. Operator sprawdzenia typu (is)
3. Operator negacj (!, -)
4. Operatory multiplikatywne (\*, /, %)
5. Operatory adytywne (+, -)
6. Operatory porównania (==, !=, <, >, <=, >=)
7. Logiczny AND (&)
8. Loginczy OR (|)
9. Operator przypisania (=, +=, -=, \*=, /=, %=)

Operatory bez priorytetów:

- Operator referencji (@)

### Instrukcje warunkowe

- if (warunek) { instrukcje }
- if (warunek) { instrukcje } else { instrukcje }
- if (warunek) { instrukcje } else if (warunek) { instrukcje } else { instrukcje }

warunek może być wyrażeniem logicznym lub wyrażeniem zwracającym wartość typu bool

### Pętle

- while (warunek) { instrukcje }
- for (zmienna: tablica) { instrukcje }

warunek może być wyrażeniem logicznym lub wyrażeniem zwracającym wartość typu bool

### Rzucanie wyjątków

Aby rzucić wyjątek należy użyć słowa kluczowego throw a następnie wywołać konstruktor klasy błędu.
Konstruktor klasy błędu będzie zawierał dwa opcjonalne pola, pierwszym będzie komunikat który ma zostać wyświetlony po rzucenu wyjątku, a drugim wartość zmiennej której dotyczy błąd.

`throw ArgumentError("Argument x cannot be negative. Value of x is: ", x);`

Error message będzie wyglądał mniej więcej tak:

`[ArgumentError]` Argument x cannot be negative. Value of x is: -1 in line x column y

### Wyłapywanie wyjątków

Aby wyłapać wyjątek musimy umieścić metodę która rzuca wyjątek w nawiasach klamrowych po słowie kluczowym try. Fukcję która ma się wywołać po rzuceniu wyjątku umieszczamy w nawiasach klamrowych po słowie kluczowym catch.

Słowo catch bez żadnych argumentów będzie przechwytywało każdy wyjątek bez dostępu do jego szczegółowych infromacji.

Słowo catch z argumentem typu Error będzie przechwytywało każdy wyjątek i zapisze jego szczegółowe informacje w tym argumencie.

Słowo catch z argumentem o szczegółowym typie błędu będzie przechwytywało wyjątek tego samego typu co argument i zapisze jego szczegółowe informacje w tym argumencie.

Możemy przechwycić wiele typów wyjątków w jednym bloku catch.

Może być wiele słów kluczowych catch po jednym bloku try.

Wyjątek rzucony w scopie występującym po słowie kluczowym catch musi zostać obsłużony oddzielnie.

### Komentarze

`# Komentarz jednoliniowy`

## Własne funkcje i klasy

Aby dodać nową funkcję wbudowaną należy zdefiniować nową klasę dziedziczącą po klasie `BuiltInFunction`.
W tej klasie należy zaimplementować metodę `__init__` w której należy zainicjować nazwę funkcji (`self.name`) oraz opcjonalnie liczbę argumentów (`self.argc` - nie ustawiamy jeżeli liczba argumentów jest nieskończona).
Należy również zaimplementować metodę `execute` która będzie wywoływała funckję.
Metoda execute MUSI przyjmować tablicę argumentów, nawet jeżeli funkcja jest bezargumentowa.
Po zdefiniowaniu klasy należy dodać ją do funkcji `get_built_in_functions` zwracającej słownik funkcji z kluczem w postaci nazwy funkcji i wartościa w postaci instancji klasy
Funkcja ta znajduje się w pliku `builtInFunctions.py`.

Aby zdefiniować własną klasę działamy dość podobnie.
Po zdefiniowaniu własnej pythonowej klasy definiujemy kolejną funkcję wbudowaną będącą konstruktorem danej klasy.
W metodzie `__init__` podajemy nazwę klasy (`self.name`) oraz listę argumentów potrzebnych przy inicjowaniu klasy (`self.args`).
Metoda `execute` konstruuje obiekt klasy na podstawie podanych argumentów i zwraca go.

## Analiza leksykalna

Analizator leksykalny (Lexer) jest częścią kompilatora odpowiedzialną za podział kodu źródłowego na tokeny. Lexer będzie działał leniwie, czyli będzie odczytywał kod znak po znaku i tworzył tokeny dopiero gdy będzie miał wystarczającą ilość znaków do stworzenia tokenu. Należało wprowadzić ograiczenia na długość tokenów, aby nie było możliwe stworzenie nieskończenie długiego tokenu.

### Testy

Testowanie polegało na sprawdzeniu czy odpowiedni ciąg znaków zostanie rozpoznany jako odpowiedni token. Testy zostały podzielone na 5 kategorii:

- Test inicjalizacji - sprawdza czy lexer został poprawnie zainicjalizowany
- Testy pojedynczych tokenów - sprawdzają czy ciąg znaków zostanie rozpoznany jako poprawny token
- Testy pozycji - sprawdzają czy podczas analizy leksykalnej pozycje tokenów są poprawnie zapisywane
- Testy escape'ów - sprawdzają czy znaki escapowane są poprawnie interpretowane
- Testy błędów - sprawdzają czy błędne ciągi znaków zostaną rozpoznane jako odpowiedni błąd

### Tokeny

```python
class TokenType(Enum):
    # --- Literals ---
    T_INT_LITERAL = "int"
    T_FLOAT_LITERAL = "float"
    T_STRING_LITERAL = "string"

    # --- Keywords ---

    # ------ Functions ------
    T_RETURN = "return"
    T_BREAK = "break"
    T_CONTINUE = "continue"
    T_TRY = "try"
    T_CATCH = "catch"
    T_THROW = "throw"

    # ------ Statements ------
    T_IF = "if"
    T_ELIF = "elif"
    T_ELSE = "else"
    T_WHILE = "while"
    T_FOR = "for"

    # ------ Literals ------
    T_TRUE = "true"
    T_FALSE = "false"
    T_NULL = "null"

    # --- Operators ---

    # ------ Arithmetic ------
    T_PLUS = "+"
    T_MINUS = "-"
    T_MULTIPLY = "*"
    T_DIVIDE = "/"
    T_MODULO = "%"

    # ------ Assignment ------
    T_ASSIGN = "="
    T_ASSIGN_PLUS = "+="
    T_ASSIGN_MINUS = "-="
    T_ASSIGN_MULTIPLY = "*="
    T_ASSIGN_DIVIDE = "/="
    T_ASSIGN_MODULO = "%="

    # ------ Comparison ------
    T_GREATER = ">"
    T_LESS = "<"
    T_GREATER_EQUAL = ">="
    T_LESS_EQUAL = "<="
    T_EQUAL = "=="
    T_NOT_EQUAL = "!="

    # ------ Logic ------
    T_AND = "&"
    T_OR = "|"

    # ------ Access ------
    T_ACCESS = "."
    T_NULLABLE_ACCESS = "?."

    # ------ Other ------
    T_NOT = "!"
    T_REF = "@"
    T_TYPE_CHECK = "is"

    # --- Brackets ---
    T_LEFT_BRACKET = "("
    T_RIGHT_BRACKET = ")"
    T_LEFT_CURLY_BRACKET = "{"
    T_RIGHT_CURLY_BRACKET = "}"

    # --- Other ---
    T_IDENTIFIER = "id"
    T_SEMICOLON = ";"
    T_COMMA = ","
    T_COLON = ":"
    T_COMMENT = "#"
    T_OPTIONAL = "?"
    T_UNDEFINED = "undefined"
    T_EOF = "eof"


```

## Analiza składniowa

Analizator składniowy (Parser) jest częścią kompilatora odpowiedzialną za sprawdzenie poprawności składni kodu źródłowego.
Parser odczytuje tokeny jeden po drugim i tworzy drzewo składniowe. Parser przyjmuje lexer jako argument konstruktora i używa go do konsumowania tokenów. Każde wyrażenie będzie miało swoją metodę konstuującą obiekt drzewa składniowego. Parser posiada metodę `parse` która będzie zwracała drzewo składniowe.

### Testy

Testowanie polegało na sprawdzeniu czy odpowiedni ciąg znaków zostanie zinterpretowany jako poprawne drzewo obiektów. Testy zostały podzielone na 6 kategorii:

- Test inicjalizacji - sprawdza czy praser został poprawnie zainicjalizowany
- Testy poszczególnych statementów - sprawdzają czy ciąg znaków zostanie rozpoznany jako poprawny statement
- Testy poszczególnych wyrażeń - sprawdzają czy ciąg znaków zostanie rozpoznany jako poprawne expression
- Testy operatora dostępu - sprawdzają czy ciąg znaków zostanie rozpoznany jako poprawnie skonstruowana klasa operacji dostępu
- Testy parametrów funkcji - sprawdzają czy ciąg znaków zostanie rozpoznany jako poprawnie skonstruowana lista parametrów funkcji
- Testy błędów - sprawdzają czy błędne ciągi znaków zostaną rozpoznane jako odpowiedni błąd

## Interpreter

Interpreter jest częścią kompilatora odpowiedzialną za wykonanie kodu źródłowego.
Interpreter wykonuje kod źródłowy w oparciu o drzewo składniowe.
Działa to na takiej zasadze, że interpreter przechodzi po drzewie składniowym i wykonuje odpowiednie akcje w zależności od tego jakie węzły drzewa składniowego napotka.
Implementacja interpretera została oparta na wzorcu wizytatora.

### Testy

Testownie polegało na sprawdzeniu czy odpowiedni ciąg znaków zostanie zinterpretowany jako poprawny wynik. Kategorii testów było wiele ale można rodzielić dwie głównie kategorie:

- Testy poprawnych programów - sprawdzają czy program zostanie poprawnie wykonany
- Testy błędów - sprawdzają czy w błędnie napisanym programie zostanie rozpoznany odpowiedni błąd

## Gramatyka

Dokument zawierający gramatykę języka znajduje się w folderze `grammar`.
Znajduje się tam zarówno gramatyka w formacie EBNF jak i graficzna reprezentacja.

## Testowanie

Testy będą wykonywane za pomocą biblioteki pytest.
Testy będą umieszczone w folderze tests w pliku o nazwie odpowiadającej nazwie pliku z kodem źródłowym.
Testy będą wykonywane za pomocą komendy:

```bash
pytest
```

## Uruchamianie

Aby uruchomić interpreter należy uruchomić skrypt pythonowy interpretera.
Interpreter będzie uruchamiany za pomocą komendy:

```bash
./main.py [plik]
```

## Przykładowe programy

Przykładowe programy będą umieszczone w folderze `code_examples`.

## Przykładowe wbudowane błędy

[LEXER ERROR - UNKNOWN_TOKEN]: Unknown token at line 2, column 15: ^

[PARSER ERROR - MISSING_SEMICOLON]: Missing semicolon at line 3, column 1

[PARSER ERROR - MISSING_BLOCK_END]: Missing block end at line 2, column 15

[TypeError]: Cannot apply operator + to given values: 1 and a at line 2 column 11

[FunctionError]: Function test is not defined at line 2 column 5
