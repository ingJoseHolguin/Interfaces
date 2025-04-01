import sys
import os
import nltk
from nltk import grammar, parse
from nltk import load_parser
from nltk.parse.generate import generate
import pywhatkit
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SpeechRecognition import lite as recognition_lite
from TextToSpeech import lite
import time 

""" Analisis semantico
    S: Sentence (Oración)
    NP: Noun Phrase (Frase nominal) - Representa el sujeto o el objeto directo de la oración.
    VP: Verb Phrase (Frase verbal) - Representa la acción o predicado de la oración.
    PP: Prepositional Phrase (Frase preposicional) Representa una frase que comienza con una preposición, seguida generalmente por una frase nominal (por ejemplo, "en la casa").
    Det: Determiner (Determinante) - Representa palabras que determinan o limitan al sustantivo
    N: Noun (Sustantivo) - Representa un sustantivo
    V: Verb (Verbo)
    IV: Intransitive Verb (Verbo intransitivo) - Verbo que no requiere un objeto directo para completar su significado
    VT: Transitive Verb (Verbo transitivo) - Verbo que requiere un objeto directo (por ejemplo, "ver", "comer", "sostener").
    Adj: Adjective (Adjetivo) - Representa un adjetivo que modifica un sustantivo (por ejemplo, "grande", "rojo").
    Adv: Adverb (Adverbio) - Representa un adverbio que modifica un verbo, adjetivo u otro adverbio
    C: Complement (Complemento) - Representa un complemento de alguna categoría, como el complemento de un verbo.
    Comp: Complementizer (Complementizador) - Es una palabra que introduce una oración subordinada (por ejemplo, "que", "si").
    Conj: Conjunction (Conjunción) - Representa una palabra que conecta oraciones o frases (por ejemplo, "y", "pero", "aunque").
 """

if __name__ == "__main__": 
    # Definición de la gramática
    # grammar_text = """
    # % start S
    # S[SEM=<?vp(?np)>] -> NP[SEM=?np] VP[SEM=?vp]
    # VP[SEM=?v] -> IV[SEM=?v]
    # NP[SEM=<temerarios>] -> "temerarios"
    # V[SEM=<\\x.reproduce(x)>] -> "reproduce"
    # """

    # grammar_text = """
    # % start S
    # S[SEM=<?vp(?np)>] -> NP[SEM=?np] VP[SEM=?vp]
    # VP[SEM=<?v(?np)>] -> V[SEM=?v] NP[SEM=?np]
    # NP[SEM=<computador>] -> "computador"
    # NP[SEM=<temerarios>] -> "temerarios" 
    # V[SEM=<\\x.reproduce(x)>] -> "reproduce"
    # """  #com

    # Estructura básica: S -> NP VP

    grammar_text = """
    % start S
    S[SEM=<?vp(?np)>] -> NP[SEM=?np] VP[SEM=?vp]
    VP[SEM=<\\x.?v(x, ?comp)>] -> TV[SEM=?v] COMP[SEM=?comp]
    NP[SEM=<computador>] -> "computador"
    TV[SEM=<\\x\\y.reproduce(x,y)>] -> "reproduce"
    VP[SEM=<\\x.?v(x, ?comp)>] -> TV[SEM=?v] COMP[SEM=?comp]
    COMP[SEM=<temerarios>] -> "temerarios"

    """

    grammar = grammar.FeatureGrammar.fromstring(grammar_text)
    parser = parse.FeatureEarleyChartParser(grammar)

    print("🎙️ Habla ahora... ")
    ("Habla ahora...")
    
    #text = recognition_lite.recognition_lite()
    #text = "computador Reproduce shakira"
    text = "computador Reproduce temerarios"
    print("Entrada reconocida: >>>", text.lower())

    tokens = text.lower().split()
    print("Tokens:", tokens)
    
    try:
        trees = parser.parse(tokens)
        for tree in trees:
            print(tree)          
            
        sem_string = str(tree.label()['SEM'])
        letters_only = ''.join(char for char in sem_string if char.isalpha())

        lite.text_to_speech(letters_only)

        print(tree.label()['SEM'])
        time.sleep(1)
        pywhatkit.playonyt(tree.label()['SEM'])
        
    except ValueError as e:
        lite.text_to_speech("Comando no reconocido.")
        print(f"⚠️ Error: {e}")