from utils import format_result


def add(a, b):
    return a + b


class Calculator:

    def multiply(self, a, b):
        return a * b

    def show_result(self, value):
        return format_result(value)