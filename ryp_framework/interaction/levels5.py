# Modelo creado por Joaquin Rosales Flores, psicologo.
# =====================================================
# NIVEL 5: DIMENSIÓN DE INTERACCIÓN (5D)
# =====================================================
# La función que modela cómo dos cristales interactúan
# en el espacio intermedio de compatibilidad
# =====================================================

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.distance import euclidean, cosine
from scipy.stats import pearsonr

from ryp_framework.core._crystal_expansion import PolyhedronCrystal, build_crystal_from_simulation
from ryp_framework.morphosemantic.prism import apply_prism_refraction, build_interaction_internal_sam, route_signature_tracker


class RelationalSpace:
    """
    El espacio de interacción (5D) entre dos cristales.
    
    Representa la función f(C₁, C₂) que modela:
    - Compatibilidad estructural (S)
    - Proximidad en trayectoria (A) 
    - Memoria de encuentros (M)
    
    Este espacio es la "arena" donde los cristales 
    se transforman mutuamente.
    """
    
    def __init__(self, crystal1, crystal2, name1="C1", name2="C2", cognitive_weight_overrides=None):
        self.crystal1 = crystal1
        self.crystal2 = crystal2
        self.name1 = name1
        self.name2 = name2
        self.cognitive_weight_overrides = cognitive_weight_overrides or {}
        
        # Métricas de interacción
        self.structural_similarity = None  # S
        self.trajectory_correlation = None  # A (amistad)
        self.interaction_memory = 0.0  # M
        self.compatibility_score = None
        
        # Espacios de transformación
        self.interaction_trajectory = None  # Trayectoria en espacio 5D
        self.transformation_vectors = None  # Cómo se transforma cada uno
        self.cognitive_profile = None
        self.cognitive_feedback = None
        
        # Calcular al instanciar
        self._compute_interaction_metrics()

    def get_cognitive_weights(self):
        """Retorna pesos cognitivos efectivos para modular la interacción."""
        defaults = {
            'mentalization': 1.0,
            'imagination': 1.0,
            'perception': 1.0,
        }
        weights = defaults.copy()
        for key, value in self.cognitive_weight_overrides.items():
            if key in weights:
                weights[key] = float(np.clip(value, 0, 2))
        return weights
    
    # =====================================================
    # PASO 1: CALCULAR SIMILITUD ESTRUCTURAL (S)
    # =====================================================
    
    def compute_structural_similarity(self):
        """
        Mide qué tan similar es la estructura de ambos cristales.
        
        Vector de características:
        - num_nodos
        - num_aristas
        - num_egos
        - densidad de red
        - Φ global (auto-consciencia)
        - fortaleza promedio de aristas
        
        Returns: S ∈ [0, 1] donde 1 = idénticos
        """
        
        m1 = self.crystal1.get_crystal_metrics()
        m2 = self.crystal2.get_crystal_metrics()
        
        # Calcular densidad si no está disponible
        if 'density' not in m1:
            density_1 = 2 * m1['num_edges'] / (m1['num_nodes'] * (m1['num_nodes'] - 1) + 1e-10) if m1['num_nodes'] > 1 else 0
        else:
            density_1 = m1['density']
        
        if 'density' not in m2:
            density_2 = 2 * m2['num_edges'] / (m2['num_nodes'] * (m2['num_nodes'] - 1) + 1e-10) if m2['num_nodes'] > 1 else 0
        else:
            density_2 = m2['density']
        
        # Vector de características normalizado
        features_C1 = np.array([
            m1['num_nodes'] / 100.0,  # Normalizar
            m1['num_edges'] / 500.0,
            m1['num_egos'] / 300.0,
            density_1,
            m1['global_phi'] if not np.isnan(m1['global_phi']) else 0.5,
            m1['avg_edge_strength']
        ])
        
        features_C2 = np.array([
            m2['num_nodes'] / 100.0,
            m2['num_edges'] / 500.0,
            m2['num_egos'] / 300.0,
            density_2,
            m2['global_phi'] if not np.isnan(m2['global_phi']) else 0.5,
            m2['avg_edge_strength']
        ])
        
        # Similitud de coseno (1 = idénticos, 0 = ortogonales)
        similarity = 1 - cosine(features_C1, features_C2)
        
        return np.clip(similarity, 0, 1)
    
    # =====================================================
    # PASO 2: CALCULAR CORRELACIÓN DE TRAYECTORIA (A)
    # =====================================================
    
    def compute_trajectory_correlation(self):
        """
        Mide qué tan sincrónicas fueron las trayectorias SAM
        que generaron ambos cristales.
        
        Si ambos cristales emergieron de dinámicas similares,
        sus trayectorias será altamente correlacionadas.
        
        Returns: A ∈ [-1, +1]
                 +1 = trayectorias perfectamente paralelas
                 0 = sin correlación (ortogonales)
                 -1 = trayectorias invertidas
        """
        
        # Extraer trayectorias base (primeros 3D de cada nodo)
        traj1 = np.array([n['state_3d'] for n in self.crystal1.nodes])
        traj2 = np.array([n['state_3d'] for n in self.crystal2.nodes])
        
        # Si tienen diferente longitud, interpolar a longitud común
        if len(traj1) != len(traj2):
            n_common = min(len(traj1), len(traj2))
            # Tomar los primeros n_common puntos
            traj1 = traj1[:n_common]
            traj2 = traj2[:n_common]
        
        if len(traj1) < 2:
            return 0.0  # Sin datos suficientes
        
        # Aplanar trayectorias para correlación
        flat_traj1 = traj1.flatten()
        flat_traj2 = traj2.flatten()
        
        if len(flat_traj1) < 2:
            return 0.0
        
        try:
            corr, _ = pearsonr(flat_traj1, flat_traj2)
            return np.clip(corr, -1, 1)
        except:
            return 0.0
    
    # =====================================================
    # PASO 3: CALCULAR COMPATIBILIDAD GENERAL
    # =====================================================
    
    def compute_compatibility_score(self):
        """
        Puntuación de compatibilidad general: 
        combinación ponderada de S y A
        
        Returns: compatibilidad ∈ [0, 1]
        """
        
        # Pesos: estructura 40%, trayectoria 60%
        w_structural = 0.4
        w_trajectory = 0.6
        
        # Normalizar correlación de trayectoria al rango [0, 1]
        trajectory_normalized = (self.trajectory_correlation + 1) / 2
        
        compatibility = (w_structural * self.structural_similarity + 
                        w_trajectory * trajectory_normalized)
        
        return np.clip(compatibility, 0, 1)
    
    # =====================================================
    # PASO 4: GENERAR TRAYECTORIA DE INTERACCIÓN (5D)
    # =====================================================
    
    def generate_interaction_trajectory(self, n_steps=50, apply_cognition=True):
        """
        Genera la trayectoria del encuentro en el espacio 5D.
        
        Cada punto representa un instante de la interacción,
        mostrando cómo cambian S, A, M mientras interactúan.
        
        Parámetros:
        -----------
        n_steps: Número de pasos temporales
        
        Returns:
        --------
        trayectoria: array (n_steps, 5)
                    Cada fila es [S(t), A(t), M(t), transformación_C1(t), transformación_C2(t)]
        """
        
        trajectory = []
        feedback = self.cognitive_feedback if (apply_cognition and self.cognitive_feedback) else {
            'similarity_bias': 0.0,
            'affective_bias': 0.0,
            'memory_gain': 0.0,
            'exploration_drive': 0.0,
            'alignment_gain': 0.0,
        }
        
        for t in np.linspace(0, 1, n_steps):
            # S y A se modulan si la interacción desarrolla propiedades cognitivas.
            s_value = self.structural_similarity + feedback['similarity_bias'] * t * (1 - self.structural_similarity) * 0.2
            a_value = self.trajectory_correlation + feedback['affective_bias'] * (2 * t - 1) * 0.12
            s_value = np.clip(s_value, 0, 1)
            a_value = np.clip(a_value, -1, 1)
            
            # M evoluciona: comienza en 0 y aumenta con la interacción
            # pero modulado por compatibilidad
            if self.compatibility_score > 0.5:
                # Alta compatibilidad: M aumenta rápidamente
                m_value = t * self.compatibility_score
            else:
                # Baja compatibilidad: M aumenta lentamente
                m_value = t * (0.3 + self.compatibility_score * 0.2)

            m_value = np.clip(m_value * (1 + feedback['memory_gain'] * t * 0.7), 0, 1)
            
            # Transformación de cada cristal bajo la influencia del otro
            # Si A > 0: ambos se transforman en la misma dirección
            # Si A < 0: se transforman en direcciones opuestas
            transform_scale = 1 + feedback['alignment_gain'] * 0.3 - feedback['exploration_drive'] * 0.15
            transform_c1 = ((1 - t) + t * (self.compatibility_score * np.sign(a_value + 0.1))) * transform_scale
            transform_c2 = ((1 - t) + t * (self.compatibility_score * np.sign(a_value + 0.1))) * transform_scale
            
            trajectory.append([s_value, a_value, m_value, transform_c1, transform_c2])
        
        return np.array(trajectory)


    def compute_cognitive_feedback(self):
        """Deriva moduladores cognitivos a partir de la propia interacción."""
        from RYP_PROPIEDADES_COGNITIVAS import MentalizationEngine, ImaginationEngine, PerceptionEngine

        mentalization = MentalizationEngine(self).theory_of_mind()
        imagination = ImaginationEngine(self).creativity_score()
        perception = PerceptionEngine(self).perception_accuracy()

        stability_mean = np.mean([
            mentalization['mental_state']['similitude_belief']['stability'],
            mentalization['mental_state']['affection_belief']['stability'],
            mentalization['mental_state']['momentum_belief']['stability'],
        ])
        affective_component = mentalization['emotional_valence']['positive_component'] - mentalization['emotional_valence']['negative_component']

        self.cognitive_profile = {
            'mentalization': float(np.clip(stability_mean, 0, 1)),
            'imagination': imagination['overall_creativity'],
            'perception': perception.get('accuracy_score', 0.5),
            'intention': mentalization['intention']['primary_intention'],
            'emotional_tone': mentalization['emotional_valence']['emotional_tone'],
        }

        weights = self.get_cognitive_weights()
        weighted_mentalization = float(np.clip(self.cognitive_profile['mentalization'] * weights['mentalization'], 0, 1))
        weighted_imagination = float(np.clip(self.cognitive_profile['imagination'] * weights['imagination'], 0, 1))
        weighted_perception = float(np.clip(self.cognitive_profile['perception'] * weights['perception'], 0, 1))

        self.cognitive_feedback = {
            'similarity_bias': float(np.clip(weighted_mentalization * 0.6 + weighted_perception * 0.4, 0, 1)),
            'affective_bias': float(np.clip(affective_component, -1, 1)),
            'memory_gain': float(np.clip(weighted_perception * 0.5 + weighted_mentalization * 0.5, 0, 1)),
            'exploration_drive': float(np.clip(weighted_imagination, 0, 1)),
            'alignment_gain': float(np.clip(weighted_mentalization * 0.7 + weighted_perception * 0.3, 0, 1)),
            'weights': weights,
        }

        return self.cognitive_feedback
    
    # =====================================================
    # PASO 5: COMPUTAR VECTORES DE TRANSFORMACIÓN
    # =====================================================
    
    def compute_transformation_vectors(self):
        """
        Calcula los vectores de transformación:
        cómo cada cristal es modificado por el otro.
        
        Si A > 0: Transformaciones sinérgicas (se refuerzan)
        Si A < 0: Transformaciones antagónicas (se anulan)
        Si A ≈ 0: Transformaciones ortogonales (no interactúan)
        """
        
        # Vector de transformación para C1
        # Dirección: hacia la estructura de C2, modulada por compatibilidad
        if len(self.crystal2.nodes) > 0 and len(self.crystal1.nodes) > 0:
            # Centro de masa de cada cristal
            center_C1 = np.mean([n['state_3d'] for n in self.crystal1.nodes], axis=0)
            center_C2 = np.mean([n['state_3d'] for n in self.crystal2.nodes], axis=0)
            
            # Vector de atracción/repulsión
            direction = center_C2 - center_C1
            magnitude = np.linalg.norm(direction)
            
            if magnitude > 0:
                direction = direction / magnitude
            
            # Modular por compatibilidad y amistad
            alignment_gain = 1 + (self.cognitive_feedback or {}).get('alignment_gain', 0.0) * 0.35
            exploration_penalty = 1 - (self.cognitive_feedback or {}).get('exploration_drive', 0.0) * 0.1
            scalar = self.compatibility_score * np.tanh(self.trajectory_correlation) * alignment_gain * exploration_penalty
            transform_C1 = direction * scalar
            transform_C2 = -direction * scalar
        else:
            transform_C1 = np.array([0, 0, 0])
            transform_C2 = np.array([0, 0, 0])
        
        self.transformation_vectors = {
            'C1': transform_C1,
            'C2': transform_C2,
            'magnitude': np.linalg.norm(transform_C1)
        }
        
        return self.transformation_vectors
    
    # =====================================================
    # UTILIDAD: COMPUTAR TODAS LAS MÉTRICAS
    # =====================================================
    
    def _compute_interaction_metrics(self):
        """Calcula todas las métricas de interacción."""
        
        self.structural_similarity = self.compute_structural_similarity()
        self.trajectory_correlation = self.compute_trajectory_correlation()
        self.compatibility_score = self.compute_compatibility_score()
        self.interaction_trajectory = self.generate_interaction_trajectory(apply_cognition=False)
        self.compute_cognitive_feedback()
        self.interaction_trajectory = self.generate_interaction_trajectory(apply_cognition=True)
        self.interaction_memory = float(self.interaction_trajectory[-1, 2])
        self.compute_transformation_vectors()
    
    # =====================================================
    # INTERPRETACIÓN Y REPORTE
    # =====================================================
    
    def print_interaction_report(self):
        """Reporte detallado de la interacción."""
        
        print("\n" + "="*70)
        print(f"  🔗 REPORTE DE INTERACCIÓN: {self.name1} ↔ {self.name2}")
        print("="*70)
        
        print(f"\n📐 SIMILITUD ESTRUCTURAL (S):")
        print(f"   Valor: {self.structural_similarity:.4f} [0=diferente, 1=idéntico]")
        if self.structural_similarity > 0.7:
            print(f"   → Cristales muy similares")
        elif self.structural_similarity > 0.4:
            print(f"   → Cristales moderadamente similares")
        else:
            print(f"   → Cristales estructuralmente diferentes")
        
        print(f"\n💫 AMISTAD / CORRELACIÓN DE TRAYECTORIA (A):")
        print(f"   Valor: {self.trajectory_correlation:.4f} [-1=opuestos, 0=ortogonal, +1=sincrónico]")
        if self.trajectory_correlation > 0.5:
            print(f"   → Trayectorias muy sincrónicas (desarrollaron en paralelo)")
        elif self.trajectory_correlation > 0:
            print(f"   → Trayectorias levemente correlacionadas")
        elif self.trajectory_correlation > -0.3:
            print(f"   → Trayectorias débilmente ortogonales")
        else:
            print(f"   → Trayectorias antagónicas (desarrollaron en direcciones opuestas)")
        
        print(f"\n⚡ COMPATIBILIDAD GENERAL:")
        print(f"   Puntuación: {self.compatibility_score:.4f} [0=incompatible, 1=perfectamente compatible]")
        if self.compatibility_score > 0.7:
            print(f"   → ALTA compatibilidad: se fusionarán/reforzarán mutuamente")
        elif self.compatibility_score > 0.4:
            print(f"   → MEDIA compatibilidad: pueden cooperar con tensiones")
        else:
            print(f"   → BAJA compatibilidad: riesgo de conflicto o rechazo")
        
        print(f"\n🔄 TRANSFORMACIONES MUTUAS:")
        tv = self.transformation_vectors
        print(f"   Magnitud de transformación: {tv['magnitude']:.4f}")
        print(f"   Vector C1: {tv['C1']}")
        print(f"   Vector C2: {tv['C2']}")

        if self.cognitive_profile:
            print(f"\n🧩 PROPIEDADES COGNITIVAS EMERGENTES:")
            print(f"   Mentalización: {self.cognitive_profile['mentalization']:.4f}")
            print(f"   Imaginación:   {self.cognitive_profile['imagination']:.4f}")
            print(f"   Percepción:    {self.cognitive_profile['perception']:.4f}")
            print(f"   Intención:     {self.cognitive_profile['intention']}")
            print(f"   Tono:          {self.cognitive_profile['emotional_tone']}")

        if self.cognitive_feedback:
            print(f"\n🔁 FEEDBACK COGNITIVO SOBRE LA INTERACCIÓN:")
            print(f"   Similarity bias:  {self.cognitive_feedback['similarity_bias']:.4f}")
            print(f"   Affective bias:   {self.cognitive_feedback['affective_bias']:.4f}")
            print(f"   Memory gain:      {self.cognitive_feedback['memory_gain']:.4f}")
            print(f"   Exploration drive:{self.cognitive_feedback['exploration_drive']:.4f}")
            print(f"   Alignment gain:   {self.cognitive_feedback['alignment_gain']:.4f}")
        
        print("\n" + "="*70 + "\n")
    
    def get_interaction_metrics(self):
        """Retorna diccionario con todas las métricas."""
        return {
            'S': self.structural_similarity,
            'A': self.trajectory_correlation,
            'M': self.interaction_memory,
            'compatibility': self.compatibility_score,
            'internal_sam_state': self.get_internal_sam_state().tolist(),
            'route_tracker': self.get_route_tracker(),
            'transformation_magnitude': self.transformation_vectors['magnitude'],
            'cognitive_profile': self.cognitive_profile,
            'cognitive_feedback': self.cognitive_feedback,
        }

    def get_internal_sam_state(self):
        """Construye un estado SAM interno desde las métricas de interacción ya calculadas."""
        return build_interaction_internal_sam(
            self.structural_similarity,
            self.trajectory_correlation,
            self.interaction_memory,
        )

    def get_route_tracker(self):
        """Resume qué rutas canónicas aparecen en la trayectoria SAM de la interacción."""
        if self.interaction_trajectory is None or len(self.interaction_trajectory) == 0:
            return route_signature_tracker([])
        return route_signature_tracker([row[:3] for row in self.interaction_trajectory])

    def simulate_prism_refraction(self, external_sam, boundary_strength=0.60, reentry_gain=0.20):
        """Aplica un evento prismático mínimo sobre el estado interno actual de la interacción."""
        result = apply_prism_refraction(
            external_sam,
            self.get_internal_sam_state(),
            boundary_strength=boundary_strength,
            reentry_gain=reentry_gain,
        )
        result['route_tracker'] = self.get_route_tracker()
        return result


