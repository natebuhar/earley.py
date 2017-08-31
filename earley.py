class Grammar:
    def __init__(self, terminals, nonterminals):
        self.terminals = terminals
        self.nonterminals = nonterminals
        self.nullable = self.get_nullable_rules()

    def __getitem__(self, symbol):
        try:
            return self.terminals[symbol]
        except KeyError:
            return self.nonterminals[symbol]

    def __contains__(self, symbol):
        return symbol in self.terminals or symbol in self.nonterminals

    def get_nullable_rules(self):
        """ Find all nullable symbols in the grammar. """
        nss = []
        def is_nullable(rule):
            for x in rule:
                if x not in nss:
                    return False
            return True

        def update_nss():
            for s, rules in self.nonterminals.items():
                for x in rules:
                    if is_nullable(x) and s not in nss:
                        nss.append(s)

        while True:
            size = len(nss)
            update_nss()
            if size == len(nss):
                break
        return nss

class Rule:
    __slots__ = ['symbol', 'seq']

    def __init__(self, symbol, seq):
        self.symbol = symbol
        self.seq = seq

    def __eq__(self, other):
        return \
            self.symbol == other.symbol and \
            self.seq == other.seq

    def __len__(self):
        return len(self.seq)

    def __getitem__(self, index):
        return self.seq[index]

    def __repr__(self):
        return '[{} -> {}]'.format(self.symbol, ' '.join(self.seq))

class Item:
    __slots__ = ['rule', 'dot', 'start']

    def __init__(self, rule, dot, start):
        self.rule = rule
        self.dot = dot
        self.start = start

    def __eq__(self, other):
        return \
            self.rule  == other.rule and \
            self.dot == other.dot and \
            self.start == other.start

    def __repr__(self):
        seq = list(self.rule.seq)
        seq.insert(self.dot, '•')
        seq = ' '.join(seq)
        return '[{} -> {} ({})]'.format(self.rule.symbol, seq, self.start)

    @classmethod
    def advance(cls, item):
        return cls(item.rule, item.dot + 1, item.start)

def earley(grammar, string):
    statesets = [[]]

    symbol = list(grammar.nonterminals.keys())[0]
    for rule in grammar[symbol]:
        statesets[-1].append(Item(rule, 0, 0))

    i = 0
    while i < len(statesets):
        stateset = statesets[i]

        j = 0
        while j < len(stateset):
            item = stateset[j]
            rule = item.rule

            if item.dot == len(rule):
                # completion
                for x in statesets[item.start]:
                    if x.dot < len(x.rule) and x.rule[x.dot] == item.rule.symbol:
                        newitem = Item.advance(x)
                        if newitem not in stateset:
                            stateset.append(newitem)

            elif rule[item.dot] in grammar.terminals and i < len(string):
                # scan
                symbol = rule[item.dot]
                token = string[i]
                if grammar.terminals[symbol](token):
                    newitem = Item.advance(item)
                    if i == len(statesets) - 1:
                        statesets.append([])
                    statesets[i + 1].append(newitem)

            elif rule[item.dot] in grammar.nonterminals:
                # prediction
                symbol = rule[item.dot]
                for rule in grammar[symbol]:
                    newitem = Item(rule, 0, i)
                    if newitem not in stateset:
                        stateset.append(newitem)

                # automatic completion for nullable symbols
                if symbol in grammar.nullable:
                    newitem = Item.advance(item)
                    if newitem not in statesets[i]:
                        statesets[i].append(newitem)

            j += 1
        i += 1

    return statesets

def dump_statesets(statesets):
    for i, s in enumerate(statesets):
        print('=== S({}) ==='.format(i))
        for i, x in enumerate(s):
            print('{}: {}'.format(i, x))
        print()

    print('=== COMPLETED ===')
    for i, x in enumerate(statesets[-1]):
        if x.dot == len(x.rule) and x.start == 0:
            print('{}: {}'.format(i, x))

def completed_items(stateset):
    for x in stateset[-1]:
        if x.dot == len(x.rule) and x.start == 0:
            yield x

def is_valid_parse(grammar, string):
    stateset = earley(grammar, string)
    return \
        len(stateset) == len(string) + 1 and \
        len(list(completed_items(stateset))) == 1

def test_simple_arith():
    grammar = Grammar(
        {
            '[+-]': lambda x: x in '+-',
            '[*/]': lambda x: x in '*/',
            '[0-9]': lambda x: x.isdecimal(),
            '(': lambda x: x == '(',
            ')': lambda x: x == ')',
        },
        {
            'Sum': [
                Rule('Sum', ['Sum', '[+-]', 'Product']),
                Rule('Sum', ['Product']),
            ],
            'Product': [
                Rule('Product', ['Product', '[*/]', 'Factor']),
                Rule('Product', ['Factor']),
            ],

            'Factor': [
                Rule('Factor', ['(', 'Sum', ')']),
                Rule('Factor', ['Number']),
            ],

            'Number': [
                Rule('Number', ['[0-9]', 'Number']),
                Rule('Number', ['[0-9]']),
            ],
        }
    )

    positive = [
        '1+2',
        '1+(2*3-4)',
    ]
    for string in positive:
        assert is_valid_parse(grammar, string)

    negative = [
        '',
        '1+',
        '+1',
        '2+(4*5',
        '2+(4*5))',
        '2++2',
    ]
    for string in negative:
        assert not is_valid_parse(grammar, string)

def test_nullable():
    grammar1 = Grammar(
        {
            'a': lambda x: x == 'a',
        },
        {
            'A': [
                Rule('A', ['a', 'A']),
                Rule('A', []),
            ],
        }
    )

    grammar2 = Grammar(
        {
            'a': lambda x: x == 'a',
            'b': lambda x: x == 'b',
        },
        {
            'A': [
                Rule('A', ['a', 'A']),
                Rule('A', ['b'])
            ],
        }
    )

    positive = [
        (grammar1, ''),
        (grammar1, 'aaa'),
        (grammar2, 'aaab'),
    ]
    for grammar, string in positive:
        assert is_valid_parse(grammar, string)

    negative = [
        (grammar2, ''),
        (grammar2, 'aaa'),
        (grammar1, 'aaab'),
    ]
    for grammar, string in negative:
        assert not is_valid_parse(grammar, string)

test_nullable()