#! /usr/bin/env python3
"""
expr := term ( (+|-) term )*
term := factor ( (*|/) term) )*
factor := integer | \( expr \)
"""
import operator

(EOF, PLUS, MINUS, MUL, DIV, INTEGER, LPAREN, RPAREN) = (
    'EOF', 'PLUS', 'MINUS', 'MUL', 'DIV', 'INTEGER', '(', ')')


class Token(object):

    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __str__(self):
        return '<Token %s%s>' % (self.type,
                                 '' if self.value is None else ':' +
                                 repr(self.value))

    def __repr__(self):
        return self.__str__()


class Lexer(object):

    token_type_map = {
        '+': PLUS,
        '-': MINUS,
        '*': MUL,
        '/': DIV,
        '(': LPAREN,
        ')': RPAREN,
    }

    op_value_map = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
    }

    def __init__(self, text):
        self.text = text + '\0'

    def skip_spaces(self, pos):
        while self.text[pos] != '\0' and self.text[pos].isspace():
            pos += 1
        return pos

    def error(self):
        raise Exception('invalid character')

    def integer(self, pos):
        anchor = pos
        while self.text[pos] != '\0' and self.text[pos].isdigit():
            pos += 1
        return [int(self.text[anchor: pos]), pos]

    @property
    def tokens(self):
        pos = 0
        while self.text[pos] != '\0':
            pos = self.skip_spaces(pos)
            current_char = self.text[pos]
            if current_char in {'+', '-', '*', '/', '(', ')'}:
                pos += 1
                yield Token(self.token_type_map[current_char],
                            self.op_value_map.get(current_char))
            elif current_char.isdigit():
                [value, pos] = self.integer(pos)
                yield Token(INTEGER, value)
            else:
                self.error()
        yield Token(EOF)


class Node(object):
    pass


class Num(Node):

    def __init__(self, value):
        self.value = value


class BinOp(Node):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    @property
    def value(self):
        return self.op(self.left.value, self.right.value)


class UnaryOp(Node):

    def __init__(self, op, child):

        self.op = op
        self.child = child

    @property
    def value(self):
        return self.op(self.child.value)


class Parser(object):

    def __init__(self, lexer):
        self.tokens = lexer.tokens
        self.current_token = next(self.tokens)

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = next(self.tokens)
        else:
            self.error()

    def error(self):
        raise Exception("unexpected token: " + str(self.current_token))

    def factor(self):
        if self.current_token.type == INTEGER:
            ret = Num(self.current_token.value)
            self.eat(INTEGER)
        elif self.current_token.type in {PLUS, MINUS}:
            op = {
                PLUS: operator.pos,
                MINUS: operator.neg,
            }[self.current_token.type]
            self.eat(self.current_token.type)
            ret = UnaryOp(op, self.expr())
        elif self.current_token.type == LPAREN:
            self.eat(LPAREN)
            ret = self.expr()
            self.eat(RPAREN)
        else:
            self.error()
        return ret

    def term(self):

        node = self.factor()
        while self.current_token.type in {MUL, DIV}:
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinOp(op, node, self.factor())

        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in {PLUS, MINUS}:
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinOp(op, node, self.term())
        return node


class Interpreter(object):

    def __init__(self, tree):
        self.__tree = tree

    def visit(self, node):
        return node.value

    def interpret(self):
        return self.visit(self.__tree)


def main():

    while True:
        try:
            text = input('calc>').strip()
        except EOFError:
            break

        if not text:
            continue

        lexer = Lexer(text)
        tree = Parser(lexer).expr()
        interpreter = Interpreter(tree)
        print(interpreter.interpret())

if __name__ == '__main__':
    main()
