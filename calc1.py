#!/usr/bin/env python3
'''
a simple interpreter only could handle `digit+digit`
'''

EOF, OP, INTEGER = 'EOF', 'OP', 'INTEGER'


class Token(object):

    def __init__(self, token_type, value=None):
        self.token_type = token_type
        self.value = value

    def __str__(self):
        return "<Token %s, %s>" % (self.token_type, self.value)

    def __repr__(self):
        return self.__str__()


class Interpreter(object):
    def __init__(self, text):
        self.text = text
        self.current_token = None
        self.pos = 0

    def error(self):
        raise Exception('Error parsing input')

    def get_next_token(self):

        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

        if self.pos > len(self.text) - 1:
            return Token(EOF)

        current_char = self.text[self.pos]
        if current_char.isdigit():
            anchor = self.pos
            self.pos += 1
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
            return Token(INTEGER, int(self.text[anchor: self.pos]))
        elif current_char == '+' or current_char == '-':
            self.pos += 1
            return Token(OP, (lambda x, y: x + y) if current_char == '+'
                         else (lambda x, y: x - y))
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
        op = self.current_token
        self.eat(OP)
        right = self.current_token
        self.eat(INTEGER)

        return op.value(left.value, right.value)


def main():
    while True:
        try:
            text = input('calc>').strip()
        except EOFError:
            break
        if not text:
            continue
        result = Interpreter(text).expr()
        print(result)

if __name__ == '__main__':
    main()
