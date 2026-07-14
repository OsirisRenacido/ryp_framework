# Modelo creado por Joaquin Rosales Flores, psicologo.
# =====================================================
# RYP - SISTEMA COMPLETO (VERSIÓN ESTABLE FINAL)
# ARQUITECTURA TIPO SOFTWARE CIENTÍFICO
# Panel superior + módulos separados + ejecución controlada con main()
# =====================================================

import numpy as np
import matplotlib.pyplot as plt
import itertools
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans

from ryp_framework.morphosemantic.operators import (
    build_higher_order_node,
    build_higher_order_trajectory,
    evaluate_projection_stability,
)
from ryp_framework.utils.paths import is_standalone_mode


LEGACY_BRIDGES_ENABLED = not is_standalone_mode()

try:
    if LEGACY_BRIDGES_ENABLED:
        from scripts.fractal_metrics import fractal_profile_from_series
    else:
        fractal_profile_from_series = None
except Exception:  # pragma: no cover - optional experimental bridge
    fractal_profile_from_series = None

try:
    if LEGACY_BRIDGES_ENABLED:
        from RYP_MOTOR_CLOSURE_ARCHITECTURE_2026_05_09 import (
            REENTRY_STAGE as MOTOR_CLOSURE_REENTRY_STAGE,
            build_architecture_contract as build_motor_closure_contract,
            run_recursive_closure as run_motor_recursive_closure,
        )
    else:
        raise ImportError("Legacy bridges disabled in standalone mode")
except Exception:  # pragma: no cover - optional bridge module
    MOTOR_CLOSURE_REENTRY_STAGE = "CPF"
    build_motor_closure_contract = None
    run_motor_recursive_closure = None

try:
    if LEGACY_BRIDGES_ENABLED:
        from RYP_SEMANTIC_THEORY_LAYER_2026_05_09 import (
            SemanticTheoryExtractor,
            SemanticMotorMapper,
            SemanticGuidedSAMPlanner,
        )
        CORE_SEMANTIC_AVAILABLE = True
    else:
        raise ImportError("Legacy semantic bridge disabled in standalone mode")
except Exception:  # pragma: no cover - optional semantic layer
    SemanticTheoryExtractor = None
    SemanticMotorMapper = None
    SemanticGuidedSAMPlanner = None
    CORE_SEMANTIC_AVAILABLE = False

# =====================================================
# 1. PANEL DE CONTROL CENTRAL (INTERFAZ CONSOLA)
# =====================================================

# Modo general de operación
MODE = "explore"  # "manual" o "explore"

# Control de ejecución global
COMPARE_MODE = True
ADVANCED_ANALYSIS = True
BUILD_CRYSTAL = True
PRINT_CONFIG = True
AUTO_RUN_ALL = False

LAST_MOTOR_CLOSURE_STATE = None
LAST_MOTOR_CLOSURE_CONTRACT = None

# =====================================================
# 🔬 EXPERIMENTAL SUITE - RYP SCIENTIFIC MODE
# =====================================================

# -----------------------------
# ROBUSTEZ ESTADÍSTICA
# -----------------------------
N_RUNS = 50
ENABLE_MULTI_RUN = True
USE_FIXED_SEEDS = True

SEEDS = list(range(50, 50 + N_RUNS))

# -----------------------------
# ABLATION STUDY MATRIX
# -----------------------------

ABLATION_RUNS = True

ABLATE_OMEGA = True
ABLATE_COUPLING = True
ABLATE_ROTATION = True
ABLATE_COLLAPSE = True
ABLATE_PERMUTATION = True

# -----------------------------
# MÉTRICAS EXPERIMENTALES
# -----------------------------

COMPUTE_CLUSTER_STABILITY = True
COMPUTE_ATTRACTOR_CONSISTENCY = True
COMPUTE_TRAJECTORY_DIVERGENCE = True
COMPUTE_FINAL_STATE_VARIANCE = True

# -----------------------------
# DINÁMICA TEMPORAL
# -----------------------------

TRACK_TIME_SERIES = True
TRACK_STATE_ENTROPY = True
TRACK_STATE_TRANSITIONS = True

# -----------------------------
# EXPORTACIÓN CIENTÍFICA
# -----------------------------

SAVE_RAW_DATA = True
SAVE_CLUSTER_DATA = True
SAVE_METRICS = True
EXPORT_FORMAT = "json"
EXPORT_PATH = "./RYP_EXPERIMENTS/"


# =====================================================
# 🔬 PAPER EXPERIMENT MODE (PUBLICATION PIPELINE)
# =====================================================

EXPERIMENT_NAME = "RYP_SAM_PUBLICATION_RUN_01"

SEED = 42
np.random.seed(SEED)

# =========================
# CONTROL DE REPRODUCIBILIDAD
# =========================

RUN_BASELINE = True
RUN_FULL_MODEL = True
RUN_ABLATION_OMEGA = True
RUN_ABLATION_COUPLING = True
RUN_ABLATION_ROTATION = True
RUN_ABLATION_COLLAPSE = True

# =========================
# EXPERIMENTOS ESTADÍSTICOS
# =========================

N_REPEATS = 30  # Monte Carlo runs

COLLECT_FINAL_STATES = True
COLLECT_TRAJECTORIES = True
COLLECT_DIFF_METRICS = True

# =========================
# MÉTRICAS PUBLICABLES
# =========================

COMPUTE_ATRACTORS = True
COMPUTE_VARIANCE_STABILITY = True
COMPUTE_CLUSTER_SEPARATION = True
COMPUTE_ENTROPY_APPROX = True

# =========================
# TEST DE ROBUSTEZ
# =========================

NOISE_LEVEL = 0.01
ENABLE_NOISE = True

# =========================
# EXPORTACIÓN (FUTURO PAPER)
# =========================

EXPORT_RESULTS = True
EXPORT_FORMAT = "npz"
EXPORT_PATH = "./RYP_RESULTS/"

# =====================================================
# 2. CONFIGURACIÓN GENERAL
# =====================================================

SYSTEM_ORDER = 2
steps = 120

ORDER4_RECURSIVE_WINDOW = 12
ORDER4_FEEDBACK_STRENGTH = 0.18
ORDER4_STARTUP_BLEND = 0.12
LAST_ORDER4_RECURSIVE_READING = None
LAST_ORDER4_RECURSIVE_METRICS = None
ORDER3_MIN_READING_LENGTH = 4

x0 = np.array([0.25, 0.5, 0.25])
x1 = np.array([0.4, 0.3, 0.3])

# =====================================================
# 3. PARÁMETROS BASE
# =====================================================

alpha0 = 0.15
phi0   = 0.8
theta0 = 0.35

# =====================================================
# 4. CONTROL DEL MODELO
# =====================================================

USE_OMEGA = True
USE_COUPLING = True

kA, kS, kM = 0.2, 0.5, 0.8
lambda_ = 0.1

# =====================================================
# 5. MODOS
# =====================================================

ROTATION_MODE = "3D"
COLLAPSE_MODE = "A"

USE_PERMUTATION = True
USE_CONJUGATION = True

# =====================================================
# 5b. CONJUGATION NAVIGATOR (FASE 1 INTEGRATION)
# =====================================================

# Optional navigator for M-conjugation constraints (backward compatible)
CONJUGATION_NAVIGATOR = None
RESPECT_CONJUGATION_CONSTRAINTS = False

# =====================================================
# 6. PERMUTACIONES
# =====================================================

PERMUTATION_OPTIONS = [
    "identity","swap_SM","swap_SA","swap_AM",
    "cycle_forward","cycle_backward"
]

ROTATION_OPTIONS = ["SA","AS","SM","MS","AM","MA","3D"]
COLLAPSE_OPTIONS = ["global","S","A","M","competitive"]

# =====================================================
# 7. INTERVENCIÓN
# =====================================================

USE_BASE_PERMUTATION = True
BASE_PERMUTATION_MODE = "swap_SM"
EXPLORE_BASE_PERMUTATIONS = True

USE_INTERVENTION = True
INTERVENTION_STEP = 60

INTERVENTION_TYPE = "permutation_change"
CURRENT_TRAJECTORY_HISTORY = []
LAST_INTERVENTION_RECOMMENDATION = None

USE_DYNAMIC_PERMUTATION = True
INTERVENTION_PERMUTATION_MODE = "cycle_forward"
EXPLORE_DYNAMIC_PERMUTATIONS = True

# =====================================================
# 7.1 CONTROL ESTRICTO DE EXPLORE
# =====================================================

# Por defecto, explore debe medir el sistema sin intervenciones exógenas.
EXPLORE_ALLOW_INTERVENTION = False

# =====================================================
# 8. MATRICES Y OPERADORES BÁSICOS
# =====================================================

def get_permutation_matrix(mode):

    if mode == "identity": return np.eye(3)

    if mode == "swap_SM":
        return np.array([[0,0,1],[0,1,0],[1,0,0]])

    if mode == "swap_SA":
        return np.array([[0,1,0],[1,0,0],[0,0,1]])

    if mode == "swap_AM":
        return np.array([[1,0,0],[0,0,1],[0,1,0]])

    if mode == "cycle_forward":
        return np.array([[0,1,0],[0,0,1],[1,0,0]])

    if mode == "cycle_backward":
        return np.array([[0,0,1],[1,0,0],[0,1,0]])

# =====================================================
# 9. BASE
# =====================================================

def initialize_base_permutation():

    global BASE_PERMUTATION_MODE, P_matrix, P_inv

    if USE_BASE_PERMUTATION:

        if EXPLORE_BASE_PERMUTATIONS:
            BASE_PERMUTATION_MODE = np.random.choice(PERMUTATION_OPTIONS)

        P_matrix = get_permutation_matrix(BASE_PERMUTATION_MODE)

    else:
        P_matrix = np.eye(3)

    P_inv = np.linalg.inv(P_matrix)


# =====================================================
# 10. OPERADORES
# =====================================================

def normalize(x):

    # -----------------------------
    # 1. eliminar valores negativos
    # -----------------------------
    x = np.maximum(x, 0)

    # -----------------------------
    # 2. normalizar
    # -----------------------------
    s = np.sum(x)

    if s == 0:
        return np.array([1/3,1/3,1/3])

    return x / s


def T(x,t):
    return x * (1 + 0.1*np.sin(t))


