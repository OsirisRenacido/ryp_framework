# Modelo creado por Joaquin Rosales Flores, psicologo.
# =====================================================
# RYP WRITER GRAMMAR - MOTOR SINTÁCTICO
# Definición de andamiajes gramaticales y concordancia en español
# =====================================================

class GrammarTemplate:
    """
    Representa un esqueleto oracional con ranuras (slots) gramaticales
    y una trayectoria SAM sugerida para cada ranura.
    """
    def __init__(self, name, slots, trajectory_profile):
        self.name = name
        self.slots = slots  # ej. ["ART", "NOUN", "V_AUX", "ART", "NOUN", "ADJ"]
        # Perfil dominante esperado por ranura: 'S', 'A', 'M'
        self.trajectory_profile = trajectory_profile 
        
    def __repr__(self):
        return f"Template({self.name}, slots={len(self.slots)})"


# Banco de andamiajes gramaticales predefinidos para RYP Writer
TEMPLATES = [
    # T1: Definición conceptual (M-dominante)
    GrammarTemplate(
        name="definicion_directa",
        slots=["ART", "NOUN", "V_AUX", "ART", "NOUN", "PREP", "ART", "NOUN", "ADJ"],
        trajectory_profile=["M", "M", "M", "A", "A", "M", "S", "S", "M"]
    ),
    # T2: Transición relacional (A-dominante)
    GrammarTemplate(
        name="transicion_vinculo",
        slots=["ART", "NOUN", "VERB", "ART", "NOUN", "CONJ", "VERB", "ART", "NOUN"],
        trajectory_profile=["A", "A", "A", "A", "A", "A", "S", "M", "M"]
    ),
    # T3: Reflexión existencial (S-dominante)
    GrammarTemplate(
        name="reflexion_sentido",
        slots=["ART", "NOUN", "PREP", "ART", "NOUN", "V_AUX", "ART", "NOUN", "ADJ"],
        trajectory_profile=["S", "S", "S", "A", "A", "S", "S", "S", "S"]
    ),
    # T4: Cierre o colapso estructural
    GrammarTemplate(
        name="cierre_sintesis",
        slots=["ADV", "ART", "NOUN", "VERB", "ART", "NOUN", "PREP", "ART", "NOUN"],
        trajectory_profile=["M", "M", "M", "M", "M", "A", "A", "S", "M"]
    ),
    # T5: Explicación de dinámica interna
    GrammarTemplate(
        name="explicacion_dinamica",
        slots=["ART", "NOUN", "V_AUX", "ADJ", "CONJ", "VERB", "ART", "NOUN", "ADJ"],
        trajectory_profile=["M", "M", "M", "M", "A", "A", "A", "S", "S"]
    )
]


def is_feminine_noun(noun):
    """Detecta de forma heurística si un sustantivo en español es femenino."""
    n = noun.lower().strip()
    
    # Excepciones manuales del core de RYP
    fem_exceptions = {
        "mente", "alma", "experiencia", "relacion", "relación", "tension", "tensión",
        "dinámica", "dinamica", "forma", "vida", "consciencia", "conciencia", "potencia",
        "comprension", "comprensión", "orientacion", "orientación", "clausura", 
        "trayectoria", "entropía", "entropia", "desorganización", "desorganizacion",
        "cohesion", "cohesión", "cultura", "identidad", "memoria", "percepción", 
        "percepcion", "imaginación", "imaginacion", "mentalización", "mentalizacion",
        "reentrada", "estructura", "unidad"
    }
    if n in fem_exceptions:
        return True
        
    masc_exceptions = {"cuerpo", "sistema", "cristal", "símbolo", "simbolo", "lenguaje", "atractor"}
    if n in masc_exceptions:
        return False

    # Heurísticas por terminaciones
    if n.endswith(("a", "ción", "cion", "sión", "sion", "dad", "tad", "encia", "ancia", "eza", "ía")):
        return True
    return False


