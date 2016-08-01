#! /usr/bin/env python3
"""
expr := term ( (+|-) term )*
term := factor ( (*|/) term) )*
factor := integer
"""
import operator

EOF, PLUS, MINUS, MUL, DIV, INTEGER = ('EOF', 'PLUS', 'MINUS', 'MUL', 'DIV',
                                       'INTEGER')


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
            if current_char == '+':
                pos += 1
                yield Token(PLUS, operator.add)
            elif current_char == '-':
                pos += 1
                yield Token(MINUS, operator.sub)
            elif current_char == '*':
                pos += 1
                yield Token(MUL, operator.mul)
            elif current_char == '/':
                pos += 1
                yield Token(DIV, operator.truediv)
            elif current_char.isdigit():
                [value, pos] = self.integer(pos)
                yield Token(INTEGER, value)
            else:
                self.error()
        yield Token(EOF)


class Interpreter(object):

    def __init__(self, text):
        self.text = text
        self.tokens = Lexer(text).tokens
        self.current_token = next(self.tokens)

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = next(self.tokens)
        else:
            self.error()

    def factor(self):
        ret = self.current_token.value
        self.eat(INTEGER)
        return ret

    def term(self):
        result = self.factor()
        while self.current_token.type in {MUL, DIV}:
            op = self.current_token
            self.eat(self.current_token.type)
            result = op.value(result, self.factor())

        return result

    def expr(self):
        result = self.term()
        while self.current_token.type in {PLUS, MINUS}:
            op = self.current_token
            self.eat(self.current_token.type)
            result = op.value(result, self.term())
        return result


def main():

    while True:
        try:
            text = input('calc>').strip()
        except EOFError:
            break
        if not text:
            continue
        print(Interpreter(text).expr())


if __name__ == '__main__':
    main()