def S_alpha(x,a):
    return (1-a)*x + a*np.array([1/3,1/3,1/3])

# =====================================================
# 11. ROTACIÓN
# =====================================================

def R(x, phi, mode):

    def rot(a, plane):

        if plane=="SA":
            return np.array([
                [np.cos(a), -np.sin(a), 0],
                [np.sin(a),  np.cos(a), 0],
                [0, 0, 1]
            ])

        if plane=="SM":
            return np.array([
                [np.cos(a), 0, -np.sin(a)],
                [0, 1, 0],
                [np.sin(a), 0, np.cos(a)]
            ])

        if plane=="AM":
            return np.array([
                [1, 0, 0],
                [0, np.cos(a), -np.sin(a)],
                [0, np.sin(a),  np.cos(a)]
            ])

    if mode=="SA": return rot(phi,"SA") @ x
    if mode=="AS": return rot(-phi,"SA") @ x
    if mode=="SM": return rot(phi,"SM") @ x
    if mode=="MS": return rot(-phi,"SM") @ x
    if mode=="AM": return rot(phi,"AM") @ x
    if mode=="MA": return rot(-phi,"AM") @ x

    if mode=="3D":
        return rot(phi,"SA") @ rot(phi,"SM") @ rot(phi,"AM") @ x

    return x

# =====================================================
# 12. COLAPSO
# =====================================================

def collapse(x,theta):

    if COLLAPSE_MODE == "global":
        return np.where(x >= theta, x, 0)

    if COLLAPSE_MODE == "S":
        return np.array([x[0] if x[0]>=theta else 0, x[1], x[2]])

    if COLLAPSE_MODE == "A":
        return np.array([x[0], x[1] if x[1]>=theta else 0, x[2]])

    if COLLAPSE_MODE == "M":
        return np.array([x[0], x[1], x[2] if x[2]>=theta else 0])

    if COLLAPSE_MODE == "competitive":
        i = np.argmax(x)
        y = np.zeros_like(x)
        if x[i] >= theta:
            y[i] = x[i]
        return y

    return x

# =====================================================
# 13. Ω
# =====================================================

def Omega(x,t):

    S,A,M = x

    alpha = alpha0 + kA*(A-1/3)
    phi   = phi0   + kS*(S-1/3)
    theta = theta0 + kM*(M-1/3)

    return alpha, phi, theta

# =====================================================
# 14. INTERVENCIÓN
# =====================================================

def apply_intervention(t, current_state=None):

    global alpha0, phi0, theta0, P_matrix, P_inv
    global ROTATION_MODE, USE_CONJUGATION, USE_PERMUTATION
    global LAST_INTERVENTION_RECOMMENDATION

    if not USE_INTERVENTION:
        return

    if t == INTERVENTION_STEP:

        if INTERVENTION_TYPE == "integration_boost":
            alpha0 *= 1.5

        elif INTERVENTION_TYPE == "flexibility_boost":
            phi0 *= 1.5

        elif INTERVENTION_TYPE == "stabilization":
            theta0 *= 0.7

        elif INTERVENTION_TYPE == "destabilization":
            theta0 *= 1.3

        elif INTERVENTION_TYPE == "permutation_change":

            if USE_DYNAMIC_PERMUTATION:

                if EXPLORE_DYNAMIC_PERMUTATIONS:
                    new_mode = np.random.choice(PERMUTATION_OPTIONS)
                else:
                    new_mode = INTERVENTION_PERMUTATION_MODE

                P_matrix = get_permutation_matrix(new_mode)
                P_inv = np.linalg.inv(P_matrix)

        elif INTERVENTION_TYPE == "a_axis_auto_stabilization":
            trajectory_seed = [np.array(state, dtype=float) for state in CURRENT_TRAJECTORY_HISTORY]
            if current_state is not None:
                trajectory_seed.append(np.array(current_state, dtype=float))

            higher_order_reading = None
            if len(trajectory_seed) >= 4:
                higher_order_reading = read_higher_order_elements_from_core(
                    np.array(trajectory_seed, dtype=float),
                    max_order=4,
                )

            state_for_decision = current_state if current_state is not None else (trajectory_seed[-1] if trajectory_seed else np.array([1/3, 1/3, 1/3], dtype=float))
            recommendation = recommend_a_axis_stabilization(state_for_decision, higher_order_reading=higher_order_reading)
            LAST_INTERVENTION_RECOMMENDATION = recommendation

            USE_CONJUGATION = bool(recommendation["use_conjugation"])
            USE_PERMUTATION = True
            ROTATION_MODE = recommendation["rotation_mode"]

            permutation_mode = recommendation["permutation_mode"]
            P_matrix = get_permutation_matrix(permutation_mode)
            P_inv = np.linalg.inv(P_matrix)


def recommend_a_axis_stabilization(state, higher_order_reading=None):
    vector = normalize(np.array(state, dtype=float))
    s_value, a_value, m_value = [float(value) for value in vector]
    spread = float(a_value - max(s_value, m_value))
    lateral_balance = float(1.0 - abs(s_value - m_value))

    crystal_regime = None
    crystal_autopoiesis = 0.0
    if higher_order_reading is not None:
        crystal_payload = higher_order_reading.get("higher_order_sam_313_crystal") or {}
        crystal_metrics_payload = crystal_payload.get("metrics") or {}
        crystal_regime = crystal_metrics_payload.get("crystal_autopoiesis_regime")
        crystal_autopoiesis = float(crystal_metrics_payload.get("crystal_autopoiesis_index", 0.0))

    if a_value < 0.45:
        return {
            "overloaded": False,
            "priority": "none",
            "rotation_mode": ROTATION_MODE,
            "permutation_mode": BASE_PERMUTATION_MODE,
            "use_conjugation": USE_CONJUGATION,
            "reason": "A no domina lo suficiente como para requerir correccion.",
        }

    if spread >= 0.22 and lateral_balance < 0.92:
        return {
            "overloaded": True,
            "priority": "directed_rotation",
            "rotation_mode": "SA" if s_value <= m_value else "AM",
            "permutation_mode": BASE_PERMUTATION_MODE,
            "use_conjugation": True,
            "reason": "A domina pero S y M siguen diferenciables; conviene redistribuir tensiones con una rotacion dirigida y conservar estructura mediante conjugacion.",
        }

    if spread >= 0.22 and lateral_balance >= 0.92:
        return {
            "overloaded": True,
            "priority": "conjugation",
            "rotation_mode": ROTATION_MODE,
            "permutation_mode": BASE_PERMUTATION_MODE,
            "use_conjugation": True,
            "reason": "A domina y S/M ya estan casi colapsados entre si; conviene estabilizar con conjugacion antes de relabelar ejes.",
        }

    if crystal_regime == "weak" or crystal_autopoiesis < 0.45:
        return {
            "overloaded": True,
            "priority": "permutation",
            "rotation_mode": ROTATION_MODE,
            "permutation_mode": "swap_SA" if s_value >= m_value else "swap_AM",
            "use_conjugation": False,
            "reason": "La organizacion estructural es debil; una permutacion explicita puede ayudar cuando el problema parece ser de asignacion de eje y no solo de exceso mediador.",
        }

    return {
        "overloaded": True,
        "priority": "directed_rotation",
        "rotation_mode": "3D",
        "permutation_mode": BASE_PERMUTATION_MODE,
        "use_conjugation": True,
        "reason": "A tiene peso alto, pero el cristal conserva coherencia; conviene una correccion suave por rotacion/conjugacion y dejar la permutacion como ultimo recurso.",
    }

# =====================================================
# 14b. CONTROL DE NAVEGADOR DE CONJUGACIÓN (FASE 1)
# =====================================================

def set_conjugation_navigator(navigator, respect_constraints=True):
    """
    Activa el navegador de conjugación M para restricciones en transiciones.
    
    Args:
        navigator: Instancia de RYPConjugacionNavigator o None
        respect_constraints: Si True, F() aplicará restricciones de Grado
    
    Uso:
        from RYP_CONJUGACION_NAVIGATOR import RYPConjugacionNavigator
        nav = RYPConjugacionNavigator(respect_conjugation=True)
        set_conjugation_navigator(nav)
        # Ahora simulate() respetará restricciones
    """
    global CONJUGATION_NAVIGATOR, RESPECT_CONJUGATION_CONSTRAINTS
    CONJUGATION_NAVIGATOR = navigator
    RESPECT_CONJUGATION_CONSTRAINTS = respect_constraints if navigator is not None else False
    print(f"[RYP_CORE] Conjugation navigator: {navigator is not None}")
    print(f"[RYP_CORE] Respect constraints: {RESPECT_CONJUGATION_CONSTRAINTS}")

def reset_conjugation_navigator():
    """Desactiva el navegador de conjugación (modo libre)."""
    global CONJUGATION_NAVIGATOR, RESPECT_CONJUGATION_CONSTRAINTS
    CONJUGATION_NAVIGATOR = None
    RESPECT_CONJUGATION_CONSTRAINTS = False
    print("[RYP_CORE] Conjugation navigator reset to free mode")

# =====================================================
# 15. FUNCIÓN CENTRAL
# =====================================================

def F(x, I, t):

    apply_intervention(t, current_state=x)

    if USE_CONJUGATION:
        x = P_matrix @ x
    elif USE_PERMUTATION:
        x = P_matrix @ x

    if USE_COUPLING:
        x = x + lambda_ * I

    if USE_OMEGA:
        alpha, phi, theta = Omega(x, t)
    else:
        alpha, phi, theta = alpha0, phi0, theta0

    x = T(x, t)
    x = R(x, phi, ROTATION_MODE)
    x = S_alpha(x, alpha)
    x = collapse(x, theta)
    x = normalize(x)

    if USE_CONJUGATION:
        x = P_inv @ x

    # ── INTEGRACIÓN FASE 1: Restricciones de Conjugación M ──────────────
    # Si RESPECT_CONJUGATION_CONSTRAINTS está activo, aplica soft-constraints
    # para preservar coherencia ontológica de Grados
    if RESPECT_CONJUGATION_CONSTRAINTS and CONJUGATION_NAVIGATOR is not None:
        try:
            from RYP_CONJUGACION_NAVIGATOR import integrate_with_ryp_core_f
            # Nota: Esta integración usa el estado anterior (pre-F)
            # Para una integración más sofisticada, llamar integrate_with_ryp_core_f
            # desde simulate() después de cada paso
            pass  # Placeholder: integración se realiza en simulate()
        except ImportError:
            pass  # Navigator no disponible, continuar en modo libre

    return x


