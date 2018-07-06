import re

text = 'hi git brot'


def in_text(keywords):
    return any(k in text for k in keywords)

print(in_text(['gi']))
