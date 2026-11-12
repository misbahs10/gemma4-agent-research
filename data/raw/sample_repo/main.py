from calculator import add, Calculator


def run():
    total = add(10, 20)

    calculator = Calculator()

    result = calculator.multiply(total, 2)

    return result