# =====================================================
# 16. SIMULACIÓN (VERSIÓN CON PARÁMETROS OPCIONALES)
# =====================================================

def simulate(initial_state=None, steps_override=None):
    """
    Simulación flexible que mantiene el modelo matemático.
    - Sin argumentos: usa x0 y steps globales (para experimentos)
    - Con argumentos: usa valores pasados (para texto)
    """
    
    global x0, steps, CURRENT_TRAJECTORY_HISTORY, LAST_INTERVENTION_RECOMMENDATION
    global LAST_ORDER4_RECURSIVE_READING, LAST_ORDER4_RECURSIVE_METRICS

    # Ensure permutation operators exist when the core is imported and used directly
    # from app workflows that do not pass through the experiment entrypoints.
    if "P_matrix" not in globals() or "P_inv" not in globals():
        initialize_base_permutation()
    
    # Usar parámetros globales si no se pasan argumentos
    state = initial_state if initial_state is not None else x0
    num_steps = steps_override if steps_override is not None else steps
    CURRENT_TRAJECTORY_HISTORY = []
    LAST_INTERVENTION_RECOMMENDATION = None
    LAST_ORDER4_RECURSIVE_READING = None
    LAST_ORDER4_RECURSIVE_METRICS = None

    traj = []

    if SYSTEM_ORDER == 1:
        x = state.copy()
        for t in range(num_steps):
            x_prev = x.copy()
            x = F(x, np.zeros(3), t)
            # ── INTEGRACIÓN FASE 1: Aplicar restricciones de Conjugación ──
            if RESPECT_CONJUGATION_CONSTRAINTS and CONJUGATION_NAVIGATOR is not None:
                try:
                    from RYP_CONJUGACION_NAVIGATOR import integrate_with_ryp_core_f
                    x, intervened = integrate_with_ryp_core_f(
                        CONJUGATION_NAVIGATOR, x_prev, x, t
                    )
                    if intervened:
                        # Log intervención (opcional)
                        pass
                except ImportError:
                    pass  # Navigator no disponible
            traj.append(x.copy())
            CURRENT_TRAJECTORY_HISTORY.append(x.copy())
    elif SYSTEM_ORDER == 4:
        x = state.copy()
        recursive_feedback = normalize((1.0 - ORDER4_STARTUP_BLEND) * state + ORDER4_STARTUP_BLEND * x1)
        for t in range(num_steps):
            x_prev = x.copy()
            x = F(x, recursive_feedback, t)
            # ── INTEGRACIÓN FASE 1: Aplicar restricciones de Conjugación ──
            if RESPECT_CONJUGATION_CONSTRAINTS and CONJUGATION_NAVIGATOR is not None:
                try:
                    from RYP_CONJUGACION_NAVIGATOR import integrate_with_ryp_core_f
                    x, intervened = integrate_with_ryp_core_f(
                        CONJUGATION_NAVIGATOR, x_prev, x, t
                    )
                except ImportError:
                    pass  # Navigator no disponible
            traj.append(x.copy())
            CURRENT_TRAJECTORY_HISTORY.append(x.copy())

            if len(CURRENT_TRAJECTORY_HISTORY) >= max(4, ORDER4_RECURSIVE_WINDOW // 2):
                window = np.array(CURRENT_TRAJECTORY_HISTORY[-ORDER4_RECURSIVE_WINDOW:], dtype=float)
                recursive_reading = read_higher_order_elements_from_core(window, max_order=4)
                recursive_feedback = derive_order4_recursive_feedback(recursive_reading, base_state=state)
                LAST_ORDER4_RECURSIVE_READING = recursive_reading
                LAST_ORDER4_RECURSIVE_METRICS = compute_order4_recursive_metrics(recursive_reading)
    else:
        xA = state.copy()
        xB = x1.copy()
        for t in range(num_steps):
            xA = F(xA, xB, t)
            xB = F(xB, xA, t)
            traj.append(xA.copy())
            CURRENT_TRAJECTORY_HISTORY.append(xA.copy())

    return np.array(traj)

# ...existing code...

# =====================================================
# 17. MÉTRICA
# =====================================================

def cosine_similarity(left, right):
    left_values = np.array(left, dtype=float)
    right_values = np.array(right, dtype=float)
    denominator = float(np.linalg.norm(left_values) * np.linalg.norm(right_values))
    if denominator <= 0.0:
        return 0.0
    return float(np.dot(left_values, right_values) / denominator)


def compute_fractal_profile(traj):
    if fractal_profile_from_series is None or traj is None:
        return {
            "active": False,
            "series_length": 0,
            "signal_profile": None,
            "step_profile": None,
            "reliable": False,
            "note": "fractal_module_unavailable_or_empty",
        }

    arr = np.array(traj, dtype=float)
    if arr.ndim != 2 or arr.shape[0] < 4:
        return {
            "active": False,
            "series_length": int(arr.shape[0]) if arr.ndim > 0 else 0,
            "signal_profile": None,
            "step_profile": None,
            "reliable": False,
            "note": "insufficient_length",
        }

    scalar_series = 0.4 * arr[:, 0] + 0.3 * arr[:, 1] + 0.3 * arr[:, 2]
    step_series = np.linalg.norm(np.diff(arr, axis=0), axis=1)

    signal_profile = fractal_profile_from_series(scalar_series)
    step_profile = fractal_profile_from_series(step_series)

    return {
        "active": True,
        "series_length": int(arr.shape[0]),
        "signal_profile": signal_profile,
        "step_profile": step_profile,
        "reliable": bool(
            signal_profile["hurst"]["reliable"]
            and signal_profile["dfa_alpha"]["reliable"]
            and step_profile["hurst"]["reliable"]
        ),
        "note": "scalar_sam_signal_and_step_magnitude",
    }


def autopoiesis_metrics(traj):
    if traj is None or len(traj) < 2:
        return {
            "reentry_similarity": 0.0,
            "continuity_index": 0.0,
            "boundary_coherence_index": 0.0,
            "closure_index": 0.0,
            "conservation_change_index": 0.0,
            "endpoint_drift": 0.0,
            "autopoiesis_index": 0.0,
            "fractal_profile": compute_fractal_profile(traj),
            "regime": "insufficient",
        }

    start_state = np.array(traj[0], dtype=float)
    end_state = np.array(traj[-1], dtype=float)
    tail = np.array(traj[-20:] if len(traj) >= 20 else traj, dtype=float)

    reentry_similarity = cosine_similarity(start_state, end_state)

    consecutive_cosines = [
        cosine_similarity(traj[index], traj[index + 1])
        for index in range(len(traj) - 1)
    ]
    continuity_index = float(np.mean(consecutive_cosines)) if consecutive_cosines else 0.0

    tail_variance = float(np.var(tail))
    boundary_coherence_index = float(max(0.0, min(1.0, 1.0 - (tail_variance / 0.08))))

    tail_centroid = np.mean(tail, axis=0)
    tail_alignment = cosine_similarity(end_state, tail_centroid)
    closure_index = float(max(0.0, min(1.0, 0.5 * tail_alignment + 0.5 * boundary_coherence_index)))

    endpoint_drift = float(np.linalg.norm(end_state - start_state))
    change_factor = float(min(1.0, endpoint_drift / 0.18))
    conservation_change_index = float(reentry_similarity * change_factor)

    autopoiesis_index = float(max(
        0.0,
        min(
            1.0,
            0.35 * reentry_similarity
            + 0.20 * continuity_index
            + 0.20 * boundary_coherence_index
            + 0.15 * closure_index
            + 0.10 * conservation_change_index,
        ),
    ))

    if autopoiesis_index >= 0.68:
        regime = "robust"
    elif autopoiesis_index >= 0.45:
        regime = "incipient"
    else:
        regime = "weak"

    fractal_profile = compute_fractal_profile(traj)

    return {
        "reentry_similarity": float(round(reentry_similarity, 6)),
        "continuity_index": float(round(continuity_index, 6)),
        "boundary_coherence_index": float(round(boundary_coherence_index, 6)),
        "closure_index": float(round(closure_index, 6)),
        "conservation_change_index": float(round(conservation_change_index, 6)),
        "endpoint_drift": float(round(endpoint_drift, 6)),
        "autopoiesis_index": float(round(autopoiesis_index, 6)),
        "fractal_profile": fractal_profile,
        "regime": regime,
    }


def build_core_local_projections(traj, segments=4):
    if traj is None or len(traj) == 0:
        return []

    window_count = max(3, int(segments))
    local_projections = []
    for index, window in enumerate(np.array_split(np.array(traj, dtype=float), window_count)):
        if len(window) == 0:
            continue
        vector = normalize(np.mean(window, axis=0))
        dominant_axis = ["S", "A", "M"][int(np.argmax(vector))]
        local_projections.append({
            "label": f"core_segment_{index + 1}",
            "sam": vector,
            "dominant_axis": dominant_axis,
            "root_term": f"core_segment_{index + 1}",
            "operator_names": [],
        })
    return local_projections


def integrate_subjectivity_in_A(projection_window, reference_node, autopoiesis, crystal):
    if not projection_window:
        return []

    reference_vector = normalize(reference_node["vector"]) if reference_node is not None else np.array([0.2, 0.6, 0.2], dtype=float)
    a_anchor = np.array([0.2, 0.6, 0.2], dtype=float)
    integration_strength = max(
        0.10,
        min(
            0.35,
            0.08
            + 0.12 * float(autopoiesis.get("autopoiesis_index", 0.0))
            + 0.10 * float(crystal.get("crystal_autopoiesis_index", 0.0)),
        ),
    )

    integrated = []
    for item in projection_window:
        base_vector = normalize(item["sam"])
        mediated_vector = normalize(
            (1.0 - integration_strength) * base_vector
            + 0.55 * integration_strength * reference_vector
            + 0.45 * integration_strength * a_anchor
        )
        integrated.append({
            **item,
            "sam": mediated_vector,
            "dominant_axis": ["S", "A", "M"][int(np.argmax(mediated_vector))],
        })

    return integrated


def select_reference_higher_order_node(higher_order_nodes):
    if not higher_order_nodes:
        return None

    centroid = normalize(np.mean([node["vector"] for node in higher_order_nodes], axis=0))
    scored = []
    for node in higher_order_nodes:
        alignment = cosine_similarity(node["vector"], centroid)
        score = 0.55 * float(node.get("stability_index", 0.0)) + 0.45 * alignment
        scored.append((score, node))
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1]


