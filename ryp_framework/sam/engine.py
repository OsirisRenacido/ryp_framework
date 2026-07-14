"""
RYP_MATRIZ_SAM_DYNAMIC_ENGINE.py
=================================

Motor dinámico de conjugación SAM.

Operación clave:
  Reemplaza palabra X → Calcula nueva SAM → Reorganiza todo → Retorna cambios

Implementa los 4 cierres como MODOS de cálculo diferentes.

Autor: Joaquín Rosales Flores
Fecha: 2026-05-19
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum


class ClosureType(Enum):
    """Los 4 cierres recursivos del lenguaje occidental."""
    OSCURO = "oscuro"        # M puro
    SOMBRA = "sombra"        # M dominante, A limitado
    LUMINOSO = "luminoso"    # S-A-M equilibrado
    VACIO = "vacio"          # S puro


@dataclass
class ClosureWeights:
    """Pesos para cálculos en cada cierre."""
    s_weight: float
    a_weight: float
    m_weight: float
    
    def normalize(self) -> "ClosureWeights":
        """Normaliza pesos a suma=1."""
        total = self.s_weight + self.a_weight + self.m_weight
        if total == 0:
            return ClosureWeights(0.33, 0.33, 0.34)
        return ClosureWeights(
            self.s_weight / total,
            self.a_weight / total,
            self.m_weight / total
        )


class DynamicConjugationEngine:
    """
    Motor dinámico de conjugación en espacio SAM.
    
    Permite:
    - Reemplazar palabra y ver reorganización completa
    - Cambiar entre modos de cierre
    - Calcular colocaciones dinámicas
    """
    
    # Pesos para los 4 cierres
    CLOSURE_WEIGHTS = {
        ClosureType.OSCURO: ClosureWeights(0.0, 0.0, 1.0),
        ClosureType.SOMBRA: ClosureWeights(0.3, 0.5, 0.9),
        ClosureType.LUMINOSO: ClosureWeights(0.9, 0.9, 0.9),
        ClosureType.VACIO: ClosureWeights(0.8, 0.0, 0.2),
    }
    
    def __init__(self, universal_table_path: str = None,
                 chains_path: str = None):
        """
        Args:
            universal_table_path: ruta a TABLA_UNIVERSAL_SAM_2026-05-19.json
            chains_path: ruta a DICCIONARIO_CADENAS_SAM_2026-05-19.json
        """
        self.universal_table_path = universal_table_path or self._find_universal_table()
        self.chains_path = chains_path or self._find_chains_file()
        
        self.universal_table = self._load_universal_table()
        self.chains = self._load_chains()
        self.current_closure = ClosureType.OSCURO
        
    def _find_universal_table(self) -> str:
        """Busca archivo de tabla universal."""
        candidates = [
            Path('07_DATOS_Y_CORPUS/TABLA_UNIVERSAL_SAM_2026-05-19.json'),
            Path('TABLA_UNIVERSAL_SAM_2026-05-19.json'),
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        raise FileNotFoundError("TABLA_UNIVERSAL_SAM_2026-05-19.json no encontrado")
    
    def _find_chains_file(self) -> str:
        """Busca archivo de cadenas."""
        candidates = [
            Path('07_DATOS_Y_CORPUS/DICCIONARIO_CADENAS_SAM_2026-05-19.json'),
            Path('DICCIONARIO_CADENAS_SAM_2026-05-19.json'),
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        raise FileNotFoundError("DICCIONARIO_CADENAS_SAM_2026-05-19.json no encontrado")
    
    def _load_universal_table(self) -> Dict[str, Any]:
        """Carga tabla universal."""
        print(f"Cargando tabla universal desde: {self.universal_table_path}")
        with open(self.universal_table_path, 'r', encoding='utf-8') as f:
            table = json.load(f)
        print(f"  → {len(table['clusters'])} clusters cargados")
        return table
    
    def _load_chains(self) -> Dict[str, Any]:
        """Carga cadenas semánticas."""
        print(f"Cargando cadenas desde: {self.chains_path}")
        with open(self.chains_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  → {data['metadata']['total_words']} palabras disponibles")
        return data['chains']
    
    def set_closure_mode(self, closure: ClosureType) -> None:
        """Cambia modo de cierre activo."""
        self.current_closure = closure
        print(f"Modo de cierre cambiado a: {closure.value.upper()}")
    
    def _euclidean_distance(self, sam1: List[float], sam2: List[float]) -> float:
        """Distancia euclidiana."""
        return float(np.sqrt(sum((a - b) ** 2 for a, b in zip(sam1, sam2))))
    
    def _weighted_distance(self, sam1: List[float], sam2: List[float],
                          weights: ClosureWeights) -> float:
        """
        Distancia ponderada por pesos del cierre.
        
        En OSCURO: M domina, se ignora S
        En LUMINOSO: igual peso
        Etc.
        """
        weighted_diffs = [
            weights.s_weight * abs(sam1[0] - sam2[0]),
            weights.a_weight * abs(sam1[1] - sam2[1]),
            weights.m_weight * abs(sam1[2] - sam2[2]),
        ]
        return float(np.sqrt(sum(d ** 2 for d in weighted_diffs)))
    
    def find_replacements(self, target_sam: List[float],
                         tolerance: float = 0.15) -> List[Dict[str, Any]]:
        """
        Encuentra palabras que podrían reemplazar un SAM objetivo.
        
        Usa pesos del cierre actual.
        """
        weights = self.CLOSURE_WEIGHTS[self.current_closure].normalize()
        replacements = []
        
        for word, word_data in self.chains.items():
            word_sam = word_data['sam_from_description']
            distance = self._weighted_distance(target_sam, word_sam, weights)
            
            if distance < tolerance:
                replacements.append({
                    'word': word,
                    'sam': word_sam,
                    'distance': round(distance, 3),
                    'category': word_data.get('category', '?'),
                })
        
        return sorted(replacements, key=lambda x: x['distance'])
    
    def replace_and_recalculate(self, old_word: str, new_word: str,
                               affected_words: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Reemplaza una palabra y recalcula dependencias.
        
        Retorna:
        {
            'replaced': {old → new},
            'reorganized': {palabra → {cambios}},
            'closure_impacts': {cierre → cambios esperados}
        }
        """
        
        if old_word not in self.chains:
            return {'error': f"Palabra '{old_word}' no encontrada"}
        
        if new_word not in self.chains:
            return {'error': f"Palabra '{new_word}' no encontrada"}
        
        old_sam = self.chains[old_word]['sam_from_description']
        new_sam = self.chains[new_word]['sam_from_description']
        
        result = {
            'replaced': {
                'old_word': old_word,
                'old_sam': old_sam,
                'new_word': new_word,
                'new_sam': new_sam,
                'closure_active': self.current_closure.value,
            },
            'reorganized': {},
            'analysis': {
                'sam_change': [
                    round(new_sam[i] - old_sam[i], 3) for i in range(3)
                ],
                'direction': self._interpret_sam_change(old_sam, new_sam),
            }
        }
        
        # Si se especifica lista de palabras, calcula cambios en ellas
        if affected_words:
            weights = self.CLOSURE_WEIGHTS[self.current_closure].normalize()
            
            for word in affected_words:
                if word in self.chains:
                    word_sam = self.chains[word]['sam_from_description']
                    
                    # Distancia a la palabra vieja
                    old_distance = self._weighted_distance(word_sam, old_sam, weights)
                    # Distancia a la palabra nueva
                    new_distance = self._weighted_distance(word_sam, new_sam, weights)
                    
                    result['reorganized'][word] = {
                        'old_distance': round(old_distance, 3),
                        'new_distance': round(new_distance, 3),
                        'distance_change': round(new_distance - old_distance, 3),
                        'status': 'closer' if new_distance < old_distance else 'farther',
                    }
        
        return result
    
    def _interpret_sam_change(self, old_sam: List[float], 
                             new_sam: List[float]) -> str:
        """Interpreta dirección del cambio SAM."""
        components = ['S (Narrativa)', 'A (Mediación)', 'M (Acción)']
        changes = []
        
        for i, component in enumerate(components):
            diff = new_sam[i] - old_sam[i]
            if diff > 0.1:
                changes.append(f"↑ {component}")
            elif diff < -0.1:
                changes.append(f"↓ {component}")
        
        return " | ".join(changes) if changes else "Sin cambios significativos"
    
    def conjugate_in_closure(self, word: str, target_closure: ClosureType) -> Dict[str, Any]:
        """
        Busca la forma conjugada de una palabra EN UN CIERRE ESPECÍFICO.
        
        Ejemplo: 
          Palabra: 'corazón' (S=0.7, A=0.6, M=0.5)
          Cierre OSCURO (S=0, A=0, M=1)
          Retorna: Forma que se acerca más a (0, 0, 1)
        """
        if word not in self.chains:
            return {'error': f"Palabra '{word}' no encontrada"}
        
        word_sam = self.chains[word]['sam_from_description']
        closure_info = self.universal_table['closures'][target_closure.value]
        target_sam = closure_info['sam_centroid']
        
        # Encuentra la palabra más cercana al centroide del cierre
        weights = self.CLOSURE_WEIGHTS[target_closure].normalize()
        
        candidates = []
        for candidate_word, candidate_data in self.chains.items():
            candidate_sam = candidate_data['sam_from_description']
            distance = self._weighted_distance(candidate_sam, target_sam, weights)
            
            # Favorece palabras que comparten contexto (mentions)
            word_mentions = set(self.chains[word].get('mentions', []))
            candidate_mentions = set(candidate_data.get('mentions', []))
            mention_overlap = len(word_mentions & candidate_mentions) / (len(word_mentions | candidate_mentions) + 0.001)
            
            score = distance - mention_overlap * 0.1  # Penaliza distancia, favorece overlap
            candidates.append({
                'word': candidate_word,
                'sam': candidate_sam,
                'distance_to_closure': round(distance, 3),
                'mention_overlap': round(mention_overlap, 3),
                'score': round(score, 3),
            })
        
        candidates = sorted(candidates, key=lambda x: x['score'])
        
        return {
            'original_word': word,
            'original_sam': word_sam,
            'target_closure': target_closure.value,
            'closure_centroid': target_sam,
            'conjugations': candidates[:5],  # Top 5 opciones
        }
    
    def color_encode(self, sam: List[float]) -> str:
        """
        Codifica SAM como color (ROJO/NARANJA/AMARILLO).
        
        ROJO (S dominante): S > 0.6
        NARANJA (A dominante): A > 0.6
        AMARILLO (M dominante): M > 0.6
        GRIS (equilibrio): ninguno > 0.6
        """
        s, a, m = sam
        
        if s > 0.6 and s >= a and s >= m:
            return "ROJO (S)"
        elif a > 0.6 and a >= s and a >= m:
            return "NARANJA (A)"
        elif m > 0.6 and m >= s and m >= a:
            return "AMARILLO (M)"
        else:
            return "GRIS (Equilibrio)"
    
    def render_word_card(self, word: str) -> str:
        """Renderiza tarjeta visual de una palabra."""
        if word not in self.chains:
            return f"Palabra '{word}' no encontrada"
        
        data = self.chains[word]
        sam = data['sam_from_description']
        color = self.color_encode(sam)
        
        card = f"""
┌─────────────────────────────────────┐
│ PALABRA: {word.upper():30s}│
├─────────────────────────────────────┤
│ SAM: S={sam[0]:.2f} | A={sam[1]:.2f} | M={sam[2]:.2f}
│ Color: {color}
│ Categoría: {data.get('category', '?')}
│ Descrip: {data.get('description', '')[:40]}...
│ Menciona: {', '.join(data.get('mentions', [])[:3])}
└─────────────────────────────────────┘
"""
        return card


