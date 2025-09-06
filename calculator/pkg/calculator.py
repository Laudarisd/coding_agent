class Calculator:
    def __init__(self):
        self.operators = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
            "^": lambda a, b: a ** b,
        }
        self.precedence = {
            "+": 1,
            "-": 1,
            "*": 2,
            "/": 2,
            "^": 3,
        }

    def evaluate(self, expression):
        if not expression or expression.isspace():
            return None
        tokens = expression.strip().split()
        return self._evaluate_infix(tokens)

    def _evaluate_infix(self, tokens):
        values = []
        operators = []

        for token in tokens:
            if token in self.operators:
                while (
                    operators
                    and operators[-1] in self.operators
                    and self.precedence[operators[-1]] >= self.precedence[token]
                ):
                    self._apply_operator(operators, values)
                operators.append(token)
            else:
                try:
                    values.append(float(token))
                except ValueError:
                    raise ValueError("Invalid token: {}".format(token))

        while operators:
            self._apply_operator(operators, values)

        return values[0] if values else None

    def _apply_operator(self, operators, values):
        operator = operators.pop()
        if len(values) < 2:
            raise ValueError("Not enough operands for operator: {}".format(operator))
        operand2 = values.pop()
        operand1 = values.pop()
        operation = self.operators[operator]
        result = operation(operand1, operand2)
        values.append(result)
