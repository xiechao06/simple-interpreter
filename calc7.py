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
        '*': PLUS,
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


class Parser(object):

    def __init__(self, lexer):
        self.tokens = lexer.tokens
        self.current_token = next(self.tokens)

    def factor(self):

        if self.current_token.type == INTEGER:
            ret = {
                'value': self.current_token.value
            }
            self.eat(INTEGER)
        else:
            self.eat(LPAREN)
            ret = self.expr()
            self.eat(RPAREN)
        return ret

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = next(self.tokens)
        else:
            self.error()

    def term(self):

        node = self.factor()
        while self.current_token.type in {MUL, DIV}:
            op = self.current_token
            self.eat(self.current_token.type)
            node = {
                'left': node,
                'value': op.value,
                'right': self.factor()
            }

        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in {PLUS, MINUS}:
            op = self.current_token
            self.eat(self.current_token.type)
            node = {
                'left': node,
                'value': op.value,
                'right': self.term(),
            }
        return node


class Interpreter(object):

    def __init__(self, tree):
        self.__tree = tree

    def is_leaf(self, node):
        return 'left' not in node

    def visit(self, node):
        if self.is_leaf(node):
            return node['value']
        else:
            return node['value'](self.visit(node['left']),
                              self.visit(node['right']))


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
