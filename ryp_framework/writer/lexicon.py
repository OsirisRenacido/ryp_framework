# Modelo creado por Joaquin Rosales Flores, psicologo.
# =====================================================
# RYP WRITER LEXICON - CAPA GRAMATICAL
# Clasificación de categorías gramaticales del lexicón RYP
# =====================================================

import numpy as np
import ryp_framework.language as lang

# Listas de palabras funcionales / estructurales en español
ARTICLES = {"el", "la", "los", "las", "un", "una", "unos", "unas"}

PREPOSITIONS = {
    "a", "ante", "bajo", "cabe", "con", "contra", "de", "del", "desde", "durante",
    "en", "entre", "hacia", "hasta", "mediante", "para", "por", "segun", "según",
    "sin", "so", "sobre", "tras", "via", "vía", "durante"
}

CONJUNCTIONS = {
    "y", "o", "pero", "sino", "porque", "pues", "si", "que", "como", "e", "u", "ni", "mas"
}

PRONOUNS = {
    "yo", "tu", "tú", "el", "él", "ella", "ello", "nosotros", "nosotras", "vosotros", 
    "vosotras", "ellos", "ellas", "me", "te", "se", "nos", "os", "lo", "la", "le", 
    "los", "las", "les", "mi", "mí", "mis", "tu", "tus", "su", "sus", "nuestro", 
    "nuestra", "mio", "mío", "tuyo", "suyo", "este", "esta", "esto", "ese", "eso", 
    "aquel", "aquello", "quien", "quién", "cual", "cuál", "que", "qué"
}

AUX_VERBS = {
    "es", "son", "era", "eran", "fue", "fueron", "ser", "siendo", "sido", 
    "puede", "pueden", "debe", "deben", "tiene", "tienen", "constituye", 
    "constituyen", "representa", "representan", "parece", "parecen", 
    "hace", "hacen", "implica", "implican", "existe", "existen", "esta", "está", "están"
}

ADVERBS = {
    "muy", "mas", "más", "bien", "no", "si", "sí", "ya", "ahora", "siempre", 
    "nunca", "hoy", "tambien", "también", "tampoco", "así", "asi", "casi", "solo", "sólo",
    "luego", "después", "despues", "antes", "aquí", "aqui", "allí", "alli", "tan"
}

# Diccionario de excepciones manuales para asegurar precisión en términos core de RYP
CORE_NOUNS = {
    "sentido", "vinculo", "vínculo", "estructura", "emocion", "emoción", "cuerpo", 
    "mente", "alma", "experiencia", "unidad", "relacion", "relación", "movimiento", 
    "cambio", "sujeto", "objeto", "tension", "tensión", "equilibrio", "dinámica", 
    "dinamica", "proceso", "forma", "limite", "límite", "sistema", "cristal", "grupo", 
    "simbolo", "símbolo", "lenguaje", "consciencia", "conciencia", "razon", "razón", 
    "vida", "ser", "espiritu", "espíritu", "potencia", "afecto", "comprension", "comprensión",
    "orientacion", "orientación", "clausura", "atractor", "trayectoria", "entropía",
    "entropia", "desorganización", "desorganizacion", "cohesion", "cohesión", "conflicto",
    "liderazgo", "cultura", "identidad", "memoria", "percepción", "percepcion", "imaginación",
    "imaginacion", "mentalización", "mentalizacion", "reentry", "reentrada", "puente"
}

CORE_VERBS = {
    "organizar", "sostener", "definir", "activar", "observar", "reducir", "cambiar", 
    "relacionar", "emerger", "desarrollar", "expresar", "integrar", "equilibrar", 
    "transformar", "limitar", "colapsar", "rotar", "fluir", "surgir", "contener", 
    "afectar", "actuar", "sentir", "pensar", "vincular", "comprender", "orientar",
    "estabilizar", "desorganizar", "percibir", "imaginar", "mentalizar", "reentrar",
    "conectar", "comunicar", "responder", "generar", "concreta", "concretar"
}

CORE_ADJECTIVES = {
    "significativo", "significativa", "sistemico", "sistémico", "sistemica", "sistémica",
    "dinamico", "dinámico", "dinamica", "dinámica", "afectivo", "afectiva", "cognitivo", 
    "cognitiva", "espiritual", "mental", "corporal", "relacional", "claro", "clara", 
    "oscuro", "oscura", "luminoso", "luminosa", "vacio", "vacío", "vacia", "vacía", 
    "sombra", "interno", "interna", "externo", "externa", "recursivo", "recursiva", 
    "libre", "estable", "inestable", "fragil", "frágil", "primordial", "inmaterial",
    "potencial", "material", "simbolico", "simbólica", "temporal", "cohesivo", 
    "cohesiva", "conflictivo", "conflictiva", "emergente", "persistente", "diferenciado",
    "diferenciada", "estructurado", "estructurada", "clínico", "clinico"
}


