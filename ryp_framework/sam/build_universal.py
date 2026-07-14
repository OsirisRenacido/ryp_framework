"""
RYP_MATRIZ_SAM_BUILD_UNIVERSAL.py
==================================

Construye Tabla Universal de Conjugaciones SAM.

Flujo:
  Cadenas SAM → Agregación de patrones → Clustering SAM → 
  → Identificación de 4 cierres → Tabla Universal

Autor: Joaquín Rosales Flores
Fecha: 2026-05-19
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set
import numpy as np
from collections import defaultdict


class UniversalSAMTableBuilder:
    """
    Construye Tabla Universal de Conjugaciones SAM.
    
    Identifica:
    - Clusters de palabras con SAM similar
    - Simetrías en el espacio semántico
    - Los 4 cierres (OSCURO, SOMBRA, LUMINOSO, VACÍO)
    - Palabras reemplazables (que ocupan posición SAM similar)
    """
    
    def __init__(self, chains_path: str = None):
        """
        Args:
            chains_path: ruta a DICCIONARIO_CADENAS_SAM_2026-05-19.json
        """
        self.chains_path = chains_path or self._find_chains_file()
        self.chains_data = self._load_chains()
        self.clusters = []
        self.closures = {}
        self.universal_table = {}
        
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
    
    def _load_chains(self) -> Dict[str, Any]:
        """Carga datos de cadenas extraídas."""
        print(f"Cargando cadenas desde: {self.chains_path}")
        with open(self.chains_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  → {data['metadata']['total_words']} palabras cargadas")
        return data
    
    def _euclidean_distance(self, sam1: List[float], sam2: List[float]) -> float:
        """Distancia euclidiana en espacio SAM."""
        return float(np.sqrt(sum((a - b) ** 2 for a, b in zip(sam1, sam2))))
    
    def _cosine_similarity(self, sam1: List[float], sam2: List[float]) -> float:
        """Similitud coseno (preserva dirección)."""
        dot = sum(a * b for a, b in zip(sam1, sam2))
        norm1 = np.sqrt(sum(a ** 2 for a in sam1))
        norm2 = np.sqrt(sum(b ** 2 for b in sam2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot / (norm1 * norm2))
    
    def identify_closures(self) -> Dict[str, Dict[str, Any]]:
        """
        Identifica los 4 cierres recursivos del lenguaje occidental.
        
        Se definen como atractores en el espacio SAM:
        - OSCURO: (S~0, A~0, M~1) — M puro, sin S ni A
        - SOMBRA: (S~0.3, A~0.5, M~0.9) — M dominante, A limitado, S ausente
        - LUMINOSO: (S~0.9, A~0.9, M~0.9) — equilibrio máximo
        - VACÍO: (S~0.8, A~0, M~0.2) — S puro sin mediación
        """
        
        closures = {
            'oscuro': {
                'name': 'CIERRE OSCURO (Actual)',
                'descriptor': 'M puro, sin S ni A. Lenguaje algebraico, lógica cerrada.',
                'sam_centroid': [0.0, 0.0, 1.0],
                'meaning': 'Estado actual del lenguaje occidental',
                'characteristic': 'Recursión M-sola (cierre en lógica)',
            },
            'sombra': {
                'name': 'CIERRE SOMBRA (Fragmentado)',
                'descriptor': 'M dominante pero A presente (limitado), S ausente.',
                'sam_centroid': [0.3, 0.5, 0.9],
                'meaning': 'Lenguaje fragmentado, con mediación incompleta',
                'characteristic': 'Recursión M-A (acción sin narrativa)',
            },
            'luminoso': {
                'name': 'CIERRE LUMINOSO (Potencial)',
                'descriptor': 'S-A-M equilibrado. Máxima articulación.',
                'sam_centroid': [0.9, 0.9, 0.9],
                'meaning': 'Máxima coherencia semántica',
                'characteristic': 'Recursión S-A-M (completa)',
            },
            'vacio': {
                'name': 'CIERRE VACÍO (Puro)',
                'descriptor': 'S puro sin mediación. Narrativa sin acción.',
                'sam_centroid': [0.8, 0.0, 0.2],
                'meaning': 'Narrativa sin mediación corporal ni acción',
                'characteristic': 'Recursión S-sola (sin materialización)',
            }
        }
        
        return closures
    
    def cluster_by_sam_proximity(self, radius: float = 0.15) -> List[Dict[str, Any]]:
        """
        Agrupa palabras por proximidad en espacio SAM.
        
        Palabras con SAM distancia < radius se agrupan en clusters.
        """
        chains = self.chains_data['chains']
        words_list = list(chains.items())
        
        print(f"\nClustering por proximidad SAM (radio={radius})...")
        
        clusters = []
        assigned = set()
        
        for word_name, word_data in words_list:
            if word_name in assigned:
                continue
            
            word_sam = word_data['sam_from_description']
            cluster_words = [word_name]
            assigned.add(word_name)
            
            # Encuentra palabras similares
            for other_name, other_data in words_list:
                if other_name in assigned or other_name == word_name:
                    continue
                
                other_sam = other_data['sam_from_description']
                distance = self._euclidean_distance(word_sam, other_sam)
                
                if distance < radius:
                    cluster_words.append(other_name)
                    assigned.add(other_name)
            
            # Calcula SAM promedio del cluster
            cluster_sams = [chains[w]['sam_from_description'] for w in cluster_words]
            avg_sam = [
                round(np.mean([s[i] for s in cluster_sams]), 3)
                for i in range(3)
            ]
            
            # Asigna closure más cercano
            closest_closure = self._assign_to_closure(avg_sam)
            
            clusters.append({
                'id': f'cluster_{len(clusters):03d}',
                'words': cluster_words,
                'size': len(cluster_words),
                'sam_centroid': avg_sam,
                'closure_type': closest_closure,
            })
        
        print(f"  → {len(clusters)} clusters identificados")
        return clusters
    
    def _assign_to_closure(self, sam: List[float]) -> str:
        """Asigna triada SAM al cierre más cercano."""
        closures = self.identify_closures()
        min_distance = float('inf')
        closest = 'oscuro'
        
        for closure_name, closure_info in closures.items():
            distance = self._euclidean_distance(sam, closure_info['sam_centroid'])
            if distance < min_distance:
                min_distance = distance
                closest = closure_name
        
        return closest
    
    def find_replaceable_words(self, target_sam: List[float], 
                               tolerance: float = 0.1) -> List[str]:
        """
        Encuentra palabras que podrían reemplazarse mutuamente.
        
        (Tienen SAM similar dentro de tolerance)
        """
        chains = self.chains_data['chains']
        replaceable = []
        
        for word, data in chains.items():
            word_sam = data['sam_from_description']
            distance = self._euclidean_distance(target_sam, word_sam)
            
            if distance < tolerance:
                replaceable.append({
                    'word': word,
                    'sam': word_sam,
                    'distance': round(distance, 3)
                })
        
        return sorted(replaceable, key=lambda x: x['distance'])
    
    def build_universal_table(self) -> Dict[str, Any]:
        """
        Construye la Tabla Universal de Conjugaciones.
        
        Estructura:
        {
            'metadata': {...},
            'closures': {cierre → definición},
            'clusters': [cluster con palabras],
            'replaceable_groups': [grupo de palabras intercambiables],
            'symmetries': [simetrías descubiertas]
        }
        """
        print("\n=== CONSTRUYENDO TABLA UNIVERSAL ===")
        
        # Identifica los 4 cierres
        self.closures = self.identify_closures()
        
        # Agrupa palabras por proximidad SAM
        self.clusters = self.cluster_by_sam_proximity(radius=0.15)
        
        # Encuentra grupos reemplazables
        print("\nEncontrando palabras reemplazables...")
        replaceable_groups = []
        for cluster in self.clusters:
            if cluster['size'] > 1:
                replaceable_groups.append({
                    'cluster_id': cluster['id'],
                    'sam_centroid': cluster['sam_centroid'],
                    'words': cluster['words'],
                    'closure_type': cluster['closure_type'],
                })
        
        # Identifica simetrías (palabras que forman ciclos)
        chains = self.chains_data['chains']
        semantic_cycles = self.chains_data.get('semantic_cycles', [])
        
        symmetries = []
        for cycle in semantic_cycles:
            cycle_sams = [chains[w]['sam_from_description'] for w in cycle if w in chains]
            if cycle_sams:
                avg_sam = [round(np.mean([s[i] for s in cycle_sams]), 3) for i in range(3)]
                symmetries.append({
                    'cycle': cycle,
                    'sam_average': avg_sam,
                    'closure_type': self._assign_to_closure(avg_sam),
                })
        
        # Construye tabla universal
        self.universal_table = {
            'metadata': {
                'construction_date': '2026-05-19',
                'source': 'Chains extraction + clustering',
                'total_clusters': len(self.clusters),
                'total_replaceable_groups': len(replaceable_groups),
                'total_symmetries': len(symmetries),
            },
            'closures': self.closures,
            'clusters': self.clusters,
            'replaceable_groups': replaceable_groups,
            'symmetries': symmetries,
        }
        
        return self.universal_table
    
    def save_universal_table(self, output_path: str = None) -> str:
        """Guarda Tabla Universal a JSON."""
        if output_path is None:
            output_path = '07_DATOS_Y_CORPUS/TABLA_UNIVERSAL_SAM_2026-05-19.json'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.universal_table, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Tabla Universal guardada en: {output_path}")
        return output_path
    
    def get_closure_words(self, closure_type: str) -> List[str]:
        """Retorna palabras asociadas a un cierre específico."""
        words = []
        for cluster in self.clusters:
            if cluster['closure_type'] == closure_type:
                words.extend(cluster['words'])
        return words


def main():
    """Script principal."""
    builder = UniversalSAMTableBuilder()
    
    # Construye tabla universal
    table = builder.build_universal_table()
    
    # Muestra cierres identificados
    print("\n=== CIERRES RECURSIVOS IDENTIFICADOS ===")
    for closure_name, closure_info in table['closures'].items():
        words = builder.get_closure_words(closure_name)
        print(f"\n{closure_info['name']}")
        print(f"  SAM centroide: {closure_info['sam_centroid']}")
        print(f"  Palabras: {words[:5]}... ({len(words)} total)")
    
    # Muestra clusters grandes
    print("\n=== TOP 10 CLUSTERS ===")
    top_clusters = sorted(table['clusters'], key=lambda x: x['size'], reverse=True)[:10]
    for cluster in top_clusters:
        print(f"{cluster['id']}: {cluster['size']} palabras, cierre={cluster['closure_type']}")
        print(f"  SAM: {cluster['sam_centroid']}")
        print(f"  Ej: {cluster['words'][:3]}")
    
    # Guarda tabla
    builder.save_universal_table()
    
    print("\n✓ Construcción completada")


if __name__ == '__main__':
    main()
