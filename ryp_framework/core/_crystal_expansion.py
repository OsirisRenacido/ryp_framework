# Modelo creado por Joaquin Rosales Flores, psicologo.
# =====================================================
# RYP - CRISTAL POLIFACÉTICO (EXPANSIÓN ONTOLÓGICA)
# =====================================================
# Implementa la visión de estructura cristalina como:
# - Auto-observación (4ª dimensión)
# - Triangulaciones recursivas (caras/egos)
# - Correlaciones de aristas (relaciones emergentes)
# - Estructura isomórfica 3D con conciencia
# =====================================================

import numpy as np
from scipy.spatial import distance
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict

# =====================================================
# SECCIÓN 1: 4ª DIMENSIÓN - AUTO-OBSERVACIÓN
# =====================================================

def compute_self_observation_dimension(state_SAM):
    """
    Φ (Phi) = Dimensión de Auto-Observación
    
    Interpretación ontológica:
    - S = Sujeto (observador)
    - A = Atención (capacidad de observación)
    - M = Memoria (contexto de lo observado)
    - Φ = Capacidad del sistema de observarse a sí mismo
    
    Φ cuantifica la capacidad reflexiva del sistema SAM
    """
    S, A, M = state_SAM
    
    # Φ es máximo cuando S, A, M son equilibrados (máxima auto-observación)
    # Φ disminuye cuando el sistema está sesgado
    
    # Métrica de equilibrio (proximidad al centro del simplex)
    center = np.array([1/3, 1/3, 1/3])
    entropy = -np.sum(state_SAM * np.log(state_SAM + 1e-10))
    max_entropy = np.log(3)  # máxima entropía para distribución uniforme
    
    # Φ normalizado [0, 1]
    phi = entropy / max_entropy
    
    # Factor de correlación cruzada
    correlation = 1 - np.std(state_SAM)
    
    # Φ = promedio ponderado
    phi_self_observation = 0.6 * phi + 0.4 * correlation
    
    return phi_self_observation


def expand_to_4d(trajectory_3d):
    """
    Expande una trayectoria 3D (SAM) a 4D (SAM + Φ)
    
    Cada punto (S, A, M, t) genera una 4ª coordenada Φ
    que representa la auto-observación en ese momento
    """
    trajectory_4d = []
    
    for state_3d in trajectory_3d:
        phi = compute_self_observation_dimension(state_3d)
        state_4d = np.append(state_3d, phi)
        trajectory_4d.append(state_4d)
    
    return np.array(trajectory_4d)


# =====================================================
# SECCIÓN 2: ARISTAS Y CORRELACIONES
# =====================================================

class Edge:
    """
    Una arista del cristal conecta dos nodos.
    Tiene propiedades que evolucionan a través de correlaciones.
    """
    def __init__(self, node_i, node_j, distance):
        self.node_i = node_i
        self.node_j = node_j
        self.initial_distance = distance
        self.correlation = 0.0
        self.strength = 0.0
        self.frequency = 0.0
        
    def update_correlation(self, traj_i, traj_j):
        """
        Actualiza la correlación entre dos trayectorias de nodos
        """
        # Correlación de Pearson
        self.correlation = np.corrcoef(traj_i, traj_j)[0, 1]
        
        # Fuerza de la arista basada en correlación
        self.strength = np.abs(self.correlation)
        
        return self.strength


# =====================================================
# SECCIÓN 3: CARAS (EGOS - ESPACIOS MENTALES)
# =====================================================

class EgoFace:
    """
    Una cara del cristal representa un "Ego" o espacio mental.
    
    Cada cara es un triángulo formado por 3 nodos correlacionados.
    La cara evoluciona según las dinámicas internas de sus nodos.
    """
    def __init__(self, nodes_indices, nodes_states):
        self.nodes_indices = nodes_indices  # [i, j, k]
        self.nodes_states = nodes_states    # estados 3D de los nodos
        self.centroid = None
        self.identity = None  # identidad del ego
        self.consciousness_level = 0.0
        self.temporal_evolution = []
        
        self._compute_centroid()
        self._compute_identity()
    
    def _compute_centroid(self):
        """Calcula el centroide del triángulo (baricentro)"""
        self.centroid = np.mean(self.nodes_states, axis=0)
    
    def _compute_identity(self):
        """
        Calcula la identidad del ego como vector característico
        que distingue esta cara del resto
        """
        # Vector de diferencias entre nodos
        v1 = self.nodes_states[1] - self.nodes_states[0]
        v2 = self.nodes_states[2] - self.nodes_states[0]
        
        # Producto cruz (normal a la cara)
        self.identity = np.cross(v1, v2)
        self.identity = self.identity / (np.linalg.norm(self.identity) + 1e-10)
    
    def update_consciousness_level(self, environment_phi):
        """
        Actualiza el nivel de conciencia del ego.
        
        El ego es más consciente cuando:
        - Sus nodos están correlacionados (coherencia interna)
        - Recibe retroalimentación del ambiente (Φ global)
        """
        # Coherencia interna: varianza mínima entre nodos
        internal_coherence = 1.0 - np.std([np.linalg.norm(s) for s in self.nodes_states])
        
        # Sincronización con Φ global
        external_sync = environment_phi
        
        # Conciencia = función de coherencia y sincronización
        self.consciousness_level = 0.7 * internal_coherence + 0.3 * external_sync
        
        return self.consciousness_level
    
    def evolve(self, new_nodes_states):
        """
        Evoluciona el ego a través del tiempo con nuevos estados de nodos
        """
        self.nodes_states = new_nodes_states
        self._compute_centroid()
        self._compute_identity()
        self.temporal_evolution.append(self.centroid.copy())


