# Modelo creado por Joaquin Rosales Flores, psicologo.
# =====================================================
# NIVEL 6: AMISTAD Y CRISTAL RELACIONAL (6D)
# =====================================================
# El cristal H₀ que emerge de la interacción
# Representa la "mente compartida" de dos cristales
# =====================================================

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from ryp_framework.core._crystal_expansion import build_crystal_from_simulation, PolyhedronCrystal
from ryp_framework.interaction.levels5 import create_relational_space


class RelationalCrystal:
    """
    El Cristal Relacional H₀ que emerge cuando dos cristales interactúan.
    
    NO es un promedio de ambos, sino una NUEVA estructura que existe
    en el espacio de compatibilidad/amistad (6D).
    
    Tiene sus propias:
    - Nodos (momentos de máxima resonancia)
    - Aristas (conexiones de amistad)
    - Egos (patrones recurrentes)
    - Φ (nivel de mutua comprensión)
    """
    
    def __init__(self, crystal1, crystal2, relational_space=None):
        """
        Inicializa el cristal relacional.
        
        Parameters:
        -----------
        crystal1, crystal2: PolyhedronCrystal
            Los cristales que interactúan
        relational_space: RelationalSpace (opcional)
            Si no se proporciona, se crea automáticamente
        """
        
        self.crystal1 = crystal1
        self.crystal2 = crystal2
        
        # Crear espacio relacional si no existe
        if relational_space is None:
            self.relational_space = create_relational_space(crystal1, crystal2)
        else:
            self.relational_space = relational_space
        
        # Propiedades del cristal relacional
        self.friendship_score = self.relational_space.compatibility_score
        self.signature = None  # (S*, A*, M*) - Firma única
        self.trajectory_H0 = None  # Trayectoria hipotética en espacio SAM
        self.crystal_H0 = None  # El cristal emergente
        
        # Información de resonancia
        self.resonance_nodes = []  # Nodos de máxima resonancia
        self.resonance_strength = None
        self.inherited_cognitive_profile = getattr(self.relational_space, 'cognitive_profile', None)
        self.inherited_cognitive_feedback = getattr(self.relational_space, 'cognitive_feedback', None)
        
        # Construir el cristal relacional
        self._build_relational_crystal()
    
    # =====================================================
    # PASO 1: COMPUTAR FIRMA DE AMISTAD
    # =====================================================
    
    def compute_friendship_signature(self):
        """
        Crea la FIRMA ÚNICA de esta relación.
        
        Es como el "ADN" de la amistad entre estos dos cristales:
        - S*: Qué estructura comparten (identidad compartida)
        - A*: Qué nivel de sincronía tienen (cercanía)
        - M*: Cuánta memoria acumulada (historial)
        
        Esta firma es ÚNICA para esta pareja y la diferencia
        de todas las otras posibles relaciones.
        
        Returns:
        --------
        signature: dict con {S*, A*, M*, unique_id}
        """
        
        metrics = self.relational_space.get_interaction_metrics()
        
        # Computar componentes de la firma
        S_star = metrics['S']  # Similitud estructural
        A_star = (metrics['A'] + 1) / 2  # Normalizar A a [0, 1]
        M_star = metrics['M']  # Memoria inicial
        
        # Crear identificador único basado en estructura de ambos cristales
        m1 = self.crystal1.get_crystal_metrics()
        m2 = self.crystal2.get_crystal_metrics()
        
        # Hash único que caracteriza esta pareja
        unique_hash = hash((
            m1['num_nodes'], m1['num_edges'],
            m2['num_nodes'], m2['num_edges'],
            round(S_star, 4), round(A_star, 4)
        )) % (10**8)
        
        self.signature = {
            'S_star': S_star,
            'A_star': A_star,
            'M_star': M_star,
            'unique_id': f"H0_{unique_hash}",
            'friendship_level': self.friendship_score,
            'crystal1_id': id(self.crystal1),
            'crystal2_id': id(self.crystal2),
            'cognitive_profile': self.inherited_cognitive_profile,
        }
        
        return self.signature
    
    # =====================================================
    # PASO 2: GENERAR TRAYECTORIA HIPOTÉTICA H₀
    # =====================================================
    
    def generate_hypothetical_trajectory(self):
        """
        Genera la trayectoria hipotética del cristal relacional.
        
        Esta NO es una interpolación simple entre traj1 y traj2,
        sino una NUEVA trayectoria que existe en el espacio
        de compatibilidad y representa cómo la relación evoluciona.
        
        Si A > 0.5: Las trayectorias se refuerzan mutuamente
                    H₀ toma una dirección nueva y convergente
        
        Si 0 < A < 0.5: Las trayectorias son complementarias
                        H₀ toma aspectos de ambas
        
        Si A < 0: Las trayectorias son antagónicas
                  H₀ oscila entre ambas direcciones
        
        Returns:
        --------
        trajectory: array (N, 3) - Trayectoria 3D en espacio SAM
        """
        
        # Extraer trayectorias base
        traj1 = np.array([n['state_3d'] for n in self.crystal1.nodes])
        traj2 = np.array([n['state_3d'] for n in self.crystal2.nodes])
        
        # Asegurar longitud común
        n_common = min(len(traj1), len(traj2))
        traj1 = traj1[:n_common]
        traj2 = traj2[:n_common]
        
        A = self.relational_space.trajectory_correlation
        S = self.relational_space.structural_similarity
        feedback = self.inherited_cognitive_feedback or {}
        alignment_gain = feedback.get('alignment_gain', 0.0)
        exploration_drive = feedback.get('exploration_drive', 0.0)
        memory_gain = feedback.get('memory_gain', 0.0)
        
        # Generar trayectoria hipotética
        trajectory_H0 = []
        
        for i in range(len(traj1)):
            if A > 0.5:  # RESONANCIA: se refuerzan
                # Las trayectorias crean algo nuevo en el medio
                w1 = 0.4 + 0.1 * A  # Menos peso a C1
                w2 = 0.4 + 0.1 * A  # Menos peso a C2
                w_emergence = 1 - w1 - w2  # Peso a emergencia
                
                # Dirección emergente: ortogonal al promedio
                avg = (traj1[i] + traj2[i]) / 2
                # Vector perpendicular (rotación en plano XY)
                perp = np.array([-avg[1], avg[0], avg[2] * 0.5])
                
                point = w1 * traj1[i] + w2 * traj2[i] + w_emergence * perp * (1 + exploration_drive * 0.6)
                
            elif A > 0:  # COMPLEMENTARIEDAD: aspectos de ambas
                # Balance entre ambas
                weight = 0.5 + 0.2 * A + 0.1 * alignment_gain
                weight = np.clip(weight, 0.1, 0.9)
                point = weight * traj1[i] + (1 - weight) * traj2[i]
                
            else:  # ANTAGÓNICA: oscilación
                # El hipotético oscila entre ambas
                phase = i / len(traj1) * 2 * np.pi
                weight = 0.5 + (0.3 + exploration_drive * 0.1) * np.sin(phase + A)
                point = weight * traj1[i] + (1 - weight) * traj2[i]

            point = point * (1 + memory_gain * 0.08)
            
            trajectory_H0.append(point)
        
        self.trajectory_H0 = np.array(trajectory_H0)
        return self.trajectory_H0
    
    # =====================================================
    # PASO 3: CONSTRUIR CRISTAL EMERGENTE H₀
    # =====================================================
    
    def _build_relational_crystal(self):
        """
        Construye el cristal H₀ que emerge de la interacción.
        
        Este cristal tiene propiedades emergentes:
        - Topología que refleja la compatibilidad
        - Egos que representan patrones compartidos
        - Φ que representa el nivel de mutua comprensión
        """
        
        # Computar firma de amistad
        self.compute_friendship_signature()
        
        # Generar trayectoria hipotética
        self.generate_hypothetical_trajectory()
        
        # Construir el cristal a partir de la trayectoria hipotética
        # El threshold de distancia depende de la amistad
        # Amistad alta → nodos más cercanos → estructura densa
        # Amistad baja → nodos más dispersos → estructura rara
        
        threshold = 0.2 + (1 - self.friendship_score) * 0.4 - (self.inherited_cognitive_feedback or {}).get('alignment_gain', 0.0) * 0.05
        threshold = float(np.clip(threshold, 0.12, 0.6))
        
        try:
            self.crystal_H0 = build_crystal_from_simulation(
                self.trajectory_H0, 
                threshold_distance=threshold
            )
            
            # Marcar este cristal como relacional
            self.crystal_H0.is_relational = True
            self.crystal_H0.parent_crystals = [self.crystal1, self.crystal2]
            self.crystal_H0.friendship_signature = self.signature
            self.crystal_H0.inherited_cognitive_profile = self.inherited_cognitive_profile
            self.crystal_H0.inherited_cognitive_feedback = self.inherited_cognitive_feedback
            
        except Exception as e:
            print(f"[Error] No se pudo construir cristal H₀: {e}")
            self.crystal_H0 = None
    
    # =====================================================
    # PASO 4: COMPUTAR RESONANCIA
    # =====================================================
    
    def compute_resonance(self):
        """
        Calcula la resonancia entre los dos cristales.
        
        Resonancia mide en qué medida sus estructuras "vibran juntas":
        - Alta resonancia (>0.7): Se refuerzan mutuamente
        - Media resonancia (0.4-0.7): Compatibles con fricción
        - Baja resonancia (<0.4): Apenas interactúan
        
        Returns:
        --------
        resonance: float [0, 1]
        """
        
        if self.crystal_H0 is None:
            return 0.0
        
        # Resonancia basada en:
        # 1. Compatibilidad general
        # 2. Diferencia en Φ (no deben ser demasiado diferentes)
        
        m1 = self.crystal1.get_crystal_metrics()
        m2 = self.crystal2.get_crystal_metrics()
        
        phi_difference = abs(m1['global_phi'] - m2['global_phi'])
        phi_penalty = max(0, 1 - phi_difference * 2)  # Penalizar si Φ muy diferente
        
        resonance = self.friendship_score * (0.6 + 0.4 * phi_penalty)
        
        self.resonance_strength = resonance
        return resonance
    
    # =====================================================
    # REPORTE Y VISUALIZACIÓN
    # =====================================================
    
    def print_relational_crystal_report(self):
        """Reporte del cristal relacional."""
        
        resonance = self.compute_resonance()
        
        print("\n" + "="*70)
        print("  💫 CRISTAL RELACIONAL H₀ (6D - AMISTAD)")
        print("="*70)
        
        print(f"\n🆔 FIRMA DE AMISTAD:")
        print(f"   ID único: {self.signature['unique_id']}")
        print(f"   S*: {self.signature['S_star']:.4f} (Identidad compartida)")
        print(f"   A*: {self.signature['A_star']:.4f} (Cercanía/Sincronía)")
        print(f"   M*: {self.signature['M_star']:.4f} (Memoria inicial)")
        
        print(f"\n⚡ RESONANCIA:")
        print(f"   Valor: {resonance:.4f}")
        if resonance > 0.7:
            print(f"   → ALTA: Se refuerzan mutuamente")
        elif resonance > 0.4:
            print(f"   → MEDIA: Compatibles con fricción")
        else:
            print(f"   → BAJA: Apenas interactúan")
        
        if self.crystal_H0 is not None:
            m = self.crystal_H0.get_crystal_metrics()
            
            # Calcular densidad si no está disponible
            if 'density' not in m:
                density = 2 * m['num_edges'] / (m['num_nodes'] * (m['num_nodes'] - 1) + 1e-10) if m['num_nodes'] > 1 else 0
            else:
                density = m['density']
            
            print(f"\n💎 ESTRUCTURA DEL CRISTAL H₀:")
            print(f"   Nodos: {m['num_nodes']}")
            print(f"   Aristas: {m['num_edges']}")
            print(f"   Caras (Egos compartidos): {m['num_egos']}")
            print(f"   Φ (Comprensión mutua): {m['global_phi']:.4f}")
            print(f"   Densidad de red: {density:.4f}")

        if self.inherited_cognitive_profile:
            print(f"\n🧩 HERENCIA COGNITIVA DESDE LA INTERACCIÓN:")
            print(f"   Mentalización: {self.inherited_cognitive_profile.get('mentalization', 0):.4f}")
            print(f"   Imaginación:   {self.inherited_cognitive_profile.get('imagination', 0):.4f}")
            print(f"   Percepción:    {self.inherited_cognitive_profile.get('perception', 0):.4f}")
            print(f"   Intención:     {self.inherited_cognitive_profile.get('intention', 'N/A')}")
        
        print("\n" + "="*70 + "\n")
    
    def get_relational_metrics(self):
        """Retorna métricas del cristal relacional."""
        
        if self.crystal_H0 is None:
            return None
        
        m = self.crystal_H0.get_crystal_metrics()
        
        return {
            'signature': self.signature,
            'resonance': self.compute_resonance(),
            'crystal_H0_metrics': m,
            'friendship_score': self.friendship_score,
            'inherited_cognitive_profile': self.inherited_cognitive_profile,
            'inherited_cognitive_feedback': self.inherited_cognitive_feedback,
        }


