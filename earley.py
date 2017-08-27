from copy import copy

class Item:
    __slots__ = ['rule', 'dot', 'start']

    def __init__(self, rule, dot, start):
        assert type(rule) is tuple
        self.rule = rule
        self.dot = dot
        self.start = start

    def __eq__(self, other):
        return \
            self.rule  == other.rule and \
            self.dot == other.dot and \
            self.start == other.start

    def __repr__(self):
        k, r = self.rule
        r = grammar[k][r][:]
        r.insert(self.dot, '•')
        return '{} -> {} ({})'.format(k, ' '.join(r), self.start)

    def getrule(self):
        return grammar[self.rule[0]][self.rule[1]]

def earley(terminals, grammar, tokens):
    statesets = [[]]

    k = list(grammar.keys())[0]
    for i in range(len(grammar[k])):
        statesets[-1].append(Item((k, i), 0, 0))

    i = 0
    while i < len(statesets):
        stateset = statesets[i]

        j = 0
        while j < len(stateset):
            item = stateset[j]
            rule = item.getrule()

            if item.dot == len(rule):
                print('completion:', item)
                for x in statesets[item.start]:
                    r = x.getrule()
                    if x.dot < len(r) and r[x.dot] == item.rule[0]:
                        newitem = copy(x)
                        newitem.dot += 1
                        assert newitem not in stateset
                        stateset.append(newitem)

            elif rule[item.dot] in terminals and i < len(tokens):
                k = rule[item.dot]
                token = tokens[i]
                if terminals[k](token):
                    print('scan:', repr(token), k)
                    newitem = copy(item)
                    newitem.dot += 1
                    if i == len(statesets) - 1:
                        statesets.append([])
                    statesets[i + 1].append(newitem)

            elif rule[item.dot] in grammar:
                print('prediction:', item)
                k = rule[item.dot]
                for x in range(len(grammar[k])):
                    newitem = Item((k, x), 0, i)
                    if newitem not in stateset:
                        stateset.append(newitem)
            j += 1
        i += 1

    print()
    for i, s in enumerate(statesets):
        print('=== S({}) ==='.format(i))
        for i, x in enumerate(s):
            print('{}: {}'.format(i, x))
        print()

    if len(statesets) == len(tokens) + 1:
        print('=== COMPLETED ===')
        for i, x in enumerate(statesets[-1]):
            if x.dot == len(x.getrule()) and x.start == 0:
                print('{}: {}'.format(i, x))

terminals = {
    '[+-]': lambda x: x in '+-',
    '[*/]': lambda x: x in '*/',
    '[0-9]': lambda x: x.isdecimal(),
    '(': lambda x: x == '(',
    ')': lambda x: x == ')',
}

grammar = {
    'Sum': [
        ['Sum', '[+-]', 'Product'],
        ['Product']],

    'Product': [
        ['Product', '[*/]', 'Factor'],
        ['Factor']],

    'Factor': [
        ['(', 'Sum', ')'],
        ['Number']],

    'Number': [
        ['[0-9]', 'Number'],
        ['[0-9]']]
}

test1 = ['1', '+', '2']
test2 = ['1', '+', '(', '2', '*', '3', '-', '4', ')']

earley(terminals, grammar, test2)