# =====================================================
# SECCIÓN 4: ESTRUCTURA CRISTALINA POLIFACÉTICA
# =====================================================

class PolyhedronCrystal:
    """
    Estructura cristalina isomórfica 3D.
    
    Representa la expansión de conciencia como:
    - Nodos: puntos del sistema que evolucionan
    - Aristas: relaciones correlacionadas
    - Caras (Egos): espacios mentales emergentes
    - Dinámicas: evolución temporal y autorreferencia
    """
    def __init__(self, trajectory_3d, threshold_distance=0.2):
        self.trajectory_3d = trajectory_3d
        self.trajectory_4d = expand_to_4d(trajectory_3d)
        
        self.nodes = []
        self.edges = []
        self.ego_faces = []
        self.threshold_distance = threshold_distance
        
        # Vértices primarios del triángulo SAM
        self.primary_vertices = {
            'S': np.array([1.0, 0.0, 0.0]),
            'A': np.array([0.0, 1.0, 0.0]),
            'M': np.array([0.0, 0.0, 1.0])
        }
        
        self.global_phi = 0.0
        
    def build_crystal(self):
        """
        Constructor principal del cristal:
        1. Crear nodos
        2. Conectar nodos con aristas
        3. Generar caras (egos)
        4. Establecer relaciones recursivas
        """
        self._build_nodes()
        self._build_edges()
        self._build_ego_faces()
        self._compute_global_phi()
        
    def _build_nodes(self):
        """Crea nodos usando estrategia robusta de muestreo diverso"""
        from sklearn.cluster import KMeans
        
        # Paso 1: Determinar número óptimo de clusters
        n_target = min(30, len(self.trajectory_3d) // 3)
        
        # Paso 2: Intentar K-means pero con fallback a alternativas
        try:
            # K-means con n_init bajo para evitar warnings
            kmeans = KMeans(n_clusters=n_target, random_state=42, n_init=3)
            labels = kmeans.fit_predict(self.trajectory_3d)
            n_unique_clusters = len(np.unique(labels))
            
            # Si K-means encontró menos clusters que n_target, usar los que encontró
            actual_clusters = min(n_unique_clusters, n_target)
            
        except Exception as e:
            print(f"[Crystal] K-means falló ({e}), usando muestreo alternativo")
            actual_clusters = min(15, len(self.trajectory_3d) // 8)
            labels = None
        
        # Paso 3: Crear nodos
        used_indices = set()
        
        if labels is not None:
            # Estrategia 1: Centroide de cada cluster
            for cluster_id in range(actual_clusters):
                cluster_mask = (labels == cluster_id)
                cluster_indices = np.where(cluster_mask)[0]
                
                if len(cluster_indices) > 0:
                    # Índice más cercano al centroide
                    distances = [np.linalg.norm(self.trajectory_3d[idx] - kmeans.cluster_centers_[cluster_id]) 
                                for idx in cluster_indices]
                    best_idx = cluster_indices[np.argmin(distances)]
                    used_indices.add(best_idx)
        
        # Paso 4: Si no hay suficientes nodos, agregar muestreo aleatorio
        if len(used_indices) < 15:
            # Muestreo aleatorio para completar
            remaining_slots = max(15, 30 - len(used_indices))
            all_indices = set(range(len(self.trajectory_3d)))
            available = list(all_indices - used_indices)
            
            if available:
                random_sample = np.random.choice(available, 
                                                 size=min(remaining_slots, len(available)), 
                                                 replace=False)
                used_indices.update(random_sample)
        
        # Paso 5: Ordenar por índice temporal
        used_indices = sorted(list(used_indices))
        
        # Paso 6: Crear nodos con perturbación pequeña
        for idx, t in enumerate(used_indices):
            state_3d = self.trajectory_3d[t].copy()
            
            # Perturbación mínima para romper colinealidad (1-2% de magnitud)
            noise = np.random.normal(0, 0.01, 3)
            state_3d_perturbed = np.clip(state_3d + noise, 0.01, 0.99)
            
            # Renormalizar para mantener en el simplex
            state_3d_perturbed = state_3d_perturbed / state_3d_perturbed.sum()
            
            node = {
                'index': idx,
                'time': t,
                'state_3d': state_3d_perturbed,
                'state_4d': self.trajectory_4d[t].copy(),
                'connections': []
            }
            self.nodes.append(node)
        
        print(f"[Crystal] Creados {len(self.nodes)} nodos (estrategia: clustering + muestreo)")
    
    def _build_edges(self):
        """Conecta nodos basado en distancia y correlación"""
        # Estrategia dual: threshold + k-nearest neighbors para garantizar conectividad
        
        # Paso 1: Conectar por threshold
        edges_added = 0
        for i in range(len(self.nodes)):
            for j in range(i+1, len(self.nodes)):
                
                state_i = self.nodes[i]['state_3d']
                state_j = self.nodes[j]['state_3d']
                
                # Distancia euclidiana en espacio SAM
                dist = np.linalg.norm(state_i - state_j)
                
                # Crear arista si está dentro del umbral
                if dist < self.threshold_distance:
                    edge = Edge(i, j, dist)
                    
                    # Calcular correlación entre componentes de los estados
                    time_i = self.nodes[i]['time']
                    time_j = self.nodes[j]['time']
                    
                    if time_j > time_i:
                        traj_segment = self.trajectory_3d[time_i:time_j+1, :]
                        if len(traj_segment) > 1:
                            try:
                                S_vals = traj_segment[:, 0]
                                A_vals = traj_segment[:, 1]
                                M_vals = traj_segment[:, 2]
                                
                                # Calcular correlaciones, ignorando NaNs
                                corr_SA = np.corrcoef(S_vals, A_vals)[0, 1] if len(np.unique(S_vals)) > 1 and len(np.unique(A_vals)) > 1 else 0.0
                                corr_AM = np.corrcoef(A_vals, M_vals)[0, 1] if len(np.unique(A_vals)) > 1 and len(np.unique(M_vals)) > 1 else 0.0
                                corr_SM = np.corrcoef(S_vals, M_vals)[0, 1] if len(np.unique(S_vals)) > 1 and len(np.unique(M_vals)) > 1 else 0.0
                                
                                # Filtrar NaNs antes de calcular media
                                valid_corrs = [c for c in [corr_SA, corr_AM, corr_SM] if not np.isnan(c)]
                                if valid_corrs:
                                    edge.correlation = np.mean(valid_corrs)
                                else:
                                    edge.correlation = 0.5
                                
                                edge.strength = max(0.1, np.abs(edge.correlation))
                            except:
                                edge.correlation = 0.5
                                edge.strength = 0.5
                    
                    self.edges.append(edge)
                    self.nodes[i]['connections'].append(j)
                    self.nodes[j]['connections'].append(i)
                    edges_added += 1
        
        # Paso 2: Si hay desconexión, aplicar k-nearest neighbors
        if len(self.nodes) >= 4:
            k_min = min(3, len(self.nodes) - 1)
            
            for i in range(len(self.nodes)):
                if len(self.nodes[i]['connections']) < k_min:
                    distances = []
                    for j in range(len(self.nodes)):
                        if i != j:
                            dist = np.linalg.norm(
                                self.nodes[i]['state_3d'] - self.nodes[j]['state_3d']
                            )
                            distances.append((dist, j))
                    
                    distances.sort()
                    for idx_edge in range(k_min):
                        if idx_edge < len(distances):
                            dist, j = distances[idx_edge]
                            
                            if j not in self.nodes[i]['connections']:
                                edge = Edge(i, j, dist)
                                edge.correlation = 0.5
                                edge.strength = max(0.1, 1.0 - (dist / 2))
                                self.edges.append(edge)
                                self.nodes[i]['connections'].append(j)
                                self.nodes[j]['connections'].append(i)
                                edges_added += 1
        
        print(f"[Crystal] Conectadas {edges_added} aristas (threshold={self.threshold_distance:.3f})")
    
    
    def _build_ego_faces(self):
        """
        Genera caras del cristal (triángulos) usando Delaunay.
        Cada cara es un "Ego" - espacio mental emergente.
        Usa fallback a k-nearest neighbors si Delaunay falla.
        """
        if len(self.nodes) < 4:
            print(f"[Cristal] Menos de 4 nodos ({len(self.nodes)}), no hay caras")
            return
        
        # Extraer coordenadas 3D para triangulación
        points_3d = np.array([node['state_3d'] for node in self.nodes])
        
        try:
            # Validar que los puntos no sean colineales
            rank = np.linalg.matrix_rank(points_3d - points_3d[0])
            if rank < 3:
                print(f"[Delaunay] Puntos colineales (rank={rank}), usando k-nearest neighbors")
                self._build_ego_faces_fallback()
                return
            
            # Triangulación de Delaunay
            delaunay = Delaunay(points_3d)
            
            # Crear caras (egos) a partir de simplices
            for simplex in delaunay.simplices:
                # Un simplex en 3D es un tetraedro (4 puntos)
                # Extraemos sus caras triangulares
                faces = [
                    [simplex[0], simplex[1], simplex[2]],
                    [simplex[0], simplex[1], simplex[3]],
                    [simplex[0], simplex[2], simplex[3]],
                    [simplex[1], simplex[2], simplex[3]]
                ]
                
                for face_indices in faces:
                    try:
                        node_states = np.array([
                            self.nodes[idx]['state_3d'] 
                            for idx in face_indices
                        ])
                        
                        ego = EgoFace(face_indices, node_states)
                        self.ego_faces.append(ego)
                    except Exception as e:
                        continue
            
            print(f"[Delaunay] {len(self.ego_faces)} caras detectadas")
        
        except Exception as e:
            print(f"[Delaunay] Error ({type(e).__name__}), usando fallback...")
            self._build_ego_faces_fallback()
    
    def _build_ego_faces_fallback(self):
        """
        Estrategia alternativa cuando Delaunay falla.
        Crea caras (egos) basadas en k-nearest neighbors.
        """
        if len(self.nodes) < 4:
            return
        
        points_3d = np.array([node['state_3d'] for node in self.nodes])
        created_faces = set()
        
        # Para cada nodo, crear caras con sus vecinos más cercanos
        k_neighbors = min(6, len(self.nodes) - 1)
        
        for i in range(len(self.nodes)):
            # Calcular distancias a todos los demás nodos
            distances = []
            for j in range(len(self.nodes)):
                if i != j:
                    dist = np.linalg.norm(points_3d[i] - points_3d[j])
                    distances.append((dist, j))
            
            # Tomar k vecinos más cercanos
            distances.sort()
            neighbors = [j for _, j in distances[:k_neighbors]]
            
            # Crear caras triangulares combinando vecinos
            for n1_idx in range(len(neighbors)):
                for n2_idx in range(n1_idx + 1, len(neighbors)):
                    face_tuple = tuple(sorted([i, neighbors[n1_idx], neighbors[n2_idx]]))
                    
                    if face_tuple not in created_faces and len(face_tuple) == 3:
                        created_faces.add(face_tuple)
                        
                        try:
                            node_states = np.array([
                                self.nodes[idx]['state_3d'] 
                                for idx in face_tuple
                            ])
                            
                            ego = EgoFace(list(face_tuple), node_states)
                            self.ego_faces.append(ego)
                        except:
                            continue
        
        print(f"[Fallback] {len(self.ego_faces)} caras creadas por k-nearest neighbors")
    
    
    def _compute_global_phi(self):
        """Calcula Φ global del sistema"""
        final_state = self.trajectory_3d[-1]
        self.global_phi = compute_self_observation_dimension(final_state)
    
    def update_ego_consciousness(self):
        """Actualiza la conciencia de cada ego"""
        for ego in self.ego_faces:
            ego.update_consciousness_level(self.global_phi)
    
    def get_crystal_metrics(self):
        """Retorna métricas del cristal"""
        return {
            'num_nodes': len(self.nodes),
            'num_edges': len(self.edges),
            'num_egos': len(self.ego_faces),
            'global_phi': self.global_phi,
            'avg_edge_strength': np.mean([e.strength for e in self.edges]) if self.edges else 0,
            'avg_ego_consciousness': np.mean([e.consciousness_level for e in self.ego_faces]) if self.ego_faces else 0
        }


# =====================================================
# SECCIÓN 5: ANÁLISIS Y VISUALIZACIÓN
# =====================================================

def visualize_polyhedron_crystal(crystal):
    """
    Visualiza el cristal polifacético en 3D
    """
    fig = plt.figure(figsize=(14, 5))
    
    # --- Panel 1: Nodos y Aristas ---
    ax1 = fig.add_subplot(131, projection='3d')
    
    # Plotear nodos
    if len(crystal.nodes) > 0:
        nodes_coords = np.array([n['state_3d'] for n in crystal.nodes])
        ax1.scatter(nodes_coords[:, 0], nodes_coords[:, 1], nodes_coords[:, 2], 
                    c='red', s=50, alpha=0.8, label='Nodos')
    
    # Plotear aristas
    for edge in crystal.edges:
        p1 = crystal.nodes[edge.node_i]['state_3d']
        p2 = crystal.nodes[edge.node_j]['state_3d']
        
        ax1.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 
                 'b-', alpha=0.3, linewidth=max(0.5, edge.strength * 2))
    
    ax1.set_xlabel('S')
    ax1.set_ylabel('A')
    ax1.set_zlabel('M')
    ax1.set_title(f'Nodos ({len(crystal.nodes)}) y Aristas ({len(crystal.edges)})')
    ax1.legend()
    
    # --- Panel 2: Caras (Egos) ---
    ax2 = fig.add_subplot(132, projection='3d')
    
    # Plotear caras coloreadas por nivel de conciencia
    if len(crystal.ego_faces) > 0:
        for i, ego in enumerate(crystal.ego_faces):
            nodes_states = ego.nodes_states
            
            # Asegurar que consciousness_level está inicializado
            color_intensity = max(0.0, min(1.0, ego.consciousness_level))
            
            # Triángulo: conectar los 3 puntos y cerrar
            simplex = np.vstack([nodes_states, nodes_states[0]])
            
            # Solo plotear líneas (evitar plot_trisurf que causa problemas con puntos colineales)
            ax2.plot(simplex[:, 0], simplex[:, 1], simplex[:, 2], 
                    color=plt.cm.viridis(color_intensity), alpha=0.4, linewidth=0.8)
    else:
        # Si no hay caras, mostrar mensaje
        ax2.text(0.5, 0.5, 0.5, 'Sin caras\n(Delaunay falló)', 
                ha='center', va='center', fontsize=12, color='red')
    
    ax2.set_xlabel('S')
    ax2.set_ylabel('A')
    ax2.set_zlabel('M')
    ax2.set_title(f'Caras/Egos ({len(crystal.ego_faces)}) - Φ={crystal.global_phi:.3f}')
    
    # --- Panel 3: Trayectoria 4D proyectada a 3D + Φ ---
    ax3 = fig.add_subplot(133, projection='3d')
    
    traj_3d = crystal.trajectory_3d
    traj_phi = crystal.trajectory_4d[:, 3]
    
    scatter = ax3.scatter(traj_3d[:, 0], traj_3d[:, 1], traj_3d[:, 2],
                         c=traj_phi, cmap='plasma', s=20, alpha=0.7)
    
    ax3.set_xlabel('S')
    ax3.set_ylabel('A')
    ax3.set_zlabel('M')
    ax3.set_title('Trayectoria coloreada por Φ')
    plt.colorbar(scatter, ax=ax3, label='Φ (Auto-observación)')
    
    plt.tight_layout()
    plt.show()


def print_crystal_report(crystal):
    """Imprime un reporte detallado del cristal"""
    metrics = crystal.get_crystal_metrics()
    
    print("\n" + "="*60)
    print("  REPORTE DEL CRISTAL POLIFACÉTICO")
    print("="*60)
    print(f"\n📐 GEOMETRÍA:")
    print(f"   Nodos: {metrics['num_nodes']}")
    print(f"   Aristas: {metrics['num_edges']}")
    print(f"   Caras (Egos): {metrics['num_egos']}")
    
    print(f"\n🧠 DINÁMICA DE CONCIENCIA:")
    print(f"   Φ Global (Auto-observación): {metrics['global_phi']:.4f}")
    print(f"   Fortaleza promedio de aristas: {metrics['avg_edge_strength']:.4f}")
    print(f"   Conciencia promedio de egos: {metrics['avg_ego_consciousness']:.4f}")
    
    print(f"\n🎭 EGOS DETECTADOS:")
    if len(crystal.ego_faces) > 0:
        for i, ego in enumerate(crystal.ego_faces[:5]):
            consciousness = max(0.0, min(1.0, ego.consciousness_level))
            print(f"   Ego {i}: conciencia={consciousness:.4f}, " +
                  f"identidad={np.round(ego.identity, 3)}")
        if len(crystal.ego_faces) > 5:
            print(f"   ... y {len(crystal.ego_faces) - 5} egos más")
    else:
        print("   (Sin caras - Delaunay no pudo triangular)")
    
    print(f"\n🔗 CORRELACIONES DE ARISTAS (top 5):")
    if len(crystal.edges) > 0:
        edges_sorted = sorted(crystal.edges, key=lambda e: e.strength, reverse=True)
        for i, edge in enumerate(edges_sorted[:5]):
            correlation = min(1.0, max(-1.0, edge.correlation))
            print(f"   Arista {i}: nodos({edge.node_i},{edge.node_j}), " +
                  f"correlación={correlation:.4f}, fortaleza={edge.strength:.4f}")
    else:
        print("   (Sin aristas)")
    
    print("\n" + "="*60 + "\n")


# =====================================================
# SECCIÓN 6: TRIANGULACIÓN RECURSIVA
# =====================================================

def recursive_triangulation(crystal, max_depth=3, current_depth=0):
    """
    Genera triangulaciones recursivas del cristal.
    
    Cada nivel de profundidad representa un nuevo nivel
    de auto-observación (Meta-conciencia).
    """
    if current_depth >= max_depth:
        return crystal
    
    print(f"\n🔄 Triangulación recursiva - Nivel {current_depth + 1}")
    
    # Para cada ego, generar sub-egos internos
    for ego in crystal.ego_faces:
        # El centroide del ego puede ser un nuevo nodo
        # que genera nuevas relaciones
        
        # Sub-triángulo 1: centroide + 2 vértices
        sub_nodes = [
            ego.centroid,
            ego.nodes_states[0],
            ego.nodes_states[1]
        ]
        
        sub_ego = EgoFace([0, 1, 2], np.array(sub_nodes))
        sub_ego.update_consciousness_level(crystal.global_phi)
    
    current_depth += 1
    return recursive_triangulation(crystal, max_depth, current_depth)


# =====================================================
# FUNCIÓN PRINCIPAL DE INTEGRACIÓN
# =====================================================

def build_crystal_from_simulation(trajectory_3d, threshold_distance=0.2):
    """
    Función principal: construir el cristal a partir de una simulación
    
    Uso:
    ```
    traj = simulate()  # desde RYP_CORE
    crystal = build_crystal_from_simulation(traj)
    visualize_polyhedron_crystal(crystal)
    print_crystal_report(crystal)
    ```
    """
    crystal = PolyhedronCrystal(trajectory_3d, threshold_distance)
    crystal.build_crystal()
    crystal.update_ego_consciousness()
    
    return crystal


# =====================================================
# NIVEL 4: META-CONCIENCIA (AUTO-OBSERVACIÓN RECURSIVA)
# =====================================================

def extract_crystal_trajectory(crystal, selection_method='nodos'):
    """
    Extrae una trayectoria a partir de la estructura del cristal.
    
    El cristal se convierte en "trayectoria" del siguiente nivel,
    permitiendo que el sistema se observe a sí mismo.
    
    Parámetros:
    -----------
    selection_method: str
        - 'nodos': Usa los estados 3D de los nodos (default)
        - 'ego_centers': Centroide de cada cara (ego)
        - 'ego_conscientes': Solo egos con Φ > 0.7
        - 'correlacion': Nodos ponderados por correlación
    
    Returns:
    --------
    trajectory: np.array (N, 3) - Trayectoria para el siguiente nivel
    """
    
    if selection_method == 'nodos':
        # Nodos muestreados de la trayectoria original
        trajectory = np.array([n['state_3d'] for n in crystal.nodes])
    
    elif selection_method == 'ego_centers':
        # Centroide de cada ego (espacio mental)
        trajectory = np.array([
            np.mean(ego.nodes_states, axis=0) 
            for ego in crystal.ego_faces
        ])
    
    elif selection_method == 'ego_conscientes':
        # Solo egos altamente conscientes (Φ > threshold)
        threshold = 0.6
        trajectory = np.array([
            np.mean(ego.nodes_states, axis=0)
            for ego in crystal.ego_faces 
            if ego.consciousness_level > threshold
        ])
        
        # Si hay muy pocos, usar todos
        if len(trajectory) < 5:
            trajectory = np.array([
                np.mean(ego.nodes_states, axis=0) 
                for ego in crystal.ego_faces
            ])
    
    elif selection_method == 'correlacion':
        # Nodos ponderados por su fuerza de conexión
        weights = []
        for i, node in enumerate(crystal.nodes):
            # Conectividad = número de aristas del nodo
            connectivity = len(node['connections'])
            weights.append(connectivity)
        
        weights = np.array(weights) / (np.sum(weights) + 1e-10)
        
        # Muestreo ponderado (nodos más conectados tienen mayor peso)
        trajectory = np.array([n['state_3d'] for n in crystal.nodes])
        
        # Reescalar por importancia
        centroid = np.mean(trajectory, axis=0)
        for i, w in enumerate(weights):
            trajectory[i] = w * trajectory[i] + (1-w) * centroid
    
    else:
        trajectory = np.array([n['state_3d'] for n in crystal.nodes])
    
    # Asegurar que tenemos suficientes puntos
    if len(trajectory) < 4:
        print(f"[Nivel 4] Advertencia: solo {len(trajectory)} puntos, agregando ruido")
        # Agregar puntos por interpolación
        n_needed = max(10, 4 - len(trajectory))
        interpolated = []
        for i in range(len(trajectory) - 1):
            p1, p2 = trajectory[i], trajectory[i+1]
            for t in np.linspace(0, 1, 3)[:-1]:
                interpolated.append((1-t)*p1 + t*p2)
        trajectory = np.vstack([trajectory, np.array(interpolated)])
    
    return trajectory


def build_recursive_crystals(initial_crystal, n_levels=3, threshold_distance=0.35):
    """
    Construye una jerarquía de cristales recursivos.
    
    Cada nivel representa el sistema observándose a sí mismo,
    generando estructuras emergentes de auto-conciencia.
    
    Parameters:
    -----------
    initial_crystal: PolyhedronCrystal
        El cristal base (Nivel 0)
    n_levels: int
        Número de niveles a generar (recomendado: 3-4)
    threshold_distance: float
        Umbral para conectar nodos en cada nivel
    
    Returns:
    --------
    crystals: list[PolyhedronCrystal]
        Lista de cristales, uno por nivel
    """
    crystals = [initial_crystal]
    
    for level in range(1, n_levels):
        print(f"\n🔮 NIVEL {level}: Meta-Conciencia (Auto-Observación)")
        print(f"   Extrayendo estructura del Nivel {level-1}...")
        
        # Extraer trayectoria del nivel anterior
        prev_crystal = crystals[level - 1]
        trajectory_L = extract_crystal_trajectory(prev_crystal, selection_method='nodos')
        
        print(f"   → {len(trajectory_L)} puntos extraídos")
        
        # Construir nuevo cristal
        crystal_L = build_crystal_from_simulation(trajectory_L, threshold_distance)
        crystals.append(crystal_L)
        
        metrics = crystal_L.get_crystal_metrics()
        print(f"   ✓ Cristal Nivel {level} construido:")
        print(f"      • Nodos: {metrics['num_nodes']}")
        print(f"      • Aristas: {metrics['num_edges']}")
        print(f"      • Caras (Egos): {metrics['num_egos']}")
        print(f"      • Φ Global: {metrics['global_phi']:.4f}")
    
    return crystals


def compare_crystal_levels(crystals):
    """
    Compara métricas entre niveles recursivos de conciencia.
    
    Revela cómo la estructura cambia a medida que el sistema
    se observa a sí mismo en cada nivel.
    
    Parameters:
    -----------
    crystals: list[PolyhedronCrystal]
        Lista de cristales (Nivel 0, 1, 2, ...)
    
    Returns:
    --------
    comparison: dict
        Métricas comparativas entre niveles
    """
    comparison = {
        'num_levels': len(crystals),
        'levels': []
    }
    
    print("\n" + "="*70)
    print("  📊 ANÁLISIS JERÁRQUICO DE CONCIENCIA")
    print("="*70)
    
    for level, crystal in enumerate(crystals):
        metrics = crystal.get_crystal_metrics()
        
        level_data = {
            'level': level,
            'num_nodes': metrics['num_nodes'],
            'num_edges': metrics['num_edges'],
            'num_egos': metrics['num_egos'],
            'global_phi': metrics['global_phi'],
            'avg_edge_strength': metrics['avg_edge_strength'],
            'avg_ego_consciousness': metrics['avg_ego_consciousness'],
            'density': 2 * metrics['num_edges'] / (metrics['num_nodes'] * (metrics['num_nodes']-1)) 
                      if metrics['num_nodes'] > 1 else 0
        }
        
        comparison['levels'].append(level_data)
        
        print(f"\n🔹 NIVEL {level}:")
        print(f"   Nodos: {level_data['num_nodes']:3d} | Aristas: {level_data['num_edges']:3d} | Caras: {level_data['num_egos']:3d}")
        print(f"   Φ Global: {level_data['global_phi']:.4f} | Densidad: {level_data['density']:.4f}")
        print(f"   Conciencia ego promedio: {level_data['avg_ego_consciousness']:.4f}")
    
    # Análisis de tendencias
    print("\n" + "="*70)
    print("  📈 TENDENCIAS OBSERVADAS:")
    print("="*70)
    
    if len(crystals) > 1:
        # Cambio en Φ
        phi_cambio = [comparison['levels'][i+1]['global_phi'] - comparison['levels'][i]['global_phi'] 
                     for i in range(len(crystals)-1)]
        phi_direction = "↑ Aumentando" if np.mean(phi_cambio) > 0 else "↓ Disminuyendo"
        print(f"\n Φ Global: {phi_direction} (promedio cambio: {np.mean(phi_cambio):+.4f})")
        
        # Cambio en densidad
        density_cambio = [comparison['levels'][i+1]['density'] - comparison['levels'][i]['density'] 
                         for i in range(len(crystals)-1)]
        density_direction = "↑ Más conexiones" if np.mean(density_cambio) > 0 else "↓ Menos conexiones"
        print(f" Densidad: {density_direction} (promedio cambio: {np.mean(density_cambio):+.4f})")
        
        # Convergencia
        phi_valores = [c['global_phi'] for c in comparison['levels']]
        if len(phi_valores) > 2:
            variancia = np.var(phi_valores[-2:])
            if variancia < 0.01:
                print(f" 🎯 Sistema convergiendo (variancia Φ: {variancia:.6f})")
            else:
                print(f" 🌀 Sistema aún explorando (variancia Φ: {variancia:.6f})")
    
    print("\n" + "="*70 + "\n")
    
    return comparison


def visualize_crystal_hierarchy(crystals, save_path=None):
    """
    Visualiza la jerarquía de cristales en una figura de subplots.
    
    Muestra cómo la estructura cambia entre niveles de conciencia.
    """
    n_levels = len(crystals)
    fig = plt.figure(figsize=(6*n_levels, 5))
    
    for level, crystal in enumerate(crystals):
        ax = fig.add_subplot(1, n_levels, level+1, projection='3d')
        
        # Plotear nodos
        if len(crystal.nodes) > 0:
            nodes_coords = np.array([n['state_3d'] for n in crystal.nodes])
            ax.scatter(nodes_coords[:, 0], nodes_coords[:, 1], nodes_coords[:, 2],
                      c='red', s=50, alpha=0.8, label=f'Nodos (N={len(crystal.nodes)})')
        
        # Plotear aristas
        for edge in crystal.edges:
            p1 = crystal.nodes[edge.node_i]['state_3d']
            p2 = crystal.nodes[edge.node_j]['state_3d']
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                   'b-', alpha=0.2, linewidth=0.5)
        
        # Plotear caras
        if len(crystal.ego_faces) > 0:
            for ego in crystal.ego_faces:
                simplex = np.vstack([ego.nodes_states, ego.nodes_states[0]])
                color_intensity = max(0.0, min(1.0, ego.consciousness_level))
                ax.plot(simplex[:, 0], simplex[:, 1], simplex[:, 2],
                       color=plt.cm.viridis(color_intensity), alpha=0.3, linewidth=0.5)
        
        ax.set_xlabel('S')
        ax.set_ylabel('A')
        ax.set_zlabel('M')
        ax.set_title(f'Nivel {level}\nΦ={crystal.global_phi:.3f}, Caras={len(crystal.ego_faces)}')
        ax.legend(fontsize=8)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"[Visualización] Guardado en: {save_path}")
    
    plt.show()