def main():
    """Script de demostración."""
    print("=== MOTOR DINÁMICO DE CONJUGACIÓN SAM ===\n")
    
    engine = DynamicConjugationEngine()
    
    # Demo 1: Cambiar modo de cierre
    print("\n--- Demo 1: Cambiar modo de cierre ---")
    for closure in ClosureType:
        engine.set_closure_mode(closure)
    
    # Demo 2: Reemplazar una palabra
    print("\n--- Demo 2: Reemplazar palabra ---")
    test_word = 'corazon'
    if test_word in engine.chains:
        print(engine.render_word_card(test_word))
        
        # Encuentra reemplazos en OSCURO
        engine.set_closure_mode(ClosureType.OSCURO)
        target_sam = engine.chains[test_word]['sam_from_description']
        replacements = engine.find_replacements(target_sam, tolerance=0.2)
        print(f"Reemplazos posibles en OSCURO: {[r['word'] for r in replacements[:3]]}")
    
    # Demo 3: Conjugar en cierre diferente
    print("\n--- Demo 3: Conjugar en cierre LUMINOSO ---")
    if test_word in engine.chains:
        conjugations = engine.conjugate_in_closure(test_word, ClosureType.LUMINOSO)
        if 'conjugations' in conjugations:
            print(f"Formas conjugadas en LUMINOSO:")
            for conj in conjugations['conjugations'][:3]:
                print(f"  {conj['word']}: {conj['score']}")
    
    print("\n✓ Demostraciones completadas")


if __name__ == '__main__':
    main()
