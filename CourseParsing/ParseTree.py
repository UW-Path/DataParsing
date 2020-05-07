from CourseParsing.AsciiTranslator import get_char, get_index
import re


class Stack:
    def __init__(self):
        self._data = []
    def push(self, x):
        self._data.append(x)
    def pop(self):
        return self._data.pop()
    def peek(self):
        return self._data[-1]
    def __len__(self):
        return len(self._data)


def convert(s):
    # initialization of string to " "
    new = " "

    # traverse in the string
    for x in s:
        if x != "True":
            new += re.sub("[A-Z][A-Za-z]+", "", x) + " "

        # return string
    return new


def remove_dup_bracket(logic):
    logic = logic.split()
    n = len(logic)
    s = logic.copy()
    stack = Stack()

    for i in range(n):
        if s[i] != "$":
            s[i] = logic[i]
            if s[i] == "<":
                if i + 1 < n and s[i+1] in "&|":
                    s[i+1] = "$"
                    stack.push(i)
                elif i + 1 < n and s[i+1] == ">":
                    if i == 0 or s[i-1] in "&|":
                        s[i] = "True"
                    else:
                        s[i] = "$"
                    s[i+1] = "$"
                elif i + 2 < n and s[i+2] == ">":
                    s[i] = "$"
                    s[i+2] = "$"
                else:
                    stack.push(i)

            elif s[i] == ">":
                if len(stack):
                    start = stack.pop()
                    if (start == 0 and i == n - 1) or \
                       (i > 0 and s[start-1] == "<" and i < n - 1 and s[i+1] == ">"):
                        s[start] = "$"
                        s[i] = "$"
                    if s[i-1] in ("&", "|", "not"):
                        s[i-1] = "$"
                else:
                    s[i] = "$"
            elif s[i] == "~":
                s[i] = "not"
            elif (i + 1 < n and s[i+1] == s[i]) or s[i] == "-":
                s[i] = "$"
    while len(stack):
        i = stack.pop()
        s[i] = "$"

    return "<" + convert(list(filter(lambda a: a != "$", s))) + ">"


def translate_to_python(logic, courses=None):
    logic = logic.replace("<", "(").replace(">", ")")
    logic = logic.split()
    in_cond = False
    i = 0
    while i < len(logic):
        if logic[i] in "123456":  # Does not support nested "X of" statements
            logic[i] = "(" + logic[i] + " <= len(tuple(filter(None,["
            in_cond = True
        elif in_cond and logic[i] == "(":
            i += logic[i:].index(")")
        elif in_cond and logic[i] in "&)":
            in_cond = False
            logic[i] = "])))))"
        elif in_cond and logic[i] == "|":
            logic[i] = ","
        i += 1

    if isinstance(courses, list):
        start = 0
        for i in range(len(courses)):
            x = logic[start:].index(get_char(i))
            logic[start+x] = courses[i]
            start = x + 1

    logic = " ".join(logic)
    return logic.replace("|", "or").replace("&", "and").replace(" ***", "").replace(" ###", "")


def fix_logic(logic):
    logic = logic.split()
    index = 0
    for i in range(len(logic)):
        if len(logic[i]) == 1 and logic[i].isalpha():
            logic[i] = get_char(index)
            index += 1
    return " ".join(logic)


class ParseTree:
    def __init__(self, val):
        self.children = []
        self.val = val

    def add_children(self, children_text):
        for ct in children_text:
            self.children.append(ParseTree(ct))

    def insert_left(self, child):
        self.children = [ParseTree(child)] + self.children

    def insert_right(self, child):
        self.children = self.children + [ParseTree(child)]

    def get_left(self):
        if len(self.children):
            return self.children[0]

    def get_right(self):
        if len(self.children):
            return self.children[-1]

    def set_value(self, value):
        self.val = value

    def __str__(self, level=0):
        output = "  " * level + self.val
        output += "\n"
        for child in self.children:
            output += "  " * level + child.__str__(level+1)
        return output

    def combine(self, c1, c2):
        c = []
        for v in c1:
            for w in c2:
                c.append(v + w)
        return c

    def options(self):
        opt = []
        if self.val not in ["&", "|", "-"]:
            return self.val
        elif self.val == "&":
            opt = self.children[0].options()
            for i in range(1, len(self.children)):
                opt = self.combine(opt, self.children[i].options())
            return opt
        elif self.val == "|":
            for i in range(len(self.children)):
                options = self.children[i].options()
                for o in options:
                    opt.append(o)
            return opt
        elif self.val == "-" and len(self.children):
            child_opt = self.children[0].options()
            if isinstance(child_opt, list):
                opt = child_opt
            else:
                opt = [child_opt]
        return opt



def buildParseTree(text):
    text = remove_dup_bracket(text)
    print(text)
    chars = text.split()
    pStack = Stack()
    eTree = ParseTree('-')
    pStack.push(eTree)
    currentTree = eTree

    for c in chars:
        if c == '<':
            currentTree.insert_left('-')
            pStack.push(currentTree)
            currentTree = currentTree.get_left()

        elif c in ['&', '|']:
            currentTree.set_value(c)
            currentTree.insert_right('')
            pStack.push(currentTree)
            currentTree = currentTree.get_right()

        elif c == '>':
            currentTree = pStack.pop()

        elif c not in ["&", "|", " "]:
            currentTree.set_value(c)
            currentTree = pStack.pop()

    return eTree


def verify(logic, debug=False):
    print(logic)
    pt = buildParseTree(logic)
    print(pt.options())
    if debug:
        print(pt)


def denote_coreqs_helper(logic, courses, i):
    while logic[i] != ">":
        i += 1
        if logic[i] == "<":
            i, courses = denote_coreqs_helper(logic, courses, i)
        else:
            index = get_index(logic[i])
            if 0 <= index < len(courses) and courses[index][0] != "_":
                courses[index] = "_" + courses[index]
    i += 1
    return i, courses


def denote_coreqs(logic, courses):
    logic = logic.split()
    coreq_indicators = []
    coreq_all = []

    for i in range(len(logic)):
        if logic[i] == "###":
            coreq_indicators.append(i)
        if logic[i] == "***":
            coreq_all.append(i)

    for i in coreq_all:
        i += 1
        while i < len(logic):
            index = get_index(logic[i])
            if 0 <= index < len(courses) and courses[index][0] != "_":
                courses[index] = "_" + courses[index]
            i += 1

    for i in coreq_indicators:
        i, courses = denote_coreqs_helper(logic, courses, i)

    return courses


if __name__ == "__main__":
    """logic = [
        "< A >",
        "< A | B >",
        "< A & B >",
        "< A | B | C >",
        "< A & B & C >",
        "< A | < B & C > >",
        "< A & < B | C > >",
        "< < A | B > & C >",
        "< < A & B > | C >",
        "< < A & B > | < C & D > >",
        "< < A | B > & < C | D > >",
        "< < A | B > & < C | D | E > >",
        "< < A | B > & < < C & D > | E | < F & G & H > > >",
    ]
    for l in logic:
        verify(l)
        print("_____________")"""

    # print(translate_to_python("< 2 A | < B & C > | D | E >"))
