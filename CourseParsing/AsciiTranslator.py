def get_char(i):
    if i + ord('A') > ord('Z'):
        return chr(i - 26 + ord('a'))
    return chr(i + ord('A'))

def get_index(c):
    if ord(c) - ord('A') > 26:
        return ord(c) - ord('a') + 26
    return ord(c) - ord('A')


if __name__ == "__main__":
    print(get_char(0))
    print(get_char(26))
    print(get_char(27))
    print(get_char(15))

    print(get_index("A"))
    print(get_index("Z"))
    print(get_index("a"))
    print(get_index("c"))