def pos_tag_word(word):
    """
    Heurística de clasificación sintáctica (Part of Speech) para español.
    Retorna una de las siguientes etiquetas: 'ART', 'PREP', 'CONJ', 'PRON', 'V_AUX', 'ADV', 'NOUN', 'VERB', 'ADJ'.
    """
    w = word.lower().strip()
    
    if w in ARTICLES:
        return "ART"
    if w in PREPOSITIONS:
        return "PREP"
    if w in CONJUNCTIONS:
        return "CONJ"
    if w in PRONOUNS:
        return "PRON"
    if w in AUX_VERBS:
        return "V_AUX"
    if w in ADVERBS:
        return "ADV"
    
    # Excepciones core explícitas
    if w in CORE_NOUNS:
        return "NOUN"
    if w in CORE_VERBS:
        return "VERB"
    if w in CORE_ADJECTIVES:
        return "ADJ"
        
    # Heurísticas por terminaciones (Sufijos comunes en español)
    if w.endswith(("ar", "er", "ir")) and len(w) > 3:
        return "VERB"
        
    # Sustantivos abstractos comunes
    if w.endswith(("cion", "ción", "sion", "sión", "dad", "tad", "ismo", "miento", "encia", "ancia", "ura", "eza", "ía", "ia", "ez")):
        return "NOUN"
        
    # Adjetivos comunes
    if w.endswith(("ado", "ada", "ido", "ida", "al", "ivo", "iva", "ico", "ica", "oso", "osa", "ente", "ante", "able", "ible", "ar")):
        # Evitar clasificar verbos en 'ar' como adjetivos por la última regla
        if w.endswith("ar") and w.endswith(("ar", "er", "ir")) and len(w) > 3:
            return "VERB"
        return "ADJ"
        
    # Por defecto, clasificar como sustantivo (Noun-default bias en lenguaje conceptual)
    return "NOUN"


class RYPWriterLexicon:
    """
    Gestor gramatical que carga el lexicón de RYP y lo segmenta
    por categorías gramaticales y firmas SAM dominantes.
    """
    
    def __init__(self):
        self.lexicon = lang.SAM_DICT
        self.tagged_lexicon = {}
        
        # Estructuras particionadas por categoría
        self.nouns = []
        self.verbs = []
        self.adjectives = []
        self.adverbs = []
        
        # Palabras estructurales / gramaticales de soporte
        self.articles = sorted(list(ARTICLES))
        self.prepositions = sorted(list(PREPOSITIONS))
        self.conjunctions = sorted(list(CONJUNCTIONS))
        self.pronouns = sorted(list(PRONOUNS))
        self.v_aux = sorted(list(AUX_VERBS))
        self.advs = sorted(list(ADVERBS))
        
        self._tag_and_partition()
        
    def _tag_and_partition(self):
        for term, entry in self.lexicon.items():
            sam = lang.extract_entry_sam(entry)
            pos = pos_tag_word(term)
            
            self.tagged_lexicon[term] = {
                "sam": sam,
                "pos": pos,
                "category": pos_tag_word(term)
            }
            
            item = (term, sam)
            if pos == "NOUN":
                self.nouns.append(item)
            elif pos == "VERB":
                self.verbs.append(item)
            elif pos == "ADJ":
                self.adjectives.append(item)
            elif pos == "ADV":
                self.adverbs.append(item)
            # Las estructurales se manejan por listas estáticas o también se pueden tomar si están en el diccionario
            
        # Añadir palabras de soporte básicas al taggeado para permitir lookup completo
        for word in ARTICLES | PREPOSITIONS | CONJUNCTIONS | PRONOUNS | AUX_VERBS | ADVERBS:
            if word not in self.tagged_lexicon:
                sam = lang.word_to_sam(word)
                self.tagged_lexicon[word] = {
                    "sam": sam,
                    "pos": pos_tag_word(word),
                    "category": pos_tag_word(word)
                }

    def get_words_by_pos(self, pos):
        """Retorna lista de tuplas (palabra, vector_sam) para un POS dado."""
        if pos == "NOUN":
            return self.nouns
        elif pos == "VERB":
            return self.verbs
        elif pos == "ADJ":
            return self.adjectives
        elif pos == "ADV":
            return self.adverbs
        elif pos == "ART":
            return [(w, lang.word_to_sam(w)) for w in self.articles]
        elif pos == "PREP":
            return [(w, lang.word_to_sam(w)) for w in self.prepositions]
        elif pos == "CONJ":
            return [(w, lang.word_to_sam(w)) for w in self.conjunctions]
        elif pos == "PRON":
            return [(w, lang.word_to_sam(w)) for w in self.pronouns]
        elif pos == "V_AUX":
            return [(w, lang.word_to_sam(w)) for w in self.v_aux]
        return []

    def get_closest_word(self, target_sam, pos, vocabulary_subset=None):
        """Encuentra la palabra más cercana al vector objetivo para un POS específico."""
        candidates = vocabulary_subset if vocabulary_subset is not None else self.get_words_by_pos(pos)
        if not candidates:
            return None, 1.0
            
        best_word = None
        min_dist = float('inf')
        
        for word, sam in candidates:
            dist = float(np.linalg.norm(sam - target_sam))
            if dist < min_dist:
                min_dist = dist
                best_word = word
                
        return best_word, min_dist


if __name__ == "__main__":
    writer_lex = RYPWriterLexicon()
    print("RYP Writer Lexicon inicializado con:")
    print(f"- Nombres: {len(writer_lex.nouns)}")
    print(f"- Verbos: {len(writer_lex.verbs)}")
    print(f"- Adjetivos: {len(writer_lex.adjectives)}")
    print(f"- Adverbios: {len(writer_lex.adverbs)}")
    
    # Test rápido de clasificación
    test_words = ["sentido", "organizar", "sistémico", "es", "en", "emoción"]
    for w in test_words:
        print(f"Palabra: '{w}' -> POS: {pos_tag_word(w)}")