def post_process_sentence(words, pos_tags):
    """
    Ajusta el género, número, concordancia gramatical y reglas fonológicas del español.
    Recibe:
      - words: lista de palabras generadas
      - pos_tags: lista de slots gramaticales correspondientes (ej. "ART", "NOUN")
    """
    if not words:
        return ""
        
    result = list(words)
    n_words = len(result)
    
    # Mapeo de conjugaciones para concordancia sujeto-verbo
    singular_to_plural = {
        "es": "son", "era": "eran", "fue": "fueron",
        "puede": "pueden", "debe": "deben", "tiene": "tienen",
        "constituye": "constituyen", "representa": "representan",
        "parece": "parecen", "hace": "hacen", "implica": "implican",
        "existe": "existen", "está": "están", "esta": "están",
        "organiza": "organizan", "sostiene": "sostienen", "activa": "activan",
        "observa": "observan", "reduce": "reducen", "cambia": "cambian",
        "relaciona": "relacionan", "emerge": "emergen", "desarrolla": "desarrollan",
        "expresa": "expresan", "integra": "integran", "equilibra": "equilibran",
        "transforma": "transforman", "limita": "limitan", "colapsa": "colapsan",
        "rota": "rotan", "fluye": "fluyen", "surge": "surgen", "contiene": "contienen",
        "afecta": "afectan", "actúa": "actúan", "siente": "sienten", "piensa": "piensan",
        "vincula": "vinculan", "comprende": "comprenden", "orienta": "orientan",
        "estabiliza": "estabilizan", "desorganiza": "desorganizan", "percibe": "perciben",
        "imagina": "imaginan", "mentaliza": "mentalizan", "reentra": "reentran",
        "conecta": "conectan", "comunica": "comunican", "responde": "responden",
        "genera": "generan", "concreta": "concretan"
    }
    plural_to_singular = {v: k for k, v in singular_to_plural.items()}

    for i in range(n_words):
        word = result[i].lower()
        tag = pos_tags[i]
        
        # 1. Ajuste de Artículos según el sustantivo siguiente (género y número)
        if tag == "ART" and i + 1 < n_words:
            # Buscar el sustantivo más cercano hacia adelante
            noun_word = None
            for j in range(i + 1, n_words):
                if pos_tags[j] == "NOUN":
                    noun_word = result[j]
                    break
            
            if noun_word:
                is_fem = is_feminine_noun(noun_word)
                is_plural = noun_word.lower().endswith("s") and not noun_word.lower().endswith("crisis")
                is_definite = word in {"el", "la", "los", "las"}
                
                if is_definite:
                    if is_plural:
                        result[i] = "las" if is_fem else "los"
                    else:
                        result[i] = "la" if is_fem else "el"
                else:
                    if is_plural:
                        result[i] = "unas" if is_fem else "unos"
                    else:
                        result[i] = "una" if is_fem else "un"

        # 2. Concordancia de Adjetivos con el sustantivo anterior
        elif tag == "ADJ":
            # Buscar el sustantivo más cercano hacia atrás
            noun_word = None
            for j in range(i - 1, -1, -1):
                if pos_tags[j] == "NOUN":
                    noun_word = result[j]
                    break
            
            if noun_word:
                is_fem = is_feminine_noun(noun_word)
                is_plural = noun_word.lower().endswith("s") and not noun_word.lower().endswith("crisis")
                
                # Ajustar género
                if is_fem:
                    if word.endswith("o"):
                        word = word[:-1] + "a"
                    elif word.endswith("os"):
                        word = word[:-2] + "as"
                    elif word.endswith("ico"):
                        word = word[:-3] + "ica"
                    elif word.endswith("icos"):
                        word = word[:-4] + "icas"
                    elif word.endswith("oso"):
                        word = word[:-3] + "osa"
                    elif word.endswith("osos"):
                        word = word[:-4] + "osas"
                    elif word.endswith("afectivo"):
                        word = "afectiva"
                    elif word.endswith("sistémico"):
                        word = "sistémica"
                    elif word.endswith("dinámico"):
                        word = "dinámica"
                else:
                    if word.endswith("a") and not word.endswith(("eta", "ista", "ema")):
                        # Restaurar masculino si se cambió accidentalmente
                        if word.endswith("ica") and not word.endswith("clínica"):
                            word = word[:-3] + "ico"
                        elif word.endswith("osa"):
                            word = word[:-3] + "oso"
                        elif word.endswith("a"):
                            word = word[:-1] + "o"

                # Ajustar número del adjetivo
                if is_plural:
                    if not word.endswith("s"):
                        if word.endswith(("a", "e", "o")):
                            word = word + "s"
                        elif word.endswith(("al", "ar", "el", "il")):
                            word = word + "es"
                else:
                    if word.endswith("s") and not word.endswith(("crisis", "lunes", "martes", "miercoles", "miércoles", "jueves", "viernes")):
                        if word.endswith("es") and len(word) > 4:
                            word = word[:-2]
                        elif word.endswith("s"):
                            word = word[:-1]

                result[i] = word

        # 3. Concordancia Sujeto-Verbo
        elif tag in {"VERB", "V_AUX"}:
            # Buscar el sustantivo sujeto (el sustantivo más cercano antes del verbo)
            noun_word = None
            for j in range(i - 1, -1, -1):
                if pos_tags[j] == "NOUN":
                    noun_word = result[j]
                    break
            
            if noun_word:
                is_plural = noun_word.lower().endswith("s") and not noun_word.lower().endswith("crisis")
                if is_plural:
                    if word in singular_to_plural:
                        result[i] = singular_to_plural[word]
                else:
                    if word in plural_to_singular:
                        result[i] = plural_to_singular[word]

        # 4. Reglas fonológicas del español (Conjunción "y" -> "e", "o" -> "u")
        elif word == "y" and i + 1 < n_words:
            next_word = result[i+1].lower()
            if next_word.startswith(("i", "hi")) and not next_word.startswith(("hia", "hie", "hio")):
                result[i] = "e"
        elif word == "o" and i + 1 < n_words:
            next_word = result[i+1].lower()
            if next_word.startswith(("o", "ho")):
                result[i] = "u"

    # Capitalizar primera palabra y agregar punto final
    sentence = " ".join(result).strip()
    if sentence:
        sentence = sentence[0].upper() + sentence[1:]
        if not sentence.endswith((".", "!", "?")):
            sentence += "."
            
    return sentence


if __name__ == "__main__":
    print("RYP Writer Grammar inicializado.")
    print(f"Plantillas cargadas: {[t.name for t in TEMPLATES]}")
    
    # Test rápido de concordancia
    words = ["el", "estructura", "es", "un", "vinculo", "sistémico"]
    tags = ["ART", "NOUN", "V_AUX", "ART", "NOUN", "ADJ"]
    print("Antes:", " ".join(words))
    print("Después:", post_process_sentence(words, tags))
