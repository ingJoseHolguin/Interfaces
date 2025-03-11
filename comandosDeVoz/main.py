import nltk
from nltk import grammar, parse
from nltk import load_parser
from nltk.parse.generate import generate
import pywhatkit
from SpeechRecognition import audio, recognition
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
    # Definición de la gramática corregida
    grammar_text = """
    % start S
    S[SEM=<?vp(?np)>] -> NP[SEM=?np] VP[SEM=?vp]
    VP[SEM=?v] -> IV[SEM=?v]
    NP[SEM=<reproduce>] -> "reproduce"
    IV[SEM=<\\x.temerarios(x)>] -> "temerarios"
    """

    # Cargar gramática y parser
    grammar = grammar.FeatureGrammar.fromstring(grammar_text)
    parser = parse.FeatureEarleyChartParser(grammar)

    print("🎙️ Habla ahora... Reconociendo semántica")
    lite.text_to_speech("Habla ahora...")
    
    # Obtener la entrada de voz y convertir a texto
    # text = recognition.trascribe_from_file(audio.file_voice()).strip()
    text = "Reproduce temerarios"
    print("Entrada reconocida:", text.lower())

    # Tokenizar la entrada y asegurar que esté en minúsculas
    tokens = text.lower().split()
    print("Tokens:", tokens)

    try:
        trees = parser.parse(tokens)
        for tree in trees:
            print(tree)
            lite.text_to_speech("Reproduciendo temerarios")
            print("🎵 Reproduciendo: temerarios")
            time.sleep(1)
            pywhatkit.playonyt("temerarios")
        
    except ValueError as e:
        lite.text_to_speech("Comando no reconocido.")
        print(f"⚠️ Error: {e}")


    

   


    

    if trees:
        # Si se encontraron árboles sintácticos, la entrada cumple con la gramática
        for tree in trees:
            print("Árbol sintáctico generado:", tree)
            # Ejecutar acción si se cumple la gramática
            if "temerarios" in tree.label()['SEM']:  # Verifica si contiene 'temerarios'
                lite.text_to_speech("Reproduciendo temerarios")
                print("🎵 Reproduciendo: temerarios")
                pywhatkit.playonyt("temerarios")
    else:
        # Si no se encontró ninguna estructura válida en la gramática
        lite.text_to_speech("No se reconoce el comando.")
        print("⚠️ No se reconoce la entrada.")