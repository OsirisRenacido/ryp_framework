"""
RYP_MATRIZ_SAM_EXTRACT_CHAINS.py
================================

Extrae cadenas semánticas de definiciones del LEXICON RYP.
Cada definición se descompone en una triada SAM implícita.

Flujo:
  LEXICON entrada → Análisis de descripciones → Cadenas SAM → JSON salida

Autor: Joaquín Rosales Flores
Fecha: 2026-05-19
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np


class SemanticChainExtractor:
    """
    Extrae cadenas semánticas de descripciones en el LEXICON.
    
    Cada descripción contiene:
    - S: narrativa, cualidad, similitud ("es como...", "se refiere a...")
    - A: proceso, mediación ("se produce cuando...", "requiere...")
    - M: acción, propósito ("sirve para...", "realiza...")
    """
    
    # Patrones para identificar componentes SAM en texto
    S_PATTERNS = [
        r'(?:es|son|representa|significa|refiere|denota|alude|evoca|semeja|parece)',
        r'(?:cualidad|propiedad|carácter|naturaleza|esencia)',
        r'(?:similar|parecido|análogo|equivalente|afín)',
    ]
    
    A_PATTERNS = [
        r'(?:proceso|mecanismo|procedimiento|operación|función)',
        r'(?:ocurre|sucede|acaece|acontece|media|interviene)',
        r'(?:causa|produce|genera|provoca|determina)',
        r'(?:requiere|necesita|implica|conlleva|demanda)',
    ]
    
    M_PATTERNS = [
        r'(?:sirve|propósito|fin|objetivo|intención|meta)',
        r'(?:acción|activa|actúa|realiza|ejecuta|desempeña)',
        r'(?:causa|efecto|resultado|consecuencia|outcome)',
        r'(?:impulsa|mueve|conduce|dirige|orienta)',
    ]
    
    def __init__(self, lexicon_path: str = None):
        """
        Inicializa extractor.
        
        Args:
            lexicon_path: ruta a RYP_LEXICON.json (si None, lo busca automático)
        """
        self.lexicon_path = lexicon_path or self._find_lexicon()
        self.lexicon = self._load_lexicon()
        self.chains = {}
        self.word_connections = {}  # Palabra → [palabras mencionadas en su def]
        
    def _find_lexicon(self) -> str:
        """Busca RYP_LEXICON.json en ubicaciones estándar."""
        candidates = [
            Path('07_DATOS_Y_CORPUS/RYP_LEXICON.json'),
            Path('RYP_LEXICON.json'),
            Path.home() / 'Documents/RYP/workspace/07_DATOS_Y_CORPUS/RYP_LEXICON.json',
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        raise FileNotFoundError("RYP_LEXICON.json no encontrado")
    
    def _load_lexicon(self) -> Dict[str, Any]:
        """Carga lexicon desde JSON."""
        print(f"Cargando lexicón desde: {self.lexicon_path}")
        with open(self.lexicon_path, 'r', encoding='utf-8') as f:
            lexicon = json.load(f)
        print(f"  → {len(lexicon)} palabras cargadas")
        return lexicon
    
    def _score_component(self, text: str, patterns: List[str]) -> float:
        """
        Calcula intensidad de componente (S/A/M) en texto.
        Retorna valor 0-1.
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for pattern in patterns if re.search(pattern, text_lower))
        word_count = len(text_lower.split())
        
        # Score = (matches / total_patterns) * (word_count_factor)
        pattern_score = matches / len(patterns) if patterns else 0
        word_factor = min(1.0, word_count / 10)  # Normaliza por palabras
        
        return float(min(1.0, (pattern_score + word_factor) / 2))
    
    def analyze_definition_as_sam(self, word: str, description: str) -> Tuple[float, float, float]:
        """
        Analiza descripción como triada SAM.
        
        Retorna: (S_score, A_score, M_score) normalizados a suma=1
        """
        if not description:
            return (0.33, 0.33, 0.34)  # Neutral si no hay descripción
        
        s_score = self._score_component(description, self.S_PATTERNS)
        a_score = self._score_component(description, self.A_PATTERNS)
        m_score = self._score_component(description, self.M_PATTERNS)
        
        # Normaliza a suma = 1
        total = s_score + a_score + m_score
        if total > 0:
            s_score /= total
            a_score /= total
            m_score /= total
        else:
            s_score = a_score = m_score = 0.33
        
        return (round(s_score, 3), round(a_score, 3), round(m_score, 3))
    
    def extract_word_mentions(self, text: str) -> List[str]:
        """
        Extrae palabras mencionadas en una definición.
        (Palabras que podrían estar en el lexicon)
        """
        # Palabras comunes a ignorar (stopwords españoles)
        stopwords = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'es', 'se', 'los', 'las',
            'un', 'una', 'unos', 'unas', 'por', 'para', 'con', 'su', 'del',
            'al', 'este', 'esta', 'como', 'o', 'sido', 'siendo', 'está', 'están'
        }
        
        # Extrae palabras (alfanuméricas), elimina stopwords
        words = re.findall(r'\b\w+\b', text.lower())
        mentioned = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Filtra solo las que existen en el lexicon
        return [w for w in set(mentioned) if w in self.lexicon]
    
    def build_chains_from_lexicon(self) -> Dict[str, Dict[str, Any]]:
        """
        Construye cadenas semánticas leyendo el lexicon.
        
        Para cada palabra:
        - Calcula su triada SAM desde su descripción
        - Extrae palabras mencionadas en esa descripción
        - Crea conexiones (cadenas)
        """
        chains = {}
        
        print("\nAnalizando definiciones...")
        for word, entry in self.lexicon.items():  # Procesa TODAS las palabras
            desc = entry.get('description', '')
            
            # Calcula SAM desde descripción
            s, a, m = self.analyze_definition_as_sam(word, desc)
            
            # Extrae palabras mencionadas
            mentions = self.extract_word_mentions(desc)
            
            chains[word] = {
                'word': word,
                'description': desc,
                'sam_from_description': [s, a, m],
                'sam_from_lexicon': entry.get('sam', [0.33, 0.33, 0.34]),
                'mentions': mentions,
                'category': entry.get('category', '?'),
                'aliases': entry.get('aliases', [])
            }
            
            self.word_connections[word] = mentions
        
        # ACTUALIZA SELF.CHAINS
        self.chains = chains
        
        print(f"  → {len(chains)} palabras analizadas")
        print(f"  → {sum(len(v['mentions']) for v in chains.values())} conexiones encontradas")
        
        return chains
    
    def find_semantic_cycles(self) -> List[List[str]]:
        """
        Busca ciclos en las cadenas semánticas.
        Ejemplo: A → B → C → A
        """
        cycles = []
        
        def dfs_find_cycle(start, current, path, visited):
            if len(path) > 1 and current == start:
                cycles.append(path[:-1])  # Elimina repetición del start
                return
            
            if current not in self.word_connections:
                return
            
            for next_word in self.word_connections.get(current, []):
                if next_word not in visited or (len(path) > 2 and next_word == start):
                    new_visited = visited.copy()
                    new_visited.add(next_word)
                    dfs_find_cycle(start, next_word, path + [next_word], new_visited)
        
        # Busca ciclos comenzando desde cada palabra (limita para velocidad)
        for word in list(self.word_connections.keys())[:100]:
            dfs_find_cycle(word, word, [word], {word})
        
        # Elimina ciclos duplicados
        unique_cycles = []
        for cycle in cycles:
            normalized = tuple(sorted(cycle))
            if normalized not in [tuple(sorted(c)) for c in unique_cycles]:
                unique_cycles.append(cycle)
        
        return unique_cycles[:20]  # Top 20 ciclos
    
    def save_chains(self, output_path: str = None) -> str:
        """Guarda cadenas extraídas a JSON."""
        if output_path is None:
            output_path = '07_DATOS_Y_CORPUS/DICCIONARIO_CADENAS_SAM_2026-05-19.json'
        
        cycles = self.find_semantic_cycles()
        
        output = {
            'metadata': {
                'extraction_date': '2026-05-19',
                'total_words': len(self.chains),
                'total_connections': sum(len(v['mentions']) for v in self.chains.values()),
                'cycles_found': len(cycles),
            },
            'chains': self.chains,
            'semantic_cycles': cycles,
            'word_connection_map': self.word_connections,
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Cadenas guardadas en: {output_path}")
        return output_path
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumen del análisis."""
        if not self.chains:
            return {'error': 'No chains extracted yet'}
        
        # Calcula estadísticas SAM
        all_sams = [v['sam_from_description'] for v in self.chains.values()]
        s_vals = [sam[0] for sam in all_sams]
        a_vals = [sam[1] for sam in all_sams]
        m_vals = [sam[2] for sam in all_sams]
        
        return {
            'total_chains': len(self.chains),
            'total_connections': sum(len(v['mentions']) for v in self.chains.values()),
            'sam_statistics': {
                'S': {'mean': float(np.mean(s_vals)), 'std': float(np.std(s_vals))},
                'A': {'mean': float(np.mean(a_vals)), 'std': float(np.std(a_vals))},
                'M': {'mean': float(np.mean(m_vals)), 'std': float(np.std(m_vals))},
            },
            'cycles_found': len(self.find_semantic_cycles()),
        }


def main():
    """Script principal para extracción."""
    extractor = SemanticChainExtractor()
    
    # Extrae cadenas
    chains = extractor.build_chains_from_lexicon()
    
    # Busca ciclos
    cycles = extractor.find_semantic_cycles()
    print(f"\nCiclos semánticos encontrados: {len(cycles)}")
    for i, cycle in enumerate(cycles[:5]):
        print(f"  Ciclo {i+1}: {' → '.join(cycle)} → {cycle[0]}")
    
    # Guarda resultado
    extractor.save_chains()
    
    # Muestra resumen
    summary = extractor.get_summary()
    print("\n=== RESUMEN ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