def assign_axis_anchors_around_reference(higher_order_nodes, reference_node):
    if reference_node is None:
        return {}

    remaining = [node for node in higher_order_nodes if node is not reference_node]
    axes = ("S", "A", "M")

    if len(remaining) < 3:
        anchors = {}
        for axis in axes:
            candidates = sorted(higher_order_nodes, key=lambda node: float(node["vector"]["SAM".index(axis)]), reverse=True)
            anchors[axis] = candidates[0]
        return anchors

    best_score = None
    best_assignment = None
    for permutation in itertools.permutations(remaining, 3):
        score = sum(float(permutation[index]["vector"][index]) for index in range(3))
        if best_score is None or score > best_score:
            best_score = score
            best_assignment = {axis: permutation[index] for index, axis in enumerate(axes)}

    return best_assignment or {}


def build_sam_313_from_higher_order_nodes(higher_order_nodes):
    if not higher_order_nodes:
        return {
            "reference_node": None,
            "axis_anchors": {},
            "sam_313_vector": None,
            "scaffold_nodes": [],
            "scaffold_trajectory": np.zeros((0, 3), dtype=float),
        }

    reference_node = select_reference_higher_order_node(higher_order_nodes)
    axis_anchors = assign_axis_anchors_around_reference(higher_order_nodes, reference_node)
    center_vector = normalize(reference_node["vector"])

    scaffold_nodes = []
    sam_components = []
    for axis in ("S", "A", "M"):
        anchor = axis_anchors.get(axis, reference_node)
        anchor_vector = normalize(anchor["vector"])
        mirrored_vector = normalize(np.maximum(0.0, 2.0 * center_vector - anchor_vector))
        scaffold_nodes.append({
            "label": f"left_{axis.lower()}",
            "role": f"left_{axis}",
            "axis": axis,
            "source_name": anchor["name"],
            "vector": anchor_vector,
        })
        sam_components.append(float(anchor_vector["SAM".index(axis)]))
        scaffold_nodes.append({
            "label": f"right_{axis.lower()}",
            "role": f"right_{axis}",
            "axis": axis,
            "source_name": anchor["name"],
            "vector": mirrored_vector,
        })

    scaffold_nodes.insert(3, {
        "label": "center",
        "role": "center_reference",
        "axis": reference_node["order_axis"],
        "source_name": reference_node["name"],
        "vector": center_vector,
    })

    sam_313_vector = normalize(np.array(sam_components, dtype=float))
    scaffold_trajectory = np.array([node["vector"] for node in scaffold_nodes], dtype=float)

    return {
        "reference_node": reference_node,
        "axis_anchors": axis_anchors,
        "sam_313_vector": sam_313_vector,
        "scaffold_nodes": scaffold_nodes,
        "scaffold_trajectory": scaffold_trajectory,
    }


def stabilize_sam_313_branches_in_A(scaffold_nodes, traj_metrics=None):
    if not scaffold_nodes:
        return []

    role_map = {node["role"]: node for node in scaffold_nodes}
    center_vector = normalize(role_map.get("center_reference", scaffold_nodes[len(scaffold_nodes) // 2])["vector"])

    a_vectors = []
    for role in ("left_A", "right_A"):
        if role in role_map:
            a_vectors.append(normalize(role_map[role]["vector"]))
    a_band_vector = normalize(np.mean(a_vectors, axis=0)) if a_vectors else np.array([0.2, 0.6, 0.2], dtype=float)

    autopoiesis_index = 0.0 if traj_metrics is None else float(traj_metrics.get("autopoiesis_index", 0.0))
    branch_strength = max(0.10, min(0.26, 0.10 + 0.18 * autopoiesis_index))
    axial_strength = max(0.06, min(0.16, 0.05 + 0.10 * autopoiesis_index))

    stabilized_nodes = []
    for node in scaffold_nodes:
        base_vector = normalize(node["vector"])
        if node["role"] == "center_reference":
            stabilized_vector = normalize((1.0 - axial_strength) * base_vector + axial_strength * a_band_vector)
        elif node["axis"] == "A":
            stabilized_vector = normalize((1.0 - axial_strength) * base_vector + axial_strength * center_vector)
        else:
            a_target = normalize(0.55 * center_vector + 0.45 * a_band_vector)
            stabilized_vector = normalize((1.0 - branch_strength) * base_vector + branch_strength * a_target)

        stabilized_nodes.append({
            **node,
            "vector": stabilized_vector,
        })

    return stabilized_nodes


def build_explicit_sam_313_crystal(scaffold_nodes, traj_metrics=None):
    if not scaffold_nodes:
        return {
            "nodes": [],
            "edge_count": 0,
            "connections": {},
            "metrics": crystal_metrics([], traj_metrics=traj_metrics, print_metrics=False),
        }

    stabilized_scaffold_nodes = stabilize_sam_313_branches_in_A(scaffold_nodes, traj_metrics=traj_metrics)

    crystal_nodes = []
    for index, scaffold_node in enumerate(stabilized_scaffold_nodes):
        node = SAMNode(normalize(scaffold_node["vector"]), index)
        node.role = scaffold_node["role"]
        node.axis = scaffold_node["axis"]
        node.source_name = scaffold_node["source_name"]
        crystal_nodes.append(node)

    role_index = {node.role: index for index, node in enumerate(crystal_nodes)}
    edge_pairs = [
        ("center_reference", "left_S"),
        ("center_reference", "right_S"),
        ("center_reference", "left_A"),
        ("center_reference", "right_A"),
        ("center_reference", "left_M"),
        ("center_reference", "right_M"),
        ("left_S", "right_S"),
        ("left_A", "right_A"),
        ("left_M", "right_M"),
        ("left_S", "left_A"),
        ("left_A", "left_M"),
        ("right_S", "right_A"),
        ("right_A", "right_M"),
    ]

    added_edges = set()
    for left_role, right_role in edge_pairs:
        if left_role not in role_index or right_role not in role_index:
            continue
        left_index = role_index[left_role]
        right_index = role_index[right_role]
        edge_key = tuple(sorted((left_index, right_index)))
        if edge_key in added_edges:
            continue
        crystal_nodes[left_index].connections.append(right_index)
        crystal_nodes[right_index].connections.append(left_index)
        added_edges.add(edge_key)

    metrics = crystal_metrics(crystal_nodes, traj_metrics=traj_metrics, print_metrics=False)
    connection_map = {
        node.role: [crystal_nodes[index].role for index in node.connections]
        for node in crystal_nodes
    }

    return {
        "nodes": crystal_nodes,
        "edge_count": len(added_edges),
        "connections": connection_map,
        "stabilized_scaffold_nodes": stabilized_scaffold_nodes,
        "metrics": metrics,
    }


def read_higher_order_elements_from_core(
    traj,
    max_order=3,
    relation_mode="general",
    family_scheme="relational",
):
    if traj is None or len(traj) == 0 or max_order <= 0:
        return {
            "higher_order_nodes": [],
            "higher_order_trajectory": np.zeros((0, 3), dtype=float),
            "source_autopoiesis": None,
            "source_crystal": None,
        }

    autopoiesis = autopoiesis_metrics(traj)
    nodes = build_nodes(traj)
    connect_nodes(nodes)
    crystal = crystal_metrics(nodes, traj_metrics=autopoiesis, print_metrics=False)
    local_projections = build_core_local_projections(traj, segments=max(4, min(6, max_order + 2)))

    higher_order_nodes = []
    for order in range(1, max_order + 1):
        shift = (order - 1) % len(local_projections)
        ordered = local_projections[shift:] + local_projections[:shift]
        projection_window = ordered[:max(3, min(len(ordered), order + 2))]
        integrated_window = integrate_subjectivity_in_A(
            projection_window,
            reference_node=select_reference_higher_order_node(higher_order_nodes) if higher_order_nodes else None,
            autopoiesis=autopoiesis,
            crystal=crystal,
        )

        projection = evaluate_projection_stability(
            integrated_window,
            relation_density=max(0.35, min(0.95, 0.45 + 0.35 * crystal["edge_density"])),
            attention_load=max(0.18, min(0.82, 0.48 - 0.22 * autopoiesis["autopoiesis_index"] + 0.03 * (order - 1))),
            coherence_bias=max(0.45, min(0.98, 0.48 + 0.42 * crystal["global_phi"])),
        )
        higher_node = build_higher_order_node(
            {"global_projection": projection},
            order=order,
            label=f"core_order_{order}",
            relation_mode=relation_mode,
            family_scheme=family_scheme,
        )
        higher_node["source"] = "core_crystal_autopoiesis"
        higher_node["source_autopoiesis_index"] = autopoiesis["autopoiesis_index"]
        higher_node["source_crystal_autopoiesis_index"] = crystal["crystal_autopoiesis_index"]
        higher_order_nodes.append(higher_node)

    sam_313 = build_sam_313_from_higher_order_nodes(higher_order_nodes)
    sam_313_crystal = build_explicit_sam_313_crystal(sam_313["scaffold_nodes"], traj_metrics=autopoiesis)

    return {
        "higher_order_nodes": higher_order_nodes,
        "higher_order_trajectory": build_higher_order_trajectory(higher_order_nodes),
        "reference_higher_order_node": sam_313["reference_node"],
        "higher_order_sam_313": sam_313,
        "higher_order_sam_313_crystal": sam_313_crystal,
        "source_autopoiesis": autopoiesis,
        "source_crystal": crystal,
    }


def derive_order4_recursive_feedback(higher_order_reading, base_state=None):
    neutral = normalize(base_state if base_state is not None else np.array([1/3, 1/3, 1/3], dtype=float))
    if not higher_order_reading:
        return neutral

    reference_node = higher_order_reading.get("reference_higher_order_node")
    sam_313 = higher_order_reading.get("higher_order_sam_313") or {}
    higher_order_trajectory = higher_order_reading.get("higher_order_trajectory")

    reference_vector = normalize(reference_node["vector"]) if reference_node is not None else neutral
    sam_313_vector = normalize(sam_313["sam_313_vector"]) if sam_313.get("sam_313_vector") is not None else neutral
    trajectory_vector = neutral
    if higher_order_trajectory is not None and len(higher_order_trajectory) > 0:
        trajectory_vector = normalize(np.mean(np.array(higher_order_trajectory, dtype=float), axis=0))

    feedback = normalize(
        (1.0 - ORDER4_FEEDBACK_STRENGTH) * neutral
        + 0.45 * ORDER4_FEEDBACK_STRENGTH * reference_vector
        + 0.35 * ORDER4_FEEDBACK_STRENGTH * sam_313_vector
        + 0.20 * ORDER4_FEEDBACK_STRENGTH * trajectory_vector
    )
    return feedback


def compute_order4_recursive_metrics(higher_order_reading):
    if not higher_order_reading:
        return {
            "active": False,
            "a_closure_index": 0.0,
            "lateral_breathing_index": 0.0,
            "recursive_coherence_index": 0.0,
            "reference_alignment": 0.0,
            "recursive_order4_index": 0.0,
            "regime": "insufficient",
        }

    reference_node = higher_order_reading.get("reference_higher_order_node")
    sam_313 = higher_order_reading.get("higher_order_sam_313") or {}
    source_autopoiesis = higher_order_reading.get("source_autopoiesis") or {}
    source_crystal = higher_order_reading.get("source_crystal") or {}

    reference_vector = normalize(reference_node["vector"]) if reference_node is not None else np.array([1/3, 1/3, 1/3], dtype=float)
    sam_313_vector = normalize(sam_313["sam_313_vector"]) if sam_313.get("sam_313_vector") is not None else np.array([1/3, 1/3, 1/3], dtype=float)

    a_closure_index = float(sam_313_vector[1])
    lateral_breathing_index = float(min(1.0, 2.0 * (sam_313_vector[0] + sam_313_vector[2])))
    recursive_coherence_index = float(max(
        0.0,
        min(
            1.0,
            0.45 * float(source_autopoiesis.get("autopoiesis_index", 0.0))
            + 0.35 * float(source_crystal.get("crystal_autopoiesis_index", 0.0))
            + 0.20 * cosine_similarity(reference_vector, sam_313_vector),
        ),
    ))
    reference_alignment = float(cosine_similarity(reference_vector, sam_313_vector))

    recursive_order4_index = float(max(
        0.0,
        min(
            1.0,
            0.40 * recursive_coherence_index
            + 0.30 * a_closure_index
            + 0.20 * lateral_breathing_index
            + 0.10 * reference_alignment,
        ),
    ))

    if recursive_order4_index >= 0.68 and lateral_breathing_index >= 0.20:
        regime = "recursive_stable"
    elif recursive_order4_index >= 0.45:
        regime = "recursive_tense"
    else:
        regime = "recursive_collapsed"

    return {
        "active": True,
        "a_closure_index": float(round(a_closure_index, 6)),
        "lateral_breathing_index": float(round(lateral_breathing_index, 6)),
        "recursive_coherence_index": float(round(recursive_coherence_index, 6)),
        "reference_alignment": float(round(reference_alignment, 6)),
        "recursive_order4_index": float(round(recursive_order4_index, 6)),
        "regime": regime,
    }


def compute_order3_viability_metrics(higher_order_reading):
    if not higher_order_reading:
        return {
            "active": False,
            "m_closure_index": 0.0,
            "lexical_attachment_index": 0.0,
            "lateral_breathing_index": 0.0,
            "reference_alignment": 0.0,
            "order3_viability_index": 0.0,
            "regime": "insufficient",
        }

    reference_node = higher_order_reading.get("reference_higher_order_node")
    sam_313 = higher_order_reading.get("higher_order_sam_313") or {}
    source_autopoiesis = higher_order_reading.get("source_autopoiesis") or {}
    source_crystal = higher_order_reading.get("source_crystal") or {}

    reference_vector = normalize(reference_node["vector"]) if reference_node is not None else np.array([1/3, 1/3, 1/3], dtype=float)
    sam_313_vector = normalize(sam_313["sam_313_vector"]) if sam_313.get("sam_313_vector") is not None else np.array([1/3, 1/3, 1/3], dtype=float)

    m_closure_index = float(sam_313_vector[2])
    lexical_attachment_index = float(max(
        0.0,
        min(
            1.0,
            0.55 * float(source_autopoiesis.get("continuity_index", 0.0))
            + 0.25 * float(source_crystal.get("global_phi", 0.0))
            + 0.20 * cosine_similarity(reference_vector, sam_313_vector),
        ),
    ))
    lateral_breathing_index = float(max(0.0, min(1.0, 1.0 - abs(float(sam_313_vector[0]) - float(sam_313_vector[1])))))
    reference_alignment = float(cosine_similarity(reference_vector, sam_313_vector))

    order3_viability_index = float(max(
        0.0,
        min(
            1.0,
            0.35 * m_closure_index
            + 0.30 * lexical_attachment_index
            + 0.20 * lateral_breathing_index
            + 0.15 * reference_alignment,
        ),
    ))

    if order3_viability_index >= 0.68 and m_closure_index >= 0.34:
        regime = "order3_integrable"
    elif order3_viability_index >= 0.45:
        regime = "order3_tense"
    else:
        regime = "order3_opaque"

    return {
        "active": True,
        "m_closure_index": float(round(m_closure_index, 6)),
        "lexical_attachment_index": float(round(lexical_attachment_index, 6)),
        "lateral_breathing_index": float(round(lateral_breathing_index, 6)),
        "reference_alignment": float(round(reference_alignment, 6)),
        "order3_viability_index": float(round(order3_viability_index, 6)),
        "regime": regime,
    }

def stability(traj):
    return np.var(traj[-20:])

# =====================================================
# 18. EXPLORE
# =====================================================

def explore():

    results = []

    global USE_INTERVENTION

    original_use_intervention = USE_INTERVENTION
    if not EXPLORE_ALLOW_INTERVENTION:
        USE_INTERVENTION = False

    try:
        for p in PERMUTATION_OPTIONS:
            for r in ROTATION_OPTIONS:
                for c in COLLAPSE_OPTIONS:

                    global BASE_PERMUTATION_MODE, P_matrix, P_inv
                    global ROTATION_MODE, COLLAPSE_MODE

                    BASE_PERMUTATION_MODE = p
                    P_matrix = get_permutation_matrix(p)
                    P_inv = np.linalg.inv(P_matrix)

                    ROTATION_MODE = r
                    COLLAPSE_MODE = c

                    traj = simulate()

                    results.append({
                        "perm": p,
                        "rot": r,
                        "col": c,
                        "stab": stability(traj),
                        "traj": traj,
                        "intervention_enabled": USE_INTERVENTION,
                    })
    finally:
        USE_INTERVENTION = original_use_intervention

    return sorted(results, key=lambda x: x["stab"])

# =====================================================
# 19. COMPARACIÓN AUTOMÁTICA (BASELINE vs FULL)
# =====================================================

def simulate_mode(use_omega, use_coupling):

    global USE_OMEGA, USE_COUPLING

    # guardar estado original
    omega_original = USE_OMEGA
    coupling_original = USE_COUPLING

    # aplicar modo
    USE_OMEGA = use_omega
    USE_COUPLING = use_coupling

    traj = simulate()

    # restaurar estado
    USE_OMEGA = omega_original
    USE_COUPLING = coupling_original

    return traj


def compare_models():

    print("\n========== COMPARACIÓN ==========\n")

    # baseline
    traj_base = simulate_mode(False, False)

    # modelo completo
    traj_full = simulate_mode(True, True)

    # diferencia
    diff = np.linalg.norm(traj_full - traj_base, axis=1)

    # -----------------------------
    # MÉTRICAS
    # -----------------------------
    impact = np.mean(diff)
    max_impact = np.max(diff)

    print(f"Impacto promedio: {impact:.5f}")
    print(f"Impacto máximo: {max_impact:.5f}")

    # -----------------------------
    # GRÁFICOS
    # -----------------------------

    # Trayectorias comparadas
    plt.figure()
    plt.plot(traj_base[:,0], '--', label="S base")
    plt.plot(traj_full[:,0], label="S full")

    plt.plot(traj_base[:,1], '--', label="A base")
    plt.plot(traj_full[:,1], label="A full")

    plt.plot(traj_base[:,2], '--', label="M base")
    plt.plot(traj_full[:,2], label="M full")

    plt.title("Baseline vs Modelo Completo")
    plt.legend()
    plt.show()

    # Diferencia temporal
    plt.figure()
    plt.plot(diff)
    plt.title("Diferencia entre modelos (impacto dinámico)")
    plt.xlabel("Tiempo")
    plt.ylabel("Distancia")
    plt.show()

    return traj_base, traj_full, diff


def run_motor_closure_bridge(traj, seed=None, label="experiment"):
    """Bridge the current RYP state into the recursive motor closure contract."""
    global LAST_MOTOR_CLOSURE_STATE, LAST_MOTOR_CLOSURE_CONTRACT

    if run_motor_recursive_closure is None:
        LAST_MOTOR_CLOSURE_STATE = None
        LAST_MOTOR_CLOSURE_CONTRACT = None
        return None

    contract = build_motor_closure_contract() if build_motor_closure_contract is not None else {}
    LAST_MOTOR_CLOSURE_CONTRACT = contract

    route = contract.get("stage_order") or [
        "CPF", "INS", "CCA", "TAL", "AMG", "HYP", "RF", "CEL",
        "VOZ", "SNP", "VAG", "AUT", "ENT", "HIP", "SOMA", "EFX",
    ]
    if route and route[-1] != MOTOR_CLOSURE_REENTRY_STAGE:
        route = list(route) + [MOTOR_CLOSURE_REENTRY_STAGE]

    if traj is not None and len(traj) > 0:
        final_state = np.asarray(traj[-1], dtype=float)
        summary_text = (
            f"RYP closure bridge seed={seed} label={label} "
            f"final_state={np.round(final_state, 4).tolist()}"
        )
    else:
        summary_text = f"RYP closure bridge seed={seed} label={label}"

    state = run_motor_recursive_closure(summary_text, typ_route_nodes=route, conv_mode="informational", prev_route="RYP_CORE")
    LAST_MOTOR_CLOSURE_STATE = state
    return state


def compute_core_semantic_metrics(
    traj,
    higher_order_reading,
    order3_viability_metrics,
    order4_recursive_metrics,
    motor_closure_metrics,
):
    """Project core dynamics into the semantic theory layer."""
    if not CORE_SEMANTIC_AVAILABLE:
        return None

    final_state = np.asarray(traj[-1], dtype=float) if traj is not None and len(traj) > 0 else np.array([1 / 3, 1 / 3, 1 / 3], dtype=float)
    route = list((motor_closure_metrics or {}).get("route", []))
    final_node = (motor_closure_metrics or {}).get("final_node", MOTOR_CLOSURE_REENTRY_STAGE)
    order3_regime = (order3_viability_metrics or {}).get("regime", "order3_tense")
    order4_regime = (order4_recursive_metrics or {}).get("regime", "recursive_tense")
    order3_value = float((order3_viability_metrics or {}).get("order3_viability_index", 0.0))
    order4_value = float((order4_recursive_metrics or {}).get("recursive_order4_index", 0.0))
    a_closure = float((order4_recursive_metrics or {}).get("a_closure_index", final_state[1]))
    m_viability = float((order3_viability_metrics or {}).get("m_closure_index", final_state[2]))
    higher_order_count = len((higher_order_reading or {}).get("higher_order_nodes", []))
    fractal_profile = compute_fractal_profile(traj)
    fractal_signal = (fractal_profile or {}).get("signal_profile", {})
    fractal_step = (fractal_profile or {}).get("step_profile", {})

    semantic_projection_text = (
        f"core route {' -> '.join(route) if route else 'SAM'}; "
        f"final node {final_node}; "
        f"estado sam S={final_state[0]:.3f} A={final_state[1]:.3f} M={final_state[2]:.3f}; "
        f"orden3 {order3_regime} indice {order3_value:.3f}; "
        f"orden4 {order4_regime} indice {order4_value:.3f}; "
        f"cierre A {a_closure:.3f}; viabilidad M {m_viability:.3f}; "
        f"fractal H {float(fractal_signal.get('hurst', {}).get('value', 0.0)):.3f}; "
        f"fractal DFA {float(fractal_signal.get('dfa_alpha', {}).get('value', 0.0)):.3f}; "
        f"fractal paso {float(fractal_step.get('hurst', {}).get('value', 0.0)):.3f}; "
        f"relay talamo prefrontal y abstraccion recursiva con {higher_order_count} nodos de orden superior."
    )

    extractor = SemanticTheoryExtractor()
    mapper = SemanticMotorMapper()
    planner = SemanticGuidedSAMPlanner()
    profile = extractor.extract_profile_from_text(semantic_projection_text)
    semantic_motor_weights = mapper.compute_all_abstract_motor_weights(profile)
    semantic_route_guidance = planner.compute_semantic_route_guidance(profile)

    return {
        "projection_source": "core_structural_projection",
        "projection_text": semantic_projection_text,
        "dominant_theory": profile.dominant_theory.value,
        "theory_balance": {
            theory.value: float(score)
            for theory, score in profile.theory_balance.items()
        },
        "semantic_motor_weights": semantic_motor_weights,
        "semantic_route_guidance": semantic_route_guidance,
        "fractal_profile": fractal_profile,
    }

# =====================================================
# 20. MAPA DE IMPACTO GLOBAL
# =====================================================

def compute_impact_map():

    impact_matrix = np.zeros((len(ROTATION_OPTIONS), len(COLLAPSE_OPTIONS)))

    for i, r in enumerate(ROTATION_OPTIONS):
        for j, c in enumerate(COLLAPSE_OPTIONS):

            global ROTATION_MODE, COLLAPSE_MODE

            ROTATION_MODE = r
            COLLAPSE_MODE = c

            base = simulate_mode(False, False)
            full = simulate_mode(True, True)

            diff = np.linalg.norm(full - base, axis=1)
            impact_matrix[i,j] = np.mean(diff)

    return impact_matrix


def plot_impact_map(matrix):

    plt.figure()
    plt.imshow(matrix)
    plt.xticks(range(len(COLLAPSE_OPTIONS)), COLLAPSE_OPTIONS)
    plt.yticks(range(len(ROTATION_OPTIONS)), ROTATION_OPTIONS)
    plt.title("Mapa de impacto (Ω + λ)")
    plt.colorbar()
    plt.show()

# =====================================================
# 21. MAPA DE FASES 3D
# =====================================================

def plot_phase_space(traj):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(traj[:,0], traj[:,1], traj[:,2])
    ax.set_xlabel("S")
    ax.set_ylabel("A")
    ax.set_zlabel("M")

    plt.title("Trayectoria en espacio SAM")
    plt.show()

# =====================================================
# 22. CLUSTERING DE PERFILES
# =====================================================

def cluster_profiles(results, k=4):

    finals = np.array([r["traj"][-1] for r in results])

    kmeans = KMeans(n_clusters=k, n_init=10)
    labels = kmeans.fit_predict(finals)

    print("\n--- CLUSTERS DETECTADOS ---\n")

    for i in range(k):
        cluster_points = finals[labels == i]
        mean_state = np.mean(cluster_points, axis=0)

        print(f"Cluster {i}: tamaño={len(cluster_points)}")
        print(f"Centro: {np.round(mean_state,3)}\n")

    return labels

# =====================================================
# 23. MATRIZ DE IMPACTO DETALLADA
# =====================================================

def impact_ranking(results):

    print("\n--- MAYOR IMPACTO ---\n")

    impacts = []

    for r in results:

        base = simulate_mode(False, False)
        full = r["traj"]

        diff = np.linalg.norm(full - base, axis=1)
        impact = np.mean(diff)

        impacts.append((r, impact))

    impacts_sorted = sorted(impacts, key=lambda x: -x[1])

    for r, imp in impacts_sorted[:10]:
        print(f"{r['perm']} | {r['rot']} | {r['col']} → impact={imp:.4f}")

# =====================================================
# 24. CRISTAL SAM (NODOS RECURSIVOS)
# =====================================================

CRYSTAL_THRESHOLD = 0.15   # distancia para conectar nodos
MAX_NODES = 200            # límite para evitar explosión

class SAMNode:

    def __init__(self, state, t):
        self.state = state
        self.time = t
        self.connections = []
        self.phi_local = 0.0

# =====================================================
# 25. CONSTRUIR NODOS
# =====================================================

def build_nodes(traj):

    nodes = []

    for t, x in enumerate(traj):

        if len(nodes) >= MAX_NODES:
            break

        node = SAMNode(x, t)
        nodes.append(node)

    return nodes

# =====================================================
# 26. CONECTAR NODOS (CRISTAL)
# =====================================================

def connect_nodes(nodes):

    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):

            d = np.linalg.norm(nodes[i].state - nodes[j].state)

            if d < CRYSTAL_THRESHOLD:
                nodes[i].connections.append(j)
                nodes[j].connections.append(i)


def compute_local_phi(nodes):
    if not nodes:
        return []

    phi_values = []
    for node in nodes:
        if not node.connections:
            node.phi_local = 0.0
            phi_values.append(node.phi_local)
            continue

        neighbor_distances = [
            np.linalg.norm(node.state - nodes[neighbor_index].state)
            for neighbor_index in node.connections
        ]
        mean_distance = float(np.mean(neighbor_distances)) if neighbor_distances else CRYSTAL_THRESHOLD
        degree_factor = min(1.0, len(node.connections) / max(1.0, np.sqrt(len(nodes))))
        coherence_factor = max(0.0, min(1.0, 1.0 - (mean_distance / max(CRYSTAL_THRESHOLD, 1e-8))))
        node.phi_local = float(max(0.0, min(1.0, 0.6 * coherence_factor + 0.4 * degree_factor)))
        phi_values.append(node.phi_local)

    return phi_values

# =====================================================
# 27. VISUALIZACIÓN DEL CRISTAL
# =====================================================

def plot_crystal(nodes):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # nodos
    for node in nodes:
        x, y, z = node.state
        ax.scatter(x, y, z, s=20)

    # conexiones
    for i, node in enumerate(nodes):
        for j in node.connections:
            p1 = node.state
            p2 = nodes[j].state

            ax.plot(
                [p1[0], p2[0]],
                [p1[1], p2[1]],
                [p1[2], p2[2]],
                linewidth=0.5
            )

    ax.set_xlabel("S")
    ax.set_ylabel("A")
    ax.set_zlabel("M")
    plt.title("Cristal SAM (estructura emergente)")
    plt.show()

# =====================================================
# 28. MÉTRICAS DEL CRISTAL
# =====================================================

def crystal_metrics(nodes, traj_metrics=None, print_metrics=True):

    if not nodes:
        metrics = {
            "node_count": 0,
            "mean_degree": 0.0,
            "max_degree": 0.0,
            "edge_density": 0.0,
            "global_phi": 0.0,
            "coherence_index": 0.0,
            "crystal_autopoiesis_index": 0.0,
            "crystal_autopoiesis_regime": "insufficient",
        }
        if print_metrics:
            print("\n--- MÉTRICAS DEL CRISTAL ---\n")
            print("Nodos: 0")
        return metrics

    degrees = [len(n.connections) for n in nodes]
    phi_values = compute_local_phi(nodes)
    max_edges = max(1.0, (len(nodes) * (len(nodes) - 1)) / 2.0)
    edge_count = float(sum(degrees) / 2.0)
    edge_density = float(edge_count / max_edges)
    global_phi = float(np.mean(phi_values)) if phi_values else 0.0

    connected_ratio = float(sum(1 for degree in degrees if degree > 0) / len(nodes))
    coherence_index = float(max(0.0, min(1.0, 0.55 * global_phi + 0.45 * connected_ratio)))

    trajectory_autopoiesis = 0.0
    if traj_metrics is not None:
        trajectory_autopoiesis = float(traj_metrics.get("autopoiesis_index", 0.0))

    crystal_autopoiesis_index = float(max(
        0.0,
        min(
            1.0,
            0.45 * global_phi + 0.25 * edge_density + 0.15 * coherence_index + 0.15 * trajectory_autopoiesis,
        ),
    ))

    if crystal_autopoiesis_index >= 0.68:
        crystal_regime = "robust"
    elif crystal_autopoiesis_index >= 0.45:
        crystal_regime = "incipient"
    else:
        crystal_regime = "weak"

    metrics = {
        "node_count": len(nodes),
        "mean_degree": float(np.mean(degrees)),
        "max_degree": float(np.max(degrees)),
        "edge_density": float(round(edge_density, 6)),
        "global_phi": float(round(global_phi, 6)),
        "coherence_index": float(round(coherence_index, 6)),
        "trajectory_autopoiesis": float(round(trajectory_autopoiesis, 6)),
        "crystal_autopoiesis_index": float(round(crystal_autopoiesis_index, 6)),
        "crystal_autopoiesis_regime": crystal_regime,
    }

    if print_metrics:
        print("\n--- METRICAS DEL CRISTAL ---\n")
        print("Nodos:", metrics["node_count"])
        print("Conexiones promedio:", metrics["mean_degree"])
        print("Max conexiones:", metrics["max_degree"])
        print("Phi global:", metrics["global_phi"])
        print("Densidad de aristas:", metrics["edge_density"])
        print("Autopoiesis cristalina:", metrics["crystal_autopoiesis_index"], f"({metrics['crystal_autopoiesis_regime']})")

    return metrics

    # =====================================================
# 🧪 EXPERIMENT ENGINE - RYP SCIENTIFIC LABORATORY CORE
# =====================================================

def run_single_experiment(seed=None, ablation=None):

    global USE_OMEGA, USE_COUPLING
    global ROTATION_MODE, COLLAPSE_MODE
    global P_matrix, P_inv
    global BASE_PERMUTATION_MODE

    # 🔥 IMPORTANTE: inicializar estado del sistema
    initialize_base_permutation()

    global USE_OMEGA, USE_COUPLING, ROTATION_MODE, COLLAPSE_MODE

    if seed is not None:
        np.random.seed(seed)

    # -----------------------------
    # ABLATION CONTROL
    # -----------------------------
    if ablation is not None:

        USE_OMEGA = not ablation.get("omega", False)
        USE_COUPLING = not ablation.get("coupling", False)

        if "rotation" in ablation:
            ROTATION_MODE = "SA"

        if "collapse" in ablation:
            global COLLAPSE_MODE
            COLLAPSE_MODE = "global"

    # -----------------------------
    # RUN SIMULATION
    # -----------------------------
    traj = simulate()

    # -----------------------------
    # METRICS CORE
    # -----------------------------
    final_state = traj[-1]

    stability_score = np.var(traj[-20:])
    final_entropy = -np.sum(final_state * np.log(final_state + 1e-8))
    max_dispersion = np.max(np.linalg.norm(traj - traj[0], axis=1))
    autopoiesis = autopoiesis_metrics(traj)
    higher_order_reading = None
    if traj is not None and len(traj) >= ORDER3_MIN_READING_LENGTH:
        higher_order_reading = read_higher_order_elements_from_core(traj, max_order=4)
    order3_viability_metrics = compute_order3_viability_metrics(higher_order_reading)
    if SYSTEM_ORDER == 4 and LAST_ORDER4_RECURSIVE_METRICS is not None:
        order4_recursive_metrics = LAST_ORDER4_RECURSIVE_METRICS
    else:
        order4_recursive_metrics = compute_order4_recursive_metrics(higher_order_reading)

    motor_closure_state = run_motor_closure_bridge(traj, seed=seed, label="single_experiment")
    motor_closure_metrics = None
    if motor_closure_state is not None:
        motor_closure_metrics = {
            "closure_index": float(motor_closure_state.closure_index),
            "coverage_index": float(motor_closure_state.coverage_index),
            "reentry_index": float(motor_closure_state.reentry_index),
            "balance_index": float(motor_closure_state.balance_index),
            "final_node": motor_closure_state.final_node,
            "route": list(motor_closure_state.route),
            "notes": list(motor_closure_state.notes),
        }

    core_semantic_metrics = compute_core_semantic_metrics(
        traj,
        higher_order_reading,
        order3_viability_metrics,
        order4_recursive_metrics,
        motor_closure_metrics,
    )

    return {
        "final_state": final_state,
        "stability": stability_score,
        "entropy": final_entropy,
        "dispersion": max_dispersion,
        "autopoiesis": autopoiesis,
        "order3_viability_metrics": order3_viability_metrics,
        "order4_recursive_metrics": order4_recursive_metrics,
        "motor_closure_metrics": motor_closure_metrics,
        "core_semantic_metrics": core_semantic_metrics,
        "trajectory": traj
    }


# =====================================================
# 🧪 MULTI-RUN STATISTICAL ENGINE
# =====================================================

def run_batch_experiments(n_runs=30, ablation=None):

    results = []

    for i in range(n_runs):

        seed = i * 10 + 42

        result = run_single_experiment(seed=seed, ablation=ablation)

        results.append(result)

    return results


def summarize_order4_recursive_taxonomy(results):
    order4_metrics = [
        r["order4_recursive_metrics"]
        for r in results
        if r.get("order4_recursive_metrics") and r["order4_recursive_metrics"].get("active")
    ]

    if not order4_metrics:
        return None

    def mean_metric(name):
        return float(np.mean([metric[name] for metric in order4_metrics]))

    regime_counts = {
        "recursive_collapsed": 0,
        "recursive_tense": 0,
        "recursive_stable": 0,
    }
    for metric in order4_metrics:
        regime = metric.get("regime")
        if regime in regime_counts:
            regime_counts[regime] += 1

    dominant_regime = max(regime_counts, key=regime_counts.get)
    total = max(1, len(order4_metrics))

    return {
        "n_active_runs": len(order4_metrics),
        "mean_a_closure": mean_metric("a_closure_index"),
        "mean_lateral_breathing": mean_metric("lateral_breathing_index"),
        "mean_recursive_coherence": mean_metric("recursive_coherence_index"),
        "mean_reference_alignment": mean_metric("reference_alignment"),
        "mean_recursive_order4": mean_metric("recursive_order4_index"),
        "dominant_regime": dominant_regime,
        "regime_counts": regime_counts,
        "regime_proportions": {
            key: float(value / total)
            for key, value in regime_counts.items()
        },
    }


def summarize_order3_viability_taxonomy(results):
    order3_metrics = [
        r["order3_viability_metrics"]
        for r in results
        if r.get("order3_viability_metrics") and r["order3_viability_metrics"].get("active")
    ]

    if not order3_metrics:
        return None

    def mean_metric(name):
        return float(np.mean([metric[name] for metric in order3_metrics]))

    regime_counts = {
        "order3_opaque": 0,
        "order3_tense": 0,
        "order3_integrable": 0,
    }
    for metric in order3_metrics:
        regime = metric.get("regime")
        if regime in regime_counts:
            regime_counts[regime] += 1

    dominant_regime = max(regime_counts, key=regime_counts.get)
    total = max(1, len(order3_metrics))

    return {
        "n_active_runs": len(order3_metrics),
        "mean_m_closure": mean_metric("m_closure_index"),
        "mean_lexical_attachment": mean_metric("lexical_attachment_index"),
        "mean_lateral_breathing": mean_metric("lateral_breathing_index"),
        "mean_reference_alignment": mean_metric("reference_alignment"),
        "mean_order3_viability": mean_metric("order3_viability_index"),
        "dominant_regime": dominant_regime,
        "regime_counts": regime_counts,
        "regime_proportions": {
            key: float(value / total)
            for key, value in regime_counts.items()
        },
    }


def build_order3_viability_markdown_report(order3_taxonomy, label="experiment"):
    if not order3_taxonomy:
        return "# Order 3 Viability Taxonomy\n\nNo active order-3 viability metrics were found for this batch.\n"

    regime_labels = {
        "order3_opaque": "opacidad de orden 3",
        "order3_tense": "tension de orden 3",
        "order3_integrable": "viabilidad integrable de orden 3",
    }
    dominant_regime = order3_taxonomy["dominant_regime"]

    return f"""# Order 3 Viability Taxonomy\n\n## Batch\n\n- label: {label}\n- active_runs: {order3_taxonomy['n_active_runs']}\n- dominant_regime: {dominant_regime} ({regime_labels.get(dominant_regime, dominant_regime)})\n\n## Mean Metrics\n\n| metric | value |\n| --- | ---: |\n| m_closure_index | {order3_taxonomy['mean_m_closure']:.6f} |\n| lexical_attachment_index | {order3_taxonomy['mean_lexical_attachment']:.6f} |\n| lateral_breathing_index | {order3_taxonomy['mean_lateral_breathing']:.6f} |\n| reference_alignment | {order3_taxonomy['mean_reference_alignment']:.6f} |\n| order3_viability_index | {order3_taxonomy['mean_order3_viability']:.6f} |\n\n## Regime Distribution\n\n| regime | count | proportion |\n| --- | ---: | ---: |\n| order3_opaque | {order3_taxonomy['regime_counts']['order3_opaque']} | {order3_taxonomy['regime_proportions']['order3_opaque']:.3f} |\n| order3_tense | {order3_taxonomy['regime_counts']['order3_tense']} | {order3_taxonomy['regime_proportions']['order3_tense']:.3f} |\n| order3_integrable | {order3_taxonomy['regime_counts']['order3_integrable']} | {order3_taxonomy['regime_proportions']['order3_integrable']:.3f} |\n"""


def build_order4_recursive_markdown_report(order4_taxonomy, label="experiment"):
    if not order4_taxonomy:
        return "# Order 4 Recursive Taxonomy\n\nNo active order-4 recursive metrics were found for this batch.\n"

    regime_labels = {
        "recursive_collapsed": "colapso recursivo",
        "recursive_tense": "tension recursiva",
        "recursive_stable": "estabilidad recursiva",
    }
    dominant_regime = order4_taxonomy["dominant_regime"]

    return f"""# Order 4 Recursive Taxonomy\n\n## Batch\n\n- label: {label}\n- active_runs: {order4_taxonomy['n_active_runs']}\n- dominant_regime: {dominant_regime} ({regime_labels.get(dominant_regime, dominant_regime)})\n\n## Mean Metrics\n\n| metric | value |\n| --- | ---: |\n| a_closure_index | {order4_taxonomy['mean_a_closure']:.6f} |\n| lateral_breathing_index | {order4_taxonomy['mean_lateral_breathing']:.6f} |\n| recursive_coherence_index | {order4_taxonomy['mean_recursive_coherence']:.6f} |\n| reference_alignment | {order4_taxonomy['mean_reference_alignment']:.6f} |\n| recursive_order4_index | {order4_taxonomy['mean_recursive_order4']:.6f} |\n\n## Regime Distribution\n\n| regime | count | proportion |\n| --- | ---: | ---: |\n| recursive_collapsed | {order4_taxonomy['regime_counts']['recursive_collapsed']} | {order4_taxonomy['regime_proportions']['recursive_collapsed']:.3f} |\n| recursive_tense | {order4_taxonomy['regime_counts']['recursive_tense']} | {order4_taxonomy['regime_proportions']['recursive_tense']:.3f} |\n| recursive_stable | {order4_taxonomy['regime_counts']['recursive_stable']} | {order4_taxonomy['regime_proportions']['recursive_stable']:.3f} |\n"""


# =====================================================
# 📊 EXPERIMENT ANALYSIS LAYER
# =====================================================

def analyze_batch(results, label="experiment"):

    finals = np.array([r["final_state"] for r in results])
    stability = np.array([r["stability"] for r in results])
    entropy = np.array([r["entropy"] for r in results])
    autopoiesis_index = np.array([r["autopoiesis"]["autopoiesis_index"] for r in results])
    order3_viability_values = np.array([
        r["order3_viability_metrics"]["order3_viability_index"]
        for r in results
        if r.get("order3_viability_metrics") and r["order3_viability_metrics"].get("active")
    ])
    recursive_order4_values = np.array([
        r["order4_recursive_metrics"]["recursive_order4_index"]
        for r in results
        if r.get("order4_recursive_metrics") and r["order4_recursive_metrics"].get("active")
    ])
    order3_taxonomy = summarize_order3_viability_taxonomy(results)
    order4_taxonomy = summarize_order4_recursive_taxonomy(results)

    print("\n==============================")
    print(f"ANALYSIS: {label}")
    print("==============================")

    print("Final state mean:", np.mean(finals, axis=0))
    print("Final state variance:", np.var(finals, axis=0))

    print("Stability mean:", np.mean(stability))
    print("Entropy mean:", np.mean(entropy))
    print("Autopoiesis mean:", np.mean(autopoiesis_index))
    if len(order3_viability_values) > 0:
        print("Order3 viability mean:", np.mean(order3_viability_values))
    if order3_taxonomy:
        print("Order3 dominant regime:", order3_taxonomy["dominant_regime"])
        print("Order3 M closure mean:", order3_taxonomy["mean_m_closure"])
        print("Order3 lexical attachment mean:", order3_taxonomy["mean_lexical_attachment"])
        print("Order3 lateral breathing mean:", order3_taxonomy["mean_lateral_breathing"])
        print("Order3 regime counts:", order3_taxonomy["regime_counts"])
    if len(recursive_order4_values) > 0:
        print("Order4 recursive mean:", np.mean(recursive_order4_values))
    if order4_taxonomy:
        print("Order4 dominant regime:", order4_taxonomy["dominant_regime"])
        print("Order4 A closure mean:", order4_taxonomy["mean_a_closure"])
        print("Order4 lateral breathing mean:", order4_taxonomy["mean_lateral_breathing"])
        print("Order4 recursive coherence mean:", order4_taxonomy["mean_recursive_coherence"])
        print("Order4 regime counts:", order4_taxonomy["regime_counts"])

    payload = {
        "mean_final": np.mean(finals, axis=0),
        "var_final": np.var(finals, axis=0),
        "mean_stability": np.mean(stability),
        "mean_entropy": np.mean(entropy),
        "mean_autopoiesis": np.mean(autopoiesis_index),
    }
    if len(order3_viability_values) > 0:
        payload["mean_order3_viability"] = np.mean(order3_viability_values)
    if order3_taxonomy:
        payload["order3_taxonomy"] = order3_taxonomy
        payload["order3_markdown_report"] = build_order3_viability_markdown_report(order3_taxonomy, label=label)
    if len(recursive_order4_values) > 0:
        payload["mean_order4_recursive"] = np.mean(recursive_order4_values)
    if order4_taxonomy:
        payload["order4_taxonomy"] = order4_taxonomy
        payload["order4_markdown_report"] = build_order4_recursive_markdown_report(order4_taxonomy, label=label)
    return payload


# =====================================================
# 🔬 FULL EXPERIMENT SUITE
# =====================================================

def run_full_experiment_suite():

    print("\n🚀 RUNNING FULL EXPERIMENT SUITE\n")

    # -----------------------------
    # BASELINE
    # -----------------------------
    base = run_batch_experiments(n_runs=N_RUNS, ablation=None)
    base_stats = analyze_batch(base, "BASELINE")

    # -----------------------------
    # ABLATIONS
    # -----------------------------
    results = {"baseline": base_stats}

    if ABLATE_OMEGA:

        omega = run_batch_experiments(
            n_runs=N_RUNS,
            ablation={"omega": True}
        )
        results["no_omega"] = analyze_batch(omega, "NO OMEGA")

    if ABLATE_COUPLING:

        coupling = run_batch_experiments(
            n_runs=N_RUNS,
            ablation={"coupling": True}
        )
        results["no_coupling"] = analyze_batch(coupling, "NO COUPLING")

    if ABLATE_COLLAPSE:

        collapse = run_batch_experiments(
            n_runs=N_RUNS,
            ablation={"collapse": True}
        )
        results["no_collapse"] = analyze_batch(collapse, "NO COLLAPSE")

    if ABLATE_ROTATION:

        rotation = run_batch_experiments(
            n_runs=N_RUNS,
            ablation={"rotation": True}
        )
        results["no_rotation"] = analyze_batch(rotation, "NO ROTATION")

    return results


# =====================================================
# 🔬 AUTO TRIGGER (CONTROLLED BY PANEL)
# =====================================================

if AUTO_RUN_ALL:
    EXPERIMENT_RESULTS = run_full_experiment_suite()
# =====================================================
# 🔤 SAM LINGÜÍSTICO (PATCH)
# =====================================================

LETTER_SAM = {
    "a": [0.6,0.3,0.1],
    "e": [0.5,0.4,0.1],
    "i": [0.7,0.2,0.1],
    "o": [0.4,0.4,0.2],
    "u": [0.3,0.5,0.2],
}

def char_to_sam(c):
    return np.array(LETTER_SAM.get(c.lower(), [0.33,0.33,0.33]))

def word_to_sam(word):

    vecs = [char_to_sam(c) for c in word if c.isalpha()]

    if not vecs:
        return np.array([1/3,1/3,1/3])

    return normalize(np.mean(vecs, axis=0))

def text_to_sam(text):

    words = text.split()
    vecs = [word_to_sam(w) for w in words]

    if not vecs:
        return np.array([1/3,1/3,1/3])

    return normalize(np.mean(vecs, axis=0))

# =====================================================
# 🔬 SIMULACIÓN DESDE TEXTO
# =====================================================

def simulate_text(text, simulate_fn, steps=50):
    """
    Convierte texto → SAM → corre simulación
    Compatible con tu simulate real
    """

    x0 = text_to_sam(text)

    # 👇 IMPORTANTE: pasar como argumento posicional, no nombrado
    traj = simulate_fn(x0, steps)

    return traj

    if SYSTEM_ORDER == 1:

        for t in range(steps):
            x = F(x, np.zeros(3), t)
            traj.append(x.copy())

    else:

        xA = x.copy()
        xB = np.array([1/3,1/3,1/3])

        for t in range(steps):
            xA = F(xA, xB, t)
            xB = F(xB, xA, t)
            traj.append(xA.copy())

    return np.array(traj)

# =====================================================
# 🔬 ENTROPÍA
# =====================================================

def entropy(x):
    return -np.sum(x*np.log(x+1e-8))
# =====================================================
# 29. EJECUCIÓN PRINCIPAL
# =====================================================

def main():

    if PRINT_CONFIG:
        print("\n========== CONFIGURACIÓN ==========")
        print("Modo:", MODE)
        print("Orden:", SYSTEM_ORDER)
        print("Comparación:", COMPARE_MODE)
        print("Análisis avanzado:", ADVANCED_ANALYSIS)
        print("Cristal:", BUILD_CRYSTAL)

    initialize_base_permutation()

    traj = simulate()

    plt.plot(traj[:,0], label="S")
    plt.plot(traj[:,1], label="A")
    plt.plot(traj[:,2], label="M")
    plt.legend()
    plt.show()

    results = None
    traj_base = None
    traj_full = None
    diff = None

    if MODE == "explore":

        results = explore()

        print("\n--- TOP RESULTADOS ---\n")

        for r in results[:10]:
            print(f"{r['perm']} | {r['rot']} | {r['col']} → {r['stab']:.5f}")

        best = results[0]["traj"]

        plt.figure()
        plt.plot(best)
        plt.title("Mejor configuración")
        plt.legend(["S","A","M"])
        plt.show()

        print("Simulación OK")

    if COMPARE_MODE:
        traj_base, traj_full, diff = compare_models()

    if ADVANCED_ANALYSIS and traj_full is not None and results is not None:

        print("\n========== ANÁLISIS AVANZADO ==========")

        # mapa de impacto
        impact_map = compute_impact_map()
        plot_impact_map(impact_map)

        # fase 3D
        plot_phase_space(traj_full)

        # clustering
        labels = cluster_profiles(results)

        # ranking impacto
        impact_ranking(results)

    if BUILD_CRYSTAL and traj_full is not None:

        print("\n========== CONSTRUCCIÓN DEL CRISTAL ==========")

        nodes = build_nodes(traj_full if COMPARE_MODE else traj)

        connect_nodes(nodes)

        reference_traj = traj_full if COMPARE_MODE else traj
        crystal_metrics(nodes, traj_metrics=autopoiesis_metrics(reference_traj))

        plot_crystal(nodes)


if __name__ == "__main__":
    main()
# =====================================================
# 🔬 SCIENTIFIC LOGGING LAYER
# =====================================================

def log_experiment(name, value):
    print(f"[{EXPERIMENT_NAME}] {name}: {value}")

def save_state(traj, label):
    if EXPORT_RESULTS:
        print(f"Saving {label} trajectory (mock export)")