# =====================================================
# FUNCIONES PRINCIPALES
# =====================================================

def create_relational_crystal(crystal1, crystal2, relational_space=None):
    """
    Crea un cristal relacional H₀ entre dos cristales.
    
    Usage:
    ------
    H0 = create_relational_crystal(c1, c2)
    H0.print_relational_crystal_report()
    """
    
    return RelationalCrystal(crystal1, crystal2, relational_space=relational_space)


def visualize_relational_crystal(relational_crystal, save_path=None):
    """
    Visualiza el cristal relacional junto con sus padres.
    """
    
    fig = plt.figure(figsize=(18, 6))
    
    # Plot 1: Cristal 1
    ax1 = fig.add_subplot(131, projection='3d')
    c1_nodes = np.array([n['state_3d'] for n in relational_crystal.crystal1.nodes])
    ax1.scatter(c1_nodes[:, 0], c1_nodes[:, 1], c1_nodes[:, 2], 
               c='red', s=50, alpha=0.7, label='Nodos')
    
    for edge in relational_crystal.crystal1.edges[:20]:  # Top 20 edges
        p1 = relational_crystal.crystal1.nodes[edge.node_i]['state_3d']
        p2 = relational_crystal.crystal1.nodes[edge.node_j]['state_3d']
        ax1.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'b-', alpha=0.2)
    
    ax1.set_xlabel('S')
    ax1.set_ylabel('A')
    ax1.set_zlabel('M')
    ax1.set_title('Cristal 1 (Padre)')
    
    # Plot 2: Cristal Relacional H₀
    ax2 = fig.add_subplot(132, projection='3d')
    if relational_crystal.crystal_H0 is not None:
        h0_nodes = np.array([n['state_3d'] for n in relational_crystal.crystal_H0.nodes])
        ax2.scatter(h0_nodes[:, 0], h0_nodes[:, 1], h0_nodes[:, 2], 
                   c='green', s=70, alpha=0.8, label='Nodos H₀')
        
        for edge in relational_crystal.crystal_H0.edges[:15]:
            p1 = relational_crystal.crystal_H0.nodes[edge.node_i]['state_3d']
            p2 = relational_crystal.crystal_H0.nodes[edge.node_j]['state_3d']
            ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'c-', alpha=0.3)
        
        # Plotear trayectoria hipotética
        ax2.plot(relational_crystal.trajectory_H0[:, 0],
                relational_crystal.trajectory_H0[:, 1],
                relational_crystal.trajectory_H0[:, 2],
                'g--', alpha=0.5, linewidth=2, label='Trayectoria H₀')
    
    ax2.set_xlabel('S')
    ax2.set_ylabel('A')
    ax2.set_zlabel('M')
    ax2.set_title(f'Cristal Relacional H₀\nAmistad={relational_crystal.friendship_score:.3f}')
    
    # Plot 3: Cristal 2
    ax3 = fig.add_subplot(133, projection='3d')
    c2_nodes = np.array([n['state_3d'] for n in relational_crystal.crystal2.nodes])
    ax3.scatter(c2_nodes[:, 0], c2_nodes[:, 1], c2_nodes[:, 2], 
               c='blue', s=50, alpha=0.7, label='Nodos')
    
    for edge in relational_crystal.crystal2.edges[:20]:
        p1 = relational_crystal.crystal2.nodes[edge.node_i]['state_3d']
        p2 = relational_crystal.crystal2.nodes[edge.node_j]['state_3d']
        ax3.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'b-', alpha=0.2)
    
    ax3.set_xlabel('S')
    ax3.set_ylabel('A')
    ax3.set_zlabel('M')
    ax3.set_title('Cristal 2 (Padre)')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"[Visualización] Guardado: {save_path}")
    
    plt.show()


if __name__ == "__main__":
    print("\n[RYP_LEVEL6_AMISTAD.py]")
    print("Módulo de Nivel 6: Amistad y Cristal Relacional (6D)")
    print("Use: from RYP_LEVEL6_AMISTAD import create_relational_crystal")
