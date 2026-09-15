def calculate(expression):
    """Обчислює вираз із числами, +, -, *, / та дужками без бібліотек."""
    position = 0

    def skip_spaces():
        nonlocal position
        while position < len(expression) and expression[position].isspace():
            position += 1

    def parse_number():
        nonlocal position
        skip_spaces()
        start = position

        # Читаємо всі цифри й десяткову крапку одного числа.
        while position < len(expression):
            character = expression[position]
            if character not in "0123456789.":
                break
            position += 1

        number = expression[start:position]
        if not number:
            raise ValueError("Очікується число або відкривальна дужка.")
        if number == "." or number.count(".") > 1:
            raise ValueError("Некоректне число: " + number)
        return float(number)

    def parse_factor():
        nonlocal position
        skip_spaces()
        if position >= len(expression):
            raise ValueError("Вираз порожній або незавершений.")

        character = expression[position]

        # Підтримуємо знак перед числом або дужками: -3, +2, -(2 + 3).
        if character in "+-":
            position += 1
            value = parse_factor()
            if character == "-":
                return -value
            return value

        # Вираз у дужках обчислюється раніше за зовнішні операції.
        if character == "(":
            position += 1
            value = parse_expression()
            skip_spaces()
            if position >= len(expression) or expression[position] != ")":
                raise ValueError("Не вистачає закривальної дужки.")
            position += 1
            return value

        return parse_number()

    def parse_term():
        nonlocal position
        result = parse_factor()

        # Множення та ділення мають вищий пріоритет; рахуємо зліва направо.
        while True:
            skip_spaces()
            if position >= len(expression) or expression[position] not in "*/":
                return result

            operation = expression[position]
            position += 1
            right_number = parse_factor()

            if operation == "*":
                result *= right_number
            else:
                if right_number == 0:
                    raise ZeroDivisionError("Ділення на нуль неможливе.")
                result /= right_number

    def parse_expression():
        nonlocal position
        result = parse_term()

        # Додавання та віднімання виконуються після множення й ділення.
        while True:
            skip_spaces()
            if position >= len(expression) or expression[position] not in "+-":
                return result

            operation = expression[position]
            position += 1
            right_number = parse_term()

            if operation == "+":
                result += right_number
            else:
                result -= right_number

    result = parse_expression()
    skip_spaces()
    if position != len(expression):
        raise ValueError("Неочікуваний символ: " + expression[position])
    return result


if __name__ == "__main__":
    expression = input("Введіть вираз, наприклад (2 + 3) * 4: ")
    try:
        print("Результат:", calculate(expression))
    except (ValueError, ZeroDivisionError) as error:
        print("Помилка:", error)
    except RecursionError:
        print("Помилка: надто багато вкладених дужок або знаків.")
