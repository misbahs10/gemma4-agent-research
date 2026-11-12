import os
import math


def add(a, b):
    return a + b


def calculate_area(radius):
    result = add(radius, radius)
    return math.pi * result


class Calculator:

    def multiply(self, a, b):
        return a * b

    def calculate(self, x, y):
        return self.multiply(x, y)