def print_hierarchy_interpretation(comparison):
    """
    Interpreta la jerarquía de conciencia en términos filosóficos.
    """
    print("\n" + "="*70)
    print("  🧠 INTERPRETACIÓN FILOSÓFICA DE LA JERARQUÍA")
    print("="*70)
    
    levels = comparison['levels']
    
    if len(levels) >= 2:
        L0_phi = levels[0]['global_phi']
        L1_phi = levels[1]['global_phi']
        
        if L1_phi > L0_phi:
            print(f"""
    El Nivel 1 (meta-conciencia) es más autoconsciencia que el Nivel 0.
    
    Esto significa:
    • El sistema observándose a sí mismo es más coherente
    • Emergen estructuras más equilibradas (egos más conscientes)
    • La auto-observación aumenta la integración del sistema
    
    Φ_Nivel0: {L0_phi:.4f} → Φ_Nivel1: {L1_phi:.4f} (↑ {(L1_phi-L0_phi)*100:.1f}%)
            """)
        else:
            print(f"""
    El Nivel 1 es menos autoconsciencia que el Nivel 0.
    
    Esto significa:
    • La auto-observación fragmenta el sistema en egos
    • Emergen múltiples perspectivas (menor integración)
    • El sistema se diversifica al observarse
    
    Φ_Nivel0: {L0_phi:.4f} → Φ_Nivel1: {L1_phi:.4f} (↓ {(L0_phi-L1_phi)*100:.1f}%)
            """)
    
    if len(levels) >= 3:
        L1_phi = levels[1]['global_phi']
        L2_phi = levels[2]['global_phi']
        
        print(f"""
    Evolución de la jerarquía:
    
    Nivel 0 → Nivel 1: El sistema percibe su estructura
    Nivel 1 → Nivel 2: El sistema percibe cómo se percibe a sí mismo
    
    Esto es un reflejo infinito: cada nivel es el espejo del anterior.
    
    Si Φ converge: El sistema alcanza una "verdad" estable sobre sí mismo
    Si Φ oscila: El sistema está en exploración de su propia naturaleza
    """)
    
    print("="*70 + "\n")
