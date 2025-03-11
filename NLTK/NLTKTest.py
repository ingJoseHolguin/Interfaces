# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import nltk
from nltk import grammar, parse
from nltk import load_parser
from nltk.parse.generate import generate

# grammar = nltk.CFG.fromstring("""
#    O -> Suj Pred
#    Suj -> Det Sust
#    Det -> "el"
#    Sust -> "perro" | "gato"
#    Pred -> Verbo
#    Verbo -> VT | VI
#    VT -> "come"
#    VI -> "duerme"
#  """)

# try:
#     text = "el gato come"
#     tokens = text.split()
#     rd_parser = nltk.RecursiveDescentParser(grammar)
#     for tree in rd_parser.parse(tokens):
#         print(tree)
#         tree.pretty_print()
# except ValueError:
#     print("No se reconoce como oración del lenguaje")

# grammar1 = nltk.CFG.fromstring("""
#   S -> NP VP
#   VP -> V NP | V NP PP
#   PP -> P NP
#   V -> "saw" | "ate" | "walked"
#   NP -> "John" | "Mary" | "Bob" | Det N | Det N PP
#   Det -> "a" | "an" | "the" | "my"
#   N -> "man" | "dog" | "cat" | "telescope" | "park"
#   P -> "in" | "on" | "by" | "with"
# """)

# text = "John saw a man with a telescope"
# tokens = text.split()
# rd_parser = nltk.RecursiveDescentParser(grammar1)
# for tree in rd_parser.parse(tokens):
#     print(tree)
#     tree.pretty_print()


grammar2 = grammar.FeatureGrammar.fromstring("""
% start S
  S[SEM=<?vp(?np)>] -> NP[SEM=?np] VP[SEM=?vp]
  VP[SEM=?v] -> IV[SEM=?v]
  NP[SEM=<cyril>] -> "Cyril"
  IV[SEM=<\\x.barks(x)>] -> "barks"
  """)

#\\x.barks(x)(cyril)
#\\cyril.barks(cyril)
#barks(cyril)


parser = parse.FeatureEarleyChartParser(grammar2)
text = "Cyril barks"
tokens = text.split()
trees = parser.parse(tokens)
for tree in trees:
    print(tree)


#
#try:
#    text = "cyril barks"
#    tokens = text.split()
#    trees = parser.parse(tokens)
#    for tree in trees: 
#        print(tree)
#except ValueError:
#    print("No se reconoce como oración del lenguaje")
#    

#parser = parse.FeatureEarleyChartParser(grammar2)
#text = "Cyril barks"
#tokens = text.split()
#tree = parser.parse_one(tokens)
#print(tree)
#print(tree.label()['SEM'])
    

#cp = load_parser('sem0.fcfg', trace=0)
#tokens = 'John walks'.split()
#for tree in cp.parse(tokens):
#    print(tree.label()['sem'])
    #print(tree)


# reproduce_video('flans')
#reproduce_cancion(flans)
#reproduce(video,flans)



# ejemplos avanzados
#cp = load_parser('sem1.fcfg', trace=0)
#tokens = 'a dog barks'.split()
#for tree in cp.parse(tokens):
#    print(tree)
# 
#cp = load_parser('sem2.fcfg', trace=0)
#tokens = 'John sees Mary'.split()
#for tree in cp.parse(tokens):
#    print(tree)
    
#cp = load_parser('sem3.fcfg', trace=0)
#tokens = 'John walks'.split()
#for tree in cp.parse(tokens):
#    print(tree)
    
    