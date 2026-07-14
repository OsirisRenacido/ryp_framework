# Modelo creado por Joaquin Rosales Flores, psicologo.
# =====================================================
# RYP WRITER ENGINE - MOTOR GENERATIVO
# Selección probabilística y optimización de trayectorias SAM
# =====================================================

import os
import re
import numpy as np
from collections import defaultdict
from pathlib import Path

import ryp_framework.language as lang
from .lexicon import RYPWriterLexicon
from .grammar import TEMPLATES, post_process_sentence

class RYPWriterEngine:
    """
    Motor que genera enunciados seleccionando palabras del lexicón RYP
    que optimizan el ajuste con una trayectoria SAM y coherencia sintáctica.
    """
    def __init__(self):
        self.writer_lexicon = RYPWriterLexicon()
        self.transitions = defaultdict(lambda: defaultdict(int))
        self._build_transitions_from_corpus()
        
    def _build_transitions_from_corpus(self):
        """
        Lee los archivos de documentación locales (README, QUICK_START, etc.)
        para construir un modelo de bigramas estilístico del autor.
        """
        from ryp_framework.utils.paths import get_resource_root
        workspace_root = get_resource_root()
        corpus_files = [
            workspace_root / "README.md",
            workspace_root / "QUICK_START.md",
            workspace_root / "ESTADO_IMPLEMENTACION_RESUMEN.md"
        ]
        
        token_pattern = re.compile(r'\b\w+\b')
        
        for file_path in corpus_files:
            if not file_path.exists():
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read().lower()
                    # Reemplazar acentos para simplificar transiciones
                    text = lang.strip_diacritics(text)
                    tokens = token_pattern.findall(text)
                    
                    for i in range(len(tokens) - 1):
                        w1 = tokens[i]
                        w2 = tokens[i+1]
                        self.transitions[w1][w2] += 1
            except Exception as e:
                print(f"[Engine Warning] Error leyendo corpus {file_path.name}: {e}")
                
        # Normalizar transiciones internas del lexicón para palabras clave si no hay datos
        # Asegurar conexiones lógicas básicas
        default_connections = {
            "el": ["sentido", "vinculo", "vínculo", "cuerpo", "proceso", "sistema", "cristal", "equilibrio"],
            "la": ["mente", "estructura", "emocion", "emoción", "experiencia", "unidad", "relacion", "relación"],
            "un": ["vinculo", "vínculo", "proceso", "sistema", "cristal", "atractor"],
            "una": ["estructura", "emocion", "emoción", "experiencia", "unidad", "dinámica", "tension"],
            "es": ["un", "una", "necesario", "primordial", "la", "el", "estable"],
            "son": ["las", "los", "estructuras", "vinculos", "procesos"],
            "sostiene": ["la", "el", "una", "un", "vida", "experiencia", "estructura"],
            "organiza": ["el", "la", "los", "las", "sentido", "cambio", "cuerpo"],
            "vinculo": ["de", "con", "y", "entre"],
            "vínculo": ["de", "con", "y", "entre"],
            "estructura": ["de", "del", "que", "para", "sistemica", "sistémica"],
            "sentido": ["de", "para", "que", "organiza", "sostiene"],
            "mente": ["y", "organiza", "sostiene", "se", "es"]
        }
        for w1, next_words in default_connections.items():
            for w2 in next_words:
                self.transitions[w1][w2] += 5

    def get_bigram_score(self, prev_word, current_word):
        """Calcula el score de transición del bigrama entre 0 y 1."""
        if not prev_word:
            return 0.5
        w1 = lang.strip_diacritics(prev_word.lower())
        w2 = lang.strip_diacritics(current_word.lower())
        
        followers = self.transitions.get(w1)
        if not followers:
            return 0.1
            
        total = sum(followers.values())
        if total == 0:
            return 0.1
            
        return followers.get(w2, 0) / total

    def _get_target_sam_vector(self, slot_label, global_target):
        """Mapea una etiqueta SAM ('S', 'A', 'M') a un vector numérico mezclado con el target global."""
        mapping = {
            'S': np.array([0.70, 0.15, 0.15]),
            'A': np.array([0.15, 0.70, 0.15]),
            'M': np.array([0.15, 0.15, 0.70])
        }
        slot_vec = mapping.get(slot_label, np.array([1/3, 1/3, 1/3]))
        
        # Mezcla balanceada: 60% peso del slot específico, 40% del atractor global del texto
        return 0.6 * slot_vec + 0.4 * global_target

    def generate_sentence(self, target_sam, route_type="definicion_directa", temperature=0.15):
        """
        Genera una oración optimizando la trayectoria SAM y la coherencia del corpus.
        
        Parámetros:
          - target_sam: vector final deseado [S, A, M]
          - route_type: nombre del andamio gramatical a usar
          - temperature: introduce variedad estocástica controlada [0.0 = codicioso]
        """
        # 1. Encontrar la plantilla
        template = next((t for t in TEMPLATES if t.name == route_type), TEMPLATES[0])
        global_target = np.array(target_sam, dtype=float)
        
        words = []
        prev_word = None
        used_words = set()
        
        # 2. Rellenar las ranuras secuencialmente
        for step, pos_tag in enumerate(template.slots):
            slot_sam_profile = template.trajectory_profile[step]
            step_target_sam = self._get_target_sam_vector(slot_sam_profile, global_target)
            
            # Obtener candidatos para esta categoría gramatical
            candidates = self.writer_lexicon.get_words_by_pos(pos_tag)
            
            if not candidates:
                # Fallback defensivo por si un POS no tiene palabras en el banco
                fallback_word = "y" if pos_tag == "CONJ" else "es"
                words.append(fallback_word)
                prev_word = fallback_word
                continue
                
            scored_candidates = []
            
            for word, word_sam in candidates:
                # Penalización por repetición cercana
                rep_penalty = -10.0 if word in used_words else 0.0
                
                # Componente 1: Cercanía al vector SAM objetivo del paso
                dist_sam = np.linalg.norm(word_sam - step_target_sam)
                sam_score = 1.0 / (1.0 + dist_sam) # Rango [0, 1]
                
                # Componente 2: Coherencia contextual (Bigramas)
                bigram_score = self.get_bigram_score(prev_word, word)
                
                # Suma ponderada de scores
                # lambda1 = 0.5 (peso SAM), lambda2 = 0.5 (coherencia estilística)
                score = 0.5 * sam_score + 0.5 * bigram_score + rep_penalty
                scored_candidates.append((word, score))
                
            # Ordenar candidatos
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            
            # 3. Selección con temperatura
            if temperature == 0.0 or len(scored_candidates) == 1:
                selected_word = scored_candidates[0][0]
            else:
                # Tomar los top 5 mejores y seleccionar usando probabilidad suavizada
                top_k = scored_candidates[:5]
                words_subset = [x[0] for x in top_k]
                scores_subset = np.array([x[1] for x in top_k])
                
                # Aplicar softmax con temperatura
                scores_subset = scores_subset - np.max(scores_subset) # Estabilizar
                exp_scores = np.exp(scores_subset / max(temperature, 1e-4))
                probs = exp_scores / np.sum(exp_scores)
                
                selected_word = np.random.choice(words_subset, p=probs)
                
            words.append(selected_word)
            used_words.add(selected_word)
            prev_word = selected_word
            
        # 4. Postprocesamiento sintáctico (concordancias de género y reglas gramaticales)
        processed_sentence = post_process_sentence(words, template.slots)
        return processed_sentence, template.slots

    def generate_paragraph(self, target_sam, count_sentences=3, temperature=0.15, keywords=None, trajectory=None):
        """
        Genera un párrafo multi-oracional encadenando distintas plantillas gramaticales
        y opcionalmente siguiendo una trayectoria SAM guiada paso a paso.

        Parámetros:
          - target_sam: vector SAM objetivo [S, A, M] para el párrafo.
          - count_sentences: cantidad de oraciones a generar (por defecto 3).
          - temperature: variabilidad estocástica para la selección de palabras.
          - keywords: lista opcional de palabras clave (reservado para uso futuro).
          - trajectory: lista opcional de letras ['S', 'A', 'M'] que guían el foco de cada oración.

        Retorna:
          - (paragraph_text, sentence_details) donde paragraph_text es el párrafo
            completo y sentence_details es una lista de diccionarios con las claves
            'sentence', 'template', 'slots' y 'target_sam'.
        """
        if trajectory and len(trajectory) > 0:
            count_sentences = len(trajectory)

        # Definir la secuencia de plantillas según la cantidad de oraciones solicitadas
        if count_sentences <= 1:
            template_sequence = ["definicion_directa"]
        elif count_sentences == 2:
            template_sequence = ["definicion_directa", "cierre_sintesis"]
        elif count_sentences == 3:
            template_sequence = ["definicion_directa", "transicion_vinculo", "cierre_sintesis"]
        else:
            # Para 4+ oraciones: inicio, transiciones intermedias, cierre
            template_sequence = ["definicion_directa", "transicion_vinculo"]
            for _ in range(count_sentences - 3):
                template_sequence.append("explicacion_dinamica")
            template_sequence.append("cierre_sintesis")

        sentence_details = []
        global_target = np.array(target_sam, dtype=float)

        mapping = {
            'S': np.array([0.70, 0.15, 0.15]),
            'A': np.array([0.15, 0.70, 0.15]),
            'M': np.array([0.15, 0.15, 0.70])
        }

        for idx, template_name in enumerate(template_sequence):
            # Determinar el target SAM de esta oración
            if trajectory and idx < len(trajectory):
                letter = trajectory[idx].upper()
                slot_vec = mapping.get(letter, np.array([1/3, 1/3, 1/3]))
                # Mezcla balanceada: 60% peso del slot específico, 40% del atractor global del texto
                step_target = 0.6 * slot_vec + 0.4 * global_target
                step_target = (step_target / np.sum(step_target)).tolist()
            else:
                step_target = target_sam

            sentence_text, slots = self.generate_sentence(
                step_target,
                route_type=template_name,
                temperature=temperature,
            )
            sentence_details.append({
                "sentence": sentence_text,
                "template": template_name,
                "slots": slots,
                "target_sam": step_target
            })

        paragraph_text = " ".join(detail["sentence"] for detail in sentence_details)
        return paragraph_text, sentence_details

    def reload_lexicon(self):
        """Re-instancia el lexicón para incorporar palabras añadidas recientemente."""
        self.writer_lexicon = RYPWriterLexicon()


if __name__ == "__main__":
    from pathlib import Path
    engine = RYPWriterEngine()
    print("Engine cargado. Transiciones de bigramas compiladas.")
    
    # Test de generación
    target = [0.35, 0.45, 0.20]
    sentence, slots = engine.generate_sentence(target, route_type="definicion_directa")
    print(f"Objetivo SAM: {target}")
    print(f"Oración Generada: '{sentence}'")