# =====================================================
# FUNCIÓN PRINCIPAL: CREAR ESPACIO DE INTERACCIÓN
# =====================================================

def create_relational_space(crystal1, crystal2, name1="Crystal1", name2="Crystal2", cognitive_weight_overrides=None):
    """
    Crea el espacio 5D de interacción entre dos cristales.
    
    Usage:
    ------
    space = create_relational_space(c1, c2)
    space.print_interaction_report()
    metrics = space.get_interaction_metrics()
    """
    
    return RelationalSpace(crystal1, crystal2, name1, name2, cognitive_weight_overrides=cognitive_weight_overrides)


def visualize_interaction_space(relational_space, save_path=None):
    """
    Visualiza el espacio de interacción 5D proyectado a 3D.
    """
    
    trajectory = relational_space.interaction_trajectory
    
    fig = plt.figure(figsize=(15, 5))
    
    # Subplot 1: Trayectoria S-A-M en 3D
    ax1 = fig.add_subplot(131, projection='3d')
    ax1.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], 
             'r-', linewidth=2, label='Trayectoria de interacción')
    ax1.scatter(trajectory[0, 0], trajectory[0, 1], trajectory[0, 2], 
               c='green', s=100, label='Inicio', marker='o')
    ax1.scatter(trajectory[-1, 0], trajectory[-1, 1], trajectory[-1, 2], 
               c='red', s=100, label='Fin', marker='s')
    ax1.set_xlabel('S (Similitud Estructural)')
    ax1.set_ylabel('A (Amistad/Correlación)')
    ax1.set_zlabel('M (Memoria)')
    ax1.set_title('Espacio 5D de Interacción (proyección SAM)')
    ax1.legend()
    
    # Subplot 2: Evolución temporal de S, A, M
    ax2 = fig.add_subplot(132)
    t = np.linspace(0, 1, len(trajectory))
    ax2.plot(t, trajectory[:, 0], 'b-', label='S (Similitud)', linewidth=2)
    ax2.plot(t, trajectory[:, 1], 'g-', label='A (Amistad)', linewidth=2)
    ax2.plot(t, trajectory[:, 2], 'r-', label='M (Memoria)', linewidth=2)
    ax2.set_xlabel('Tiempo de interacción')
    ax2.set_ylabel('Valor')
    ax2.set_title('Evolución temporal de S, A, M')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: Transformaciones
    ax3 = fig.add_subplot(133)
    ax3.plot(t, trajectory[:, 3], 'c--', label=f'{relational_space.name1} transformación', linewidth=2)
    ax3.plot(t, trajectory[:, 4], 'm--', label=f'{relational_space.name2} transformación', linewidth=2)
    ax3.set_xlabel('Tiempo de interacción')
    ax3.set_ylabel('Factor de transformación')
    ax3.set_title('Transformación de cada cristal')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"[Visualización] Guardado: {save_path}")
    
    plt.show()


if __name__ == "__main__":
    print("\n[RYP_LEVEL5_INTERACCION.py]")
    print("Módulo de Nivel 5: Dimensión de Interacción (5D)")
    print("Use: from RYP_LEVEL5_INTERACCION import create_relational_space")
