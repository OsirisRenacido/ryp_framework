# Modelo creado por Joaquin Rosales Flores, psicologo.
# =====================================================
# RYP WRITER CRITIC - CAPA DE AUTO-OBSERVACIÓN
# Evaluador de calidad y bucle de ajuste Omega para generación
# =====================================================

import numpy as np
import ryp_framework.language as lang

class RYPWriterCritic:
    """
    El crítico analiza la calidad semántica del texto generado,
    calcula la entropía y la deriva, y emite un dictamen (PASS/FAIL).
    Si hay falla, calcula un vector de corrección Omega para el motor.
    """
    def __init__(self, max_drift_allowed=0.15):
        self.max_drift_allowed = max_drift_allowed

    def evaluate_generation(self, text, target_sam):
        """
        Evalúa el texto generado contra el vector objetivo.
        Retorna un reporte de diagnóstico.
        """
        target = np.array(target_sam, dtype=float)
        
        # 1. Calcular el vector SAM real del texto generado
        estimated_sam = lang.text_to_sam(text)
        
        # 2. Calcular la deriva (distancia euclidiana)
        drift = float(np.linalg.norm(estimated_sam - target))
        
        # 3. Calcular entropía de la salida
        entropy_val = float(lang.entropy(estimated_sam))
        
        # 4. Chequear repeticiones (excluyendo stopwords)
        tokens = lang.tokenize(text)
        unique_tokens = set(tokens)
        repetition_rate = 0.0
        if len(tokens) > 0:
            repetition_rate = 1.0 - (len(unique_tokens) / len(tokens))
            
        # 5. Generar recomendación de autoajuste Omega
        omega_adjustment = self._calculate_omega_adjustment(estimated_sam, target)
        
        # Criterio de aceptación
        has_repetition_issue = repetition_rate > 0.25
        is_drift_ok = drift <= self.max_drift_allowed
        
        if is_drift_ok and not has_repetition_issue:
            decision = "PASS"
            recommendation = "Enunciado coherente y estable con la trayectoria."
        else:
            decision = "FAIL"
            if has_repetition_issue:
                recommendation = "Se detectaron repeticiones excesivas. Ajustar penalizaciones."
            else:
                recommendation = f"Deriva SAM excesiva ({drift:.3f}). Aplicar ajuste Omega."

        return {
            "estimated_sam": estimated_sam.tolist(),
            "target_sam": target.tolist(),
            "drift": drift,
            "entropy": entropy_val,
            "repetition_rate": repetition_rate,
            "decision": decision,
            "recommendation": recommendation,
            "omega_adjustment": omega_adjustment.tolist()
        }

    def _calculate_omega_adjustment(self, estimated_sam, target_sam):
        """
        Calcula el desvío por componente para reajustar el vector
        objetivo en la siguiente pasada (Bucle de auto-observación Omega).
        """
        # Desvío por eje: target - estimated
        deviation = target_sam - estimated_sam
        
        # Si el desvío es muy pequeño, no requiere ajuste
        if np.linalg.norm(deviation) < 0.05:
            return np.zeros(3)
            
        # Retorna el vector de ajuste. 
        # Si estimated_sam tiene exceso de M (M_estimated > M_target), 
        # deviation[2] será negativo, reduciendo el peso de M en la siguiente vuelta.
        return deviation


if __name__ == "__main__":
    critic = RYPWriterCritic()
    
    # Test rápido de evaluación
    target_vec = [0.30, 0.40, 0.30]
    sample_text = "El sentido organiza el vínculo y la mente sostiene el cambio."
    
    report = critic.evaluate_generation(sample_text, target_vec)
    print("=== TEST REPORTE CRÍTICO ===")
    print(f"Texto: '{sample_text}'")
    print(f"Objetivo: {target_vec}")
    print(f"Estimado: {np.round(report['estimated_sam'], 3)}")
    print(f"Deriva: {report['drift']:.4f}")
    print(f"Decisión: {report['decision']}")
    print(f"Ajuste Omega: {np.round(report['omega_adjustment'], 3)}")
