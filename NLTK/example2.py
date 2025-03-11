import nltk

grammar = nltk.CFG.fromstring("""
    O -> Suj Pred
    Suj -> Det Sust
    Det -> "el"
    Sust -> "Perro" | "gato"
    Pred -> Verbo
    Verbo -> VT | VI
    VT -> "come"
    VI -> "duerme"                
""")

try:
    text= "el gato come"
    tokens = text.split()
    rd_parser = nltk.RecursiveDescentParser(grammar)
    for tree in rd_parser.parse(tokens):
        print(tree)
        tree.pretty_print()
except ValueError:
    print("no se reconoce como oración del lenguaje")