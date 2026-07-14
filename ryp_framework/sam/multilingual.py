"""
RYP_MATRIZ_SAM_MULTILINGUAL.py
===============================

Fase 8: Análisis multilingüe comparativo.

Compara estructura SAM entre idiomas:
- Español (RYP_LEXICON)
- Inglés (si disponible)
- Francés (si disponible)

Pregunta central:
¿Todos los idiomas occidentales presentan cierre oscuro?
¿O algunos recuperan S de forma diferente?

Autor: Joaquín Rosales Flores
Fecha: 2026-05-19
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import numpy as np


class MultilingualSAMComparison:
    """
    Compara estructura SAM entre idiomas.
    """
    
    def __init__(self):
        """Inicializa comparador."""
        self.languages = {}
        self.comparisons = {}
        self._load_available_lexicons()
        
    def _load_available_lexicons(self):
        """
        Busca lexicones disponibles en el workspace.
        Formatos esperados:
        - RYP_LEXICON.json (español)
        - RYP_LEXICON_ENGLISH.json (inglés)
        - RYP_LEXICON_FRENCH.json (francés)
        """
        
        print("Buscando lexicones multilingües...\n")
        
        # Español (base)
        if Path('07_DATOS_Y_CORPUS/RYP_LEXICON.json').exists():
            self.languages['español'] = {
                'path': '07_DATOS_Y_CORPUS/RYP_LEXICON.json',
                'code': 'es',
                'name': 'Español (RYP)',
                'data': None
            }
            print("  ✓ Español (RYP_LEXICON.json)")
        
        # Inglés
        candidates_en = list(Path('07_DATOS_Y_CORPUS').glob('*ENGLISH*.json'))
        if candidates_en:
            self.languages['inglés'] = {
                'path': str(candidates_en[0]),
                'code': 'en',
                'name': 'Inglés',
                'data': None
            }
            print(f"  ✓ Inglés ({candidates_en[0].name})")
        else:
            print("  ✗ Inglés (no disponible)")
        
        # Francés
        candidates_fr = list(Path('07_DATOS_Y_CORPUS').glob('*FRENCH*.json'))
        if candidates_fr:
            self.languages['francés'] = {
                'path': str(candidates_fr[0]),
                'code': 'fr',
                'name': 'Francés',
                'data': None
            }
            print(f"  ✓ Francés ({candidates_fr[0].name})")
        else:
            print("  ✗ Francés (no disponible)")
        
        # Carga datos
        for lang, info in self.languages.items():
            self._load_lexicon_data(lang, info)
    
    def _load_lexicon_data(self, lang_name: str, info: Dict[str, Any]):
        """Carga lexicón para idioma."""
        try:
            with open(info['path'], 'r', encoding='utf-8') as f:
                data = json.load(f)
            info['data'] = data
            print(f"    Cargadas palabras para {lang_name}")
        except Exception as e:
            print(f"    Error cargando {lang_name}: {str(e)}")
    
    def analyze_language_sam_distribution(self, lang_name: str) -> Dict[str, Any]:
        """
        Analiza distribución SAM de un idioma.
        """
        if lang_name not in self.languages:
            return {'error': f'Idioma {lang_name} no disponible'}
        
        lang_info = self.languages[lang_name]
        if not lang_info['data']:
            return {'error': f'Datos no cargados para {lang_name}'}
        
        lexicon = lang_info['data']
        
        # Extrae SAM scores
        sams = []
        for word, entry in lexicon.items():
            if 'sam' in entry:
                sams.append(entry['sam'])
        
        if not sams:
            return {'error': f'No SAM data found for {lang_name}'}
        
        sams_array = np.array(sams)
        
        # Estadísticas
        stats = {
            'language': lang_name,
            'code': lang_info['code'],
            'total_words': len(lexicon),
            'words_with_sam': len(sams),
            'sam_statistics': {
                'S': {
                    'mean': float(np.mean(sams_array[:, 0])),
                    'std': float(np.std(sams_array[:, 0])),
                    'min': float(np.min(sams_array[:, 0])),
                    'max': float(np.max(sams_array[:, 0])),
                },
                'A': {
                    'mean': float(np.mean(sams_array[:, 1])),
                    'std': float(np.std(sams_array[:, 1])),
                    'min': float(np.min(sams_array[:, 1])),
                    'max': float(np.max(sams_array[:, 1])),
                },
                'M': {
                    'mean': float(np.mean(sams_array[:, 2])),
                    'std': float(np.std(sams_array[:, 2])),
                    'min': float(np.min(sams_array[:, 2])),
                    'max': float(np.max(sams_array[:, 2])),
                }
            }
        }
        
        # Identifica patrón dominante
        means = [
            stats['sam_statistics']['S']['mean'],
            stats['sam_statistics']['A']['mean'],
            stats['sam_statistics']['M']['mean']
        ]
        dominant_idx = np.argmax(means)
        dominant_names = ['S (Narrativa)', 'A (Mediación)', 'M (Acción)']
        
        stats['dominant_component'] = dominant_names[dominant_idx]
        stats['dominance_score'] = float(means[dominant_idx])
        
        return stats
    
    def compare_languages(self) -> Dict[str, Any]:
        """
        Compara estructura SAM entre idiomas.
        """
        print("\n=== ANÁLISIS SAM POR IDIOMA ===\n")
        
        comparisons = {}
        
        for lang_name in self.languages.keys():
            analysis = self.analyze_language_sam_distribution(lang_name)
            
            if 'error' not in analysis:
                comparisons[lang_name] = analysis
                
                print(f"{lang_name.upper()}")
                print(f"  Palabras: {analysis['total_words']}")
                print(f"  Componente dominante: {analysis['dominant_component']}")
                print(f"  S mean={analysis['sam_statistics']['S']['mean']:.3f}, " +
                      f"A mean={analysis['sam_statistics']['A']['mean']:.3f}, " +
                      f"M mean={analysis['sam_statistics']['M']['mean']:.3f}")
                print()
        
        return comparisons
    
    def calculate_language_distance(self, lang1: str, lang2: str) -> float:
        """
        Calcula distancia SAM entre dos idiomas.
        (Distancia entre centroides SAM)
        """
        if lang1 not in self.languages or lang2 not in self.languages:
            return -1
        
        analysis1 = self.compare_languages().get(lang1)
        analysis2 = self.compare_languages().get(lang2)
        
        if not analysis1 or not analysis2 or 'error' in analysis1 or 'error' in analysis2:
            return -1
        
        sam1 = [
            analysis1['sam_statistics']['S']['mean'],
            analysis1['sam_statistics']['A']['mean'],
            analysis1['sam_statistics']['M']['mean'],
        ]
        
        sam2 = [
            analysis2['sam_statistics']['S']['mean'],
            analysis2['sam_statistics']['A']['mean'],
            analysis2['sam_statistics']['M']['mean'],
        ]
        
        # Distancia euclidiana
        distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(sam1, sam2)))
        
        return float(distance)
    
    def generate_multilingual_report(self) -> Dict[str, Any]:
        """Genera reporte multilingüe."""
        
        comparisons = self.compare_languages()
        
        # Calcula distancias
        distances = {}
        lang_list = list(comparisons.keys())
        for i, lang1 in enumerate(lang_list):
            for lang2 in lang_list[i+1:]:
                key = f"{lang1} ↔ {lang2}"
                distance = self.calculate_language_distance(lang1, lang2)
                distances[key] = distance
        
        report = {
            'metadata': {
                'date': '2026-05-19',
                'languages_compared': len(comparisons),
                'analysis_type': 'SAM structure comparison',
            },
            'language_analyses': comparisons,
            'inter_language_distances': distances,
            'interpretation': {
                'findings': self._generate_findings(comparisons, distances),
                'implications': self._generate_implications(comparisons),
            }
        }
        
        return report
    
    def _generate_findings(self, comparisons: Dict[str, Any],
                          distances: Dict[str, float]) -> List[str]:
        """Genera hallazgos del análisis."""
        findings = []
        
        if len(comparisons) > 1:
            # Compara patrones de dominancia
            components = [c['dominant_component'] for c in comparisons.values()]
            
            if all(comp == 'S (Narrativa)' for comp in components):
                findings.append("✓ Todos los idiomas analizados tienen S (narrativa) como componente dominante")
                findings.append("  → Sugiere que recuperación de S es patrón universal")
            
            elif all(comp == 'M (Acción)' for comp in components):
                findings.append("✓ Todos los idiomas analizados tienen M (acción) como componente dominante")
                findings.append("  → Sugiere que cierre oscuro es universal en lenguajes occidentales")
            
            else:
                findings.append(f"✓ Idiomas analizados muestran diferentes patrones de dominancia: {set(components)}")
                findings.append("  → Sugiere que recuperación de S varía según idioma/cultura")
        
        else:
            findings.append(f"Análisis limitado a 1 idioma disponible ({list(comparisons.keys())[0]})")
        
        return findings
    
    def _generate_implications(self, comparisons: Dict[str, Any]) -> List[str]:
        """Genera implicaciones del análisis."""
        implications = []
        
        if 'español' in comparisons:
            es_analysis = comparisons['español']
            dominance = es_analysis['dominance_score']
            
            if dominance > 0.37:
                implications.append("S está significativamente representado en español RYP")
                implications.append("  → Lenguaje del RYP framework ha logrado recuperación parcial de S")
            else:
                implications.append("S está débilmente representado")
        
        implications.append("Para conclusiones multilingües robustas, necesitamos lexicones en inglés y francés")
        implications.append("Próximo paso: Expandir corpus a otros idiomas occidentales (inglés, francés, alemán)")
        
        return implications
    
    def save_multilingual_report(self, report: Dict[str, Any],
                                output_path: str = None) -> str:
        """Guarda reporte multilingüe."""
        if output_path is None:
            output_path = '07_DATOS_Y_CORPUS/ANALISIS_MULTILINGUE_SAM_2026-05-19.json'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Reporte multilingüe guardado en: {output_path}")
        return output_path
    
    def print_multilingual_report(self, report: Dict[str, Any]):
        """Imprime reporte multilingüe."""
        
        print("\n" + "="*70)
        print("  ANÁLISIS MULTILINGÜE - ESTRUCTURA SAM")
        print("="*70 + "\n")
        
        # Análisis por idioma
        print("ANÁLISIS POR IDIOMA")
        print("-" * 70)
        for lang, analysis in report['language_analyses'].items():
            print(f"\n{lang.upper()}")
            print(f"  Total palabras: {analysis['total_words']}")
            print(f"  Componente dominante: {analysis['dominant_component']}")
            print(f"  (Dominance score: {analysis['dominance_score']:.3f})")
        
        # Distancias
        if report['inter_language_distances']:
            print("\n\nDISTANCIAS ENTRE IDIOMAS (SAM espacio)")
            print("-" * 70)
            for pair, distance in report['inter_language_distances'].items():
                if distance > 0:
                    print(f"  {pair}: {distance:.4f}")
        
        # Hallazgos
        print("\n\nHALLAZGOS")
        print("-" * 70)
        for finding in report['interpretation']['findings']:
            print(f"  {finding}")
        
        # Implicaciones
        print("\n\nIMPLICACIONES")
        print("-" * 70)
        for implication in report['interpretation']['implications']:
            print(f"  {implication}")
        
        print("\n" + "="*70 + "\n")


def main():
    """Script principal."""
    
    comparison = MultilingualSAMComparison()
    report = comparison.generate_multilingual_report()
    comparison.print_multilingual_report(report)
    comparison.save_multilingual_report(report)
    
    print("✓ Análisis multilingüe completado")


if __name__ == '__main__':
    main()
