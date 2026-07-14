"""
RYP_MATRIZ_SAM_SEMANTIC_CYCLES.py
===================================

Fase 6: Búsqueda automática de ciclos semánticos emergentes.

Identifica:
- Ciclos simples (triadas A→B→C→A)
- Ciclos complejos (cuadrados, pentágonos, etc)
- Propiedades SAM de cada ciclo
- Tabla ontológica emergente de cada ciclo

Autor: Joaquín Rosales Flores
Fecha: 2026-05-19
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
import numpy as np


class SemanticCycleAnalyzer:
    """
    Analiza ciclos semánticos descubiertos en cadenas.
    
    Un ciclo es un patrón donde palabras se conectan recursivamente:
    A → B → C → A (triada)
    A → B → C → D → A (cuadrado)
    Etc.
    """
    
    def __init__(self, chains_path: str = None):
        """
        Args:
            chains_path: ruta a DICCIONARIO_CADENAS_SAM_2026-05-19.json
        """
        self.chains_path = chains_path or self._find_chains_file()
        self.chains_data = self._load_chains()
        self.word_graph = self._build_word_graph()
        self.cycles = []
        self.cycle_tables = []
        
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
        """Carga datos de cadenas."""
        print(f"Cargando cadenas desde: {self.chains_path}")
        with open(self.chains_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  → {data['metadata']['total_words']} palabras cargadas")
        return data
    
    def _build_word_graph(self) -> Dict[str, List[str]]:
        """
        Construye grafo de conexiones palabra → palabras mencionadas.
        """
        graph = defaultdict(list)
        chains = self.chains_data['chains']
        
        for word, data in chains.items():
            mentions = data.get('mentions', [])
            graph[word] = mentions
        
        print(f"  → Grafo de {len(graph)} nodos construido")
        return graph
    
    def find_cycles_dfs(self, max_length: int = 6, max_cycles: int = 100) -> List[List[str]]:
        """
        Busca ciclos usando DFS.
        
        Args:
            max_length: longitud máxima del ciclo (para evitar infinitos)
            max_cycles: máximo número de ciclos a retornar
        """
        print(f"\nBuscando ciclos semánticos (máx {max_cycles})...")
        
        cycles = set()
        
        def dfs_cycle(start, current, path, visited):
            """DFS para encontrar ciclos."""
            if len(cycles) >= max_cycles:
                return
            
            if len(path) > max_length:
                return
            
            # Si volvemos al inicio y hemos avanzado al menos 2 pasos
            if current == start and len(path) > 2:
                # Normaliza el ciclo (inicio siempre es la palabra más pequeña alfabéticamente)
                normalized = tuple(sorted(path[:-1]))
                if normalized not in cycles:
                    cycles.add(normalized)
                return
            
            # Si no hemos visitado o es el inicio en pasos posteriores
            if current not in visited or current == start:
                neighbors = self.word_graph.get(current, [])
                
                for next_word in neighbors:
                    if next_word not in visited or next_word == start:
                        new_visited = visited.copy()
                        if next_word != start:
                            new_visited.add(next_word)
                        
                        dfs_cycle(start, next_word, path + [next_word], new_visited)
        
        # Busca desde cada palabra (limita para velocidad)
        words_to_check = list(self.word_graph.keys())[:500]
        for i, word in enumerate(words_to_check):
            if i % 50 == 0:
                print(f"  Procesadas {i}/{len(words_to_check)} palabras...")
            
            if len(cycles) >= max_cycles:
                break
            
            dfs_cycle(word, word, [word], {word})
        
        # Convierte a listas
        self.cycles = [list(c) for c in cycles]
        
        print(f"  → {len(self.cycles)} ciclos encontrados")
        return self.cycles
    
    def analyze_cycle(self, cycle: List[str]) -> Dict[str, Any]:
        """
        Analiza propiedades SAM de un ciclo.
        """
        chains = self.chains_data['chains']
        
        # Obtiene SAM de cada palabra en ciclo
        sams = []
        missing = []
        for word in cycle:
            if word in chains:
                sams.append(chains[word]['sam_from_description'])
            else:
                missing.append(word)
        
        if not sams:
            return {'error': f'Ciclo {cycle} no tiene palabras en lexicón'}
        
        # Calcula SAM promedio
        sams_array = np.array(sams)
        avg_sam = [
            float(np.mean(sams_array[:, i])) for i in range(3)
        ]
        
        # Normaliza
        total = sum(avg_sam)
        if total > 0:
            avg_sam = [s / total for s in avg_sam]
        
        # Identifica tipo de ciclo
        cycle_type = f"{len(cycle)}-uple"
        if len(cycle) == 3:
            cycle_type = "triada"
        elif len(cycle) == 4:
            cycle_type = "cuadrado"
        elif len(cycle) == 5:
            cycle_type = "pentágono"
        
        return {
            'cycle': cycle,
            'type': cycle_type,
            'length': len(cycle),
            'sam_average': avg_sam,
            'sam_components': {
                'S': avg_sam[0],
                'A': avg_sam[1],
                'M': avg_sam[2],
            },
            'words_found': len(sams),
            'words_missing': missing,
        }
    
    def identify_cycle_closures(self, cycle_info: Dict[str, Any]) -> str:
        """
        Identifica qué cierre describe mejor el ciclo.
        
        Closures:
        - OSCURO: (0, 0, 1)
        - SOMBRA: (0.3, 0.5, 0.9)
        - LUMINOSO: (0.9, 0.9, 0.9)
        - VACÍO: (0.8, 0, 0.2)
        """
        closures = {
            'oscuro': ([0.0, 0.0, 1.0], "M puro"),
            'sombra': ([0.3, 0.5, 0.9], "M dominante"),
            'luminoso': ([0.9, 0.9, 0.9], "Equilibrio"),
            'vacio': ([0.8, 0.0, 0.2], "S puro"),
        }
        
        sam = cycle_info['sam_average']
        min_distance = float('inf')
        closest = 'sombra'
        
        for closure_name, (closure_sam, desc) in closures.items():
            distance = sum((sam[i] - closure_sam[i]) ** 2 for i in range(3))
            if distance < min_distance:
                min_distance = distance
                closest = closure_name
        
        return closest
    
    def build_cycle_ontology_table(self, cycle: List[str]) -> Dict[str, List[str]]:
        """
        Construye tabla ontológica de ciclo (palabras por fila/columna SAM).
        
        Output:
        {
            'rojo (S)': [palabras que son S-dominantes],
            'naranja (A)': [palabras que son A-dominantes],
            'amarillo (M)': [palabras que son M-dominantes],
            'gris': [palabras equilibradas]
        }
        """
        chains = self.chains_data['chains']
        table = {
            'rojo_s': [],
            'naranja_a': [],
            'amarillo_m': [],
            'gris': []
        }
        
        for word in cycle:
            if word in chains:
                sam = chains[word]['sam_from_description']
                s, a, m = sam
                
                if s > 0.4 and s >= a and s >= m:
                    table['rojo_s'].append(word)
                elif a > 0.4 and a >= s and a >= m:
                    table['naranja_a'].append(word)
                elif m > 0.4 and m >= s and m >= a:
                    table['amarillo_m'].append(word)
                else:
                    table['gris'].append(word)
        
        return table
    
    def analyze_all_cycles(self) -> List[Dict[str, Any]]:
        """
        Analiza todos los ciclos descubiertos.
        """
        print(f"\nAnalizando {len(self.cycles)} ciclos...")
        
        cycle_analyses = []
        for i, cycle in enumerate(self.cycles):
            if i % 20 == 0:
                print(f"  Analizados {i}/{len(self.cycles)}...")
            
            analysis = self.analyze_cycle(cycle)
            
            if 'error' not in analysis:
                analysis['closure'] = self.identify_cycle_closures(analysis)
                analysis['ontology_table'] = self.build_cycle_ontology_table(cycle)
                
                cycle_analyses.append(analysis)
        
        self.cycle_tables = cycle_analyses
        return cycle_analyses
    
    def save_cycle_analysis(self, output_path: str = None) -> str:
        """Guarda análisis de ciclos a JSON."""
        if output_path is None:
            output_path = '07_DATOS_Y_CORPUS/CICLOS_SEMANTICOS_ANALISIS_2026-05-19.json'
        
        output = {
            'metadata': {
                'analysis_date': '2026-05-19',
                'total_cycles': len(self.cycle_tables),
                'total_keywords': sum(len(c['cycle']) for c in self.cycle_tables),
            },
            'cycles': self.cycle_tables,
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Análisis de ciclos guardado en: {output_path}")
        return output_path
    
    def print_top_cycles(self, n: int = 10):
        """Imprime los N ciclos más interesantes."""
        print(f"\n=== TOP {n} CICLOS SEMÁNTICOS ===\n")
        
        # Ordena por longitud y luego por proximidad a cierre
        sorted_cycles = sorted(
            self.cycle_tables,
            key=lambda x: (x['type'], x['length']),
            reverse=True
        )[:n]
        
        for i, cycle_info in enumerate(sorted_cycles, 1):
            print(f"{i}. {cycle_info['type'].upper()}: {' → '.join(cycle_info['cycle'])} → {cycle_info['cycle'][0]}")
            print(f"   SAM: S={cycle_info['sam_components']['S']:.3f} | " +
                  f"A={cycle_info['sam_components']['A']:.3f} | " +
                  f"M={cycle_info['sam_components']['M']:.3f}")
            print(f"   Cierre: {cycle_info['closure'].upper()}")
            print(f"   Tabla SAM:")
            table = cycle_info['ontology_table']
            for color, words in table.items():
                if words:
                    print(f"     {color}: {', '.join(words[:3])}")
            print()


def main():
    """Script principal."""
    analyzer = SemanticCycleAnalyzer()
    
    # Busca ciclos
    cycles = analyzer.find_cycles_dfs(max_length=5, max_cycles=100)
    
    # Analiza ciclos
    analyses = analyzer.analyze_all_cycles()
    
    # Imprime top ciclos
    analyzer.print_top_cycles(10)
    
    # Guarda análisis
    analyzer.save_cycle_analysis()
    
    print("\n✓ Análisis de ciclos completado")


if __name__ == '__main__':
    main()
