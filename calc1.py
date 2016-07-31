#!/usr/bin/env python3
'''
a simple interpreter only could handle `digit+digit`
'''

EOF, PLUS, INTEGER = "EOF", "PLUS", "INTEGER"


class Token(object):

    def __init__(self, token_type, value=None):
        self.token_type = token_type
        self.value = value


class Interpreter(object):
    def __init__(self, text):
        self.text = text
        self.current_token = None
        self.pos = 0

    def error(self):
        raise Exception('Error parsing input')

    def get_next_token(self):

        if self.pos > len(self.text) - 1:
            return Token(EOF)

        current_char = self.text[self.pos]
        if current_char.isdigit():
            self.pos += 1
            return Token(INTEGER, int(current_char))
        elif current_char == '+':
            self.pos += 1
            return Token(PLUS)
        else:
            self.error()

    def eat(self, token_type):

        if self.current_token.token_type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error()

    def expr(self):

        self.current_token = self.get_next_token()

        left = self.current_token
        self.eat(INTEGER)
        self.eat(PLUS)
        right = self.current_token
        self.eat(INTEGER)

        return left.value + right.value


def main():
    while True:
        try:
            text = input('calc>')
        except EOFError:
            break
        if not text:
            continue
        result = Interpreter(text).expr()
        print(result)

if __name__ == '__main__':
    main()
