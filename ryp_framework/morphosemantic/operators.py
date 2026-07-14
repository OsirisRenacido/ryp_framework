import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import numpy as np


def normalize(vector: Iterable[float]) -> np.ndarray:
    values = np.array(list(vector), dtype=float)
    values = np.maximum(values, 0.0)
    total = float(values.sum())
    if total <= 0.0:
        return np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0], dtype=float)
    return values / total


@dataclass(frozen=True)
class MorphOperator:
    name: str
    sam: tuple[float, float, float]
    position: str = "suffix"
    weight: float = 1.0

    def vector(self) -> np.ndarray:
        return normalize(self.sam)


@dataclass(frozen=True)
class ProjectionTrace:
    name: str
    kind: str
    weight: float
    vector: tuple[float, float, float]


@dataclass(frozen=True)
class LocalProjection:
    label: str
    sam: tuple[float, float, float]
    dominant_axis: str
    root_term: str
    operator_names: tuple[str, ...]


def _default_lexicon_path() -> Path:
    return Path(__file__).with_name("RYP_LEXICON.json")


DEFAULT_OPERATORS = {
    "fron": MorphOperator("fron", (0.22, 0.18, 0.60), position="prefix", weight=1.05),
    "tera": MorphOperator("tera", (0.20, 0.34, 0.46), position="suffix", weight=0.95),
    "al": MorphOperator("al", (0.18, 0.60, 0.22), position="suffix", weight=1.00),
    "mente": MorphOperator("mente", (0.48, 0.34, 0.18), position="suffix", weight=1.10),
    "ente": MorphOperator("ente", (0.34, 0.42, 0.24), position="suffix", weight=1.00),
    "super": MorphOperator("super", (0.24, 0.28, 0.48), position="prefix", weight=1.00),
}

ORDER_AXIS_CYCLE = ("S", "A", "M")
AXIS_INDEX = {axis: index for index, axis in enumerate(ORDER_AXIS_CYCLE)}
AXIS_DEFINITIONS = {
    "S": {
        "label": "estructuracion cognitiva",
        "definition": "organiza criterio, diferenciacion, lectura de forma y capacidad de sostener una estructura semantica.",
        "negation": "no-S no significa vacio cognitivo, sino desplazamiento del criterio hacia acoplamiento relacional A y/o descarga ejecutiva M.",
    },
    "A": {
        "label": "acoplamiento relacional",
        "definition": "organiza vinculo, sintonia, modulacion interpersonal y ajuste reciproco con el contexto.",
        "negation": "no-A no implica aislamiento absoluto, sino primacia del criterio S o de la ejecucion M sobre la mediacion relacional.",
    },
    "M": {
        "label": "materializacion operativa",
        "definition": "organiza ejecucion, descarga, implementacion y traduccion de un estado semantico a acto o movimiento.",
        "negation": "no-M no significa inmovilidad total, sino suspension de la descarga en favor de estructura S o regulacion vincular A.",
    },
}
PERMUTATION_INTERPRETATIONS = {
    "SAM": "S domina, A modula y M ejecuta al final: el criterio organiza el vinculo antes de pasar a la accion.",
    "SMA": "S domina, M acelera y A queda en tercer lugar: el criterio se traduce rapido en operacion y la relacion se ajusta tarde.",
    "ASM": "A domina, S ordena y M cierra: el vinculo abre el proceso, el criterio lo estabiliza y la accion lo realiza.",
    "AMS": "A domina, M precipita y S queda relegado: la relacion empuja a actuar antes de consolidar criterio.",
    "MSA": "M domina, S reordena y A queda al final: la ejecucion abre escena y el criterio intenta estabilizar despues.",
    "MAS": "M domina, A busca acompasamiento y S queda ultimo: la accion manda y el criterio aparece como correccion tardia.",
}
FAMILY_SCHEMES = {
    "structural": {
        "S": "triadia",
        "A": "trama",
        "M": "cristal",
    },
    "relational": {
        "S": "triadia",
        "A": "amistad",
        "M": "cristal",
    },
}
DEFAULT_FAMILY_SCHEME = "structural"


def _rank_axes(vector: Iterable[float]) -> list[str]:
    normalized = normalize(vector)
    ranked = sorted(ORDER_AXIS_CYCLE, key=lambda axis: float(normalized[AXIS_INDEX[axis]]), reverse=True)
    return ranked


def describe_axis_state(vector: Iterable[float]) -> dict[str, dict]:
    normalized = normalize(vector)
    ranked_axes = _rank_axes(normalized)
    profile = {}
    for axis in ORDER_AXIS_CYCLE:
        index = AXIS_INDEX[axis]
        value = float(normalized[index])
        other_axes = [candidate for candidate in ORDER_AXIS_CYCLE if candidate != axis]
        complement = float(sum(normalized[AXIS_INDEX[candidate]] for candidate in other_axes))
        rank = ranked_axes.index(axis) + 1
        if rank == 1:
            state = "dominante"
            interpretation = AXIS_DEFINITIONS[axis]["definition"]
        elif rank == 2:
            state = "intermedio"
            interpretation = f"{axis} permanece disponible, pero queda conjugado por {ranked_axes[0]} y contiene una negacion parcial de si mismo."
        else:
            state = "recesivo"
            interpretation = AXIS_DEFINITIONS[axis]["negation"]
        profile[axis] = {
            "axis": axis,
            "label": AXIS_DEFINITIONS[axis]["label"],
            "value": round(value, 6),
            "rank": rank,
            "state": state,
            "definition": AXIS_DEFINITIONS[axis]["definition"],
            "negation": AXIS_DEFINITIONS[axis]["negation"],
            "complement_value": round(complement, 6),
            "conjugated_with": ranked_axes[0] if rank > 1 else ranked_axes[1],
            "interpretation": interpretation,
        }
    return profile


def interpret_axis_permutation(vector: Iterable[float]) -> dict:
    normalized = normalize(vector)
    ranked_axes = _rank_axes(normalized)
    signature = "".join(ranked_axes)
    primary, secondary, tertiary = ranked_axes
    interpretation = PERMUTATION_INTERPRETATIONS.get(
        signature,
        f"Permutacion {signature}: {primary} abre el regimen, {secondary} lo modula y {tertiary} queda como funcion recesiva.",
    )
    return {
        "signature": signature,
        "primary_axis": primary,
        "secondary_axis": secondary,
        "tertiary_axis": tertiary,
        "interpretation": interpretation,
    }


def _position_gain(position: str) -> float:
    if position == "prefix":
        return 1.12
    if position == "infix":
        return 0.94
    return 1.00


def _interaction_gain(base_vector: np.ndarray, operator_vector: np.ndarray) -> float:
    return 1.0 + 0.15 * float(np.dot(base_vector, operator_vector))


def compute_self_observation_proxy(state_sam: Iterable[float]) -> float:
    state = normalize(state_sam)
    entropy = -float(np.sum(state * np.log(state + 1e-10)))
    max_entropy = float(np.log(3.0))
    phi = entropy / max_entropy
    correlation = 1.0 - float(np.std(state))
    return 0.6 * phi + 0.4 * correlation


def collapse_morphosemantic_sam(
    root_sam: Iterable[float],
    operators: Iterable[MorphOperator],
    context_sam: Optional[Iterable[float]] = None,
    root_weight: float = 0.58,
    operator_weight: float = 0.28,
    context_weight: float = 0.14,
    root_memory: float = 0.22,
) -> dict:
    root_vector = normalize(root_sam)
    running_state = root_vector * root_weight
    trace: List[ProjectionTrace] = [
        ProjectionTrace(
            name="root",
            kind="root",
            weight=root_weight,
            vector=tuple(np.round(root_vector, 6)),
        )
    ]

    ordered_operators = list(operators)
    total_operators = max(len(ordered_operators), 1)

    for index, operator in enumerate(ordered_operators):
        operator_vector = operator.vector()
        order_gain = 1.0 + 0.08 * (total_operators - index - 1)
        position_gain = _position_gain(operator.position)
        interaction_gain = _interaction_gain(normalize(running_state + root_vector * root_memory), operator_vector)
        effective_weight = operator_weight * operator.weight * order_gain * position_gain * interaction_gain
        contribution = operator_vector * effective_weight
        running_state = running_state + contribution
        running_state = normalize(running_state + root_vector * root_memory)
        trace.append(
            ProjectionTrace(
                name=operator.name,
                kind="operator",
                weight=effective_weight,
                vector=tuple(np.round(operator_vector, 6)),
            )
        )

    if context_sam is not None:
        context_vector = normalize(context_sam)
        effective_context_weight = context_weight * (1.0 + 0.10 * float(np.dot(running_state, context_vector)))
        running_state = normalize(running_state + context_vector * effective_context_weight + root_vector * (root_memory / 2.0))
        trace.append(
            ProjectionTrace(
                name="context",
                kind="context",
                weight=effective_context_weight,
                vector=tuple(np.round(context_vector, 6)),
            )
        )

    result_vector = normalize(running_state + root_vector * root_memory)
    axis_profile = describe_axis_state(result_vector)
    axis_permutation = interpret_axis_permutation(result_vector)
    return {
        "sam": result_vector,
        "dominant_axis": ["S", "A", "M"][int(np.argmax(result_vector))],
        "axis_profile": axis_profile,
        "axis_permutation": axis_permutation,
        "root_drift": float(np.linalg.norm(result_vector - root_vector)),
        "trace": [
            {
                "name": item.name,
                "kind": item.kind,
                "weight": round(item.weight, 6),
                "vector": list(item.vector),
            }
            for item in trace
        ],
    }


def build_operator_sequence(names: Iterable[str]) -> list[MorphOperator]:
    sequence = []
    for name in names:
        if name not in DEFAULT_OPERATORS:
            raise KeyError(f"Operador morfosemantico no definido: {name}")
        sequence.append(DEFAULT_OPERATORS[name])
    return sequence


def load_local_lexicon(lexicon_path: Optional[str] = None) -> dict:
    path = Path(lexicon_path) if lexicon_path else _default_lexicon_path()
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_lexicon_vector(term: str, lexicon: Optional[dict] = None, lexicon_path: Optional[str] = None) -> np.ndarray:
    data = lexicon if lexicon is not None else load_local_lexicon(lexicon_path)
    key = term.lower().strip()
    if key not in data:
        raise KeyError(f"Termino no encontrado en el lexicon: {term}")
    entry = data[key]
    if isinstance(entry, dict):
        return normalize(entry["sam"])
    return normalize(entry)


def project_from_lexicon(
    root_term: str,
    operator_names: Iterable[str],
    context_term: Optional[str] = None,
    lexicon: Optional[dict] = None,
    lexicon_path: Optional[str] = None,
    label: Optional[str] = None,
) -> dict:
    data = lexicon if lexicon is not None else load_local_lexicon(lexicon_path)
    root_vector = get_lexicon_vector(root_term, lexicon=data)
    context_vector = get_lexicon_vector(context_term, lexicon=data) if context_term else None
    result = collapse_morphosemantic_sam(
        root_vector,
        build_operator_sequence(operator_names),
        context_sam=context_vector,
    )
    result["label"] = label or root_term
    result["root_term"] = root_term
    result["operator_names"] = list(operator_names)
    result["context_term"] = context_term
    return result


def _pairwise_dispersion(vectors: list[np.ndarray]) -> float:
    if len(vectors) < 2:
        return 0.0
    distances = []
    for index, left in enumerate(vectors):
        for right in vectors[index + 1:]:
            distances.append(float(np.linalg.norm(left - right)))
    return float(np.mean(distances)) if distances else 0.0


def evaluate_projection_stability(
    projections: Iterable[dict],
    relation_density: float = 0.55,
    attention_load: float = 0.45,
    coherence_bias: float = 0.60,
) -> dict:
    items = list(projections)
    if not items:
        neutral = np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0], dtype=float)
        return {
            "global_sam": neutral,
            "stability_index": 1.0,
            "integration": 1.0,
            "fragmentation": 0.0,
            "overload": 0.0,
            "regime": "stable",
            "local_count": 0,
        }

    vectors = [normalize(item["sam"]) for item in items]
    centroid = normalize(np.mean(vectors, axis=0))
    drift_values = [float(np.linalg.norm(vector - centroid)) for vector in vectors]
    fragmentation = min(1.0, float(np.mean(drift_values)) * 1.9)
    dispersion = min(1.0, _pairwise_dispersion(vectors) * 1.7)
    axis_entropy = -float(np.sum(centroid * np.log(np.maximum(centroid, 1e-9)))) / float(np.log(3.0))
    axis_balance = max(0.0, min(1.0, axis_entropy))
    integration = max(
        0.0,
        min(
            1.0,
            0.20
            + 0.34 * axis_balance
            + 0.18 * relation_density
            + 0.18 * coherence_bias
            - 0.28 * fragmentation
            - 0.16 * dispersion,
        ),
    )
    load_pressure = attention_load * (1.0 + 0.08 * max(len(items) - 1, 0))
    overload = max(
        0.0,
        min(
            1.0,
            load_pressure
            * (0.25 + 0.55 * fragmentation + 0.20 * (1.0 - relation_density))
            * (1.0 + 0.10 * max(len(items) - 3, 0)),
        ),
    )
    stability_index = max(
        0.0,
        min(
            1.0,
            0.45 * integration + 0.25 * axis_balance + 0.20 * relation_density + 0.10 * coherence_bias - 0.35 * overload,
        ),
    )

    if stability_index >= 0.72 and overload < 0.35:
        regime = "stable"
    elif stability_index >= 0.50 and overload < 0.55:
        regime = "tense"
    elif stability_index >= 0.30:
        regime = "overloaded"
    else:
        regime = "fragmented"

    return {
        "global_sam": centroid,
        "stability_index": stability_index,
        "integration": integration,
        "fragmentation": fragmentation,
        "dispersion": dispersion,
        "overload": overload,
        "regime": regime,
        "local_count": len(items),
        "contributors": [
            LocalProjection(
                label=str(item.get("label", item.get("root_term", f"projection_{index}"))),
                sam=tuple(np.round(vectors[index], 6)),
                dominant_axis=str(item["dominant_axis"]),
                root_term=str(item.get("root_term", "")),
                operator_names=tuple(str(name) for name in item.get("operator_names", [])),
            ).__dict__
            for index, item in enumerate(items)
        ],
    }


def build_global_projection_from_lexicon(experiments: Iterable[dict], lexicon_path: Optional[str] = None) -> dict:
    data = load_local_lexicon(lexicon_path)
    local_results = [
        project_from_lexicon(
            root_term=experiment["root_term"],
            operator_names=experiment.get("operator_names", []),
            context_term=experiment.get("context_term"),
            lexicon=data,
            label=experiment.get("label"),
        )
        for experiment in experiments
    ]
    stability = evaluate_projection_stability(
        local_results,
        relation_density=float(np.mean([experiment.get("relation_density", 0.55) for experiment in experiments])) if local_results else 0.55,
        attention_load=float(np.mean([experiment.get("attention_load", 0.45) for experiment in experiments])) if local_results else 0.45,
        coherence_bias=float(np.mean([experiment.get("coherence_bias", 0.60) for experiment in experiments])) if local_results else 0.60,
    )
    return {
        "local_projections": local_results,
        "global_projection": stability,
    }


def infer_order_axis(order: int) -> str:
    if order <= 0:
        raise ValueError("El orden superior debe ser un entero positivo.")
    return ORDER_AXIS_CYCLE[(order - 1) % len(ORDER_AXIS_CYCLE)]


def get_order_axis_families(family_scheme: str = DEFAULT_FAMILY_SCHEME) -> dict[str, str]:
    if family_scheme not in FAMILY_SCHEMES:
        raise KeyError(f"Esquema de familias no definido: {family_scheme}")
    return FAMILY_SCHEMES[family_scheme]


def suggest_higher_order_node_name(
    order: int,
    dominant_axis: str,
    label: Optional[str] = None,
    family_scheme: str = DEFAULT_FAMILY_SCHEME,
) -> str:
    order_axis = infer_order_axis(order)
    dominant_axis = dominant_axis.upper()
    family = get_order_axis_families(family_scheme)[order_axis]

    if dominant_axis == order_axis:
        core_name = family
    else:
        core_name = f"{family}_{dominant_axis.lower()}"

    if label:
        normalized_label = str(label).strip().lower().replace(" ", "_")
        return f"{core_name}_{normalized_label}"
    return core_name


def build_higher_order_node(
    global_projection: dict,
    order: int,
    label: Optional[str] = None,
    relation_mode: str = "general",
    family_scheme: str = DEFAULT_FAMILY_SCHEME,
) -> dict:
    projection = global_projection["global_projection"] if "global_projection" in global_projection else global_projection
    vector = normalize(projection["global_sam"])
    dominant_axis = ["S", "A", "M"][int(np.argmax(vector))]
    axis_profile = describe_axis_state(vector)
    axis_permutation = interpret_axis_permutation(vector)
    order_axis = infer_order_axis(order)
    suggested_name = suggest_higher_order_node_name(order, dominant_axis, label=label, family_scheme=family_scheme)
    order_family = get_order_axis_families(family_scheme)[order_axis]

    if relation_mode == "friendship" and dominant_axis == "A":
        semantic_role = "amistad"
    elif dominant_axis == "S":
        semantic_role = "triadia"
    elif dominant_axis == "A":
        semantic_role = "trama"
    else:
        semantic_role = "cristal"

    return {
        "name": suggested_name,
        "order": order,
        "order_axis": order_axis,
        "order_family": order_family,
        "dominant_axis": dominant_axis,
        "axis_profile": axis_profile,
        "axis_permutation": axis_permutation,
        "semantic_role": semantic_role,
        "vector": vector,
        "stability_index": projection["stability_index"],
        "regime": projection["regime"],
        "relation_mode": relation_mode,
        "family_scheme": family_scheme,
        "contributors": projection.get("contributors", []),
    }


def higher_order_node_to_crystal_node(
    higher_node: dict,
    index: int,
    time: int = 0,
) -> dict:
    state_3d = normalize(higher_node["vector"])
    phi = compute_self_observation_proxy(state_3d)
    return {
        "index": index,
        "time": time,
        "state_3d": state_3d,
        "state_4d": np.append(state_3d, phi),
        "connections": [],
        "higher_order": True,
        "order": int(higher_node["order"]),
        "order_axis": str(higher_node["order_axis"]),
        "order_family": str(higher_node.get("order_family", "")),
        "dominant_axis": str(higher_node["dominant_axis"]),
        "semantic_role": str(higher_node["semantic_role"]),
        "name": str(higher_node["name"]),
        "stability_index": float(higher_node["stability_index"]),
        "regime": str(higher_node["regime"]),
    }


def build_higher_order_crystal_nodes(
    experiment_specs: Iterable[dict],
    family_scheme: str = DEFAULT_FAMILY_SCHEME,
    start_time: int = 0,
) -> list[dict]:
    crystal_nodes = []
    for index, spec in enumerate(experiment_specs):
        projection = build_global_projection_from_lexicon(spec["experiments"])
        higher_node = build_higher_order_node(
            projection,
            order=spec["order"],
            label=spec.get("label"),
            relation_mode=spec.get("relation_mode", "general"),
            family_scheme=family_scheme,
        )
        crystal_nodes.append(higher_order_node_to_crystal_node(higher_node, index=index, time=start_time + index))
    return crystal_nodes


def build_higher_order_trajectory(crystal_nodes: Iterable[dict]) -> np.ndarray:
    nodes = list(crystal_nodes)
    if not nodes:
        return np.zeros((0, 3), dtype=float)
    trajectory = []
    for node in nodes:
        if "state_3d" in node:
            trajectory.append(normalize(node["state_3d"]))
        elif "vector" in node:
            trajectory.append(normalize(node["vector"]))
        else:
            raise KeyError("Cada nodo debe incluir 'state_3d' o 'vector'.")
    return np.array(trajectory, dtype=float)


def split_text_into_segments(text: str, segments: int = 3) -> list[str]:
    cleaned = text.strip()
    if not cleaned:
        return []
    words = cleaned.split()
    if not words:
        return []
    segments = max(1, int(segments))
    chunk_size = max(1, int(np.ceil(len(words) / segments)))
    return [" ".join(words[index:index + chunk_size]) for index in range(0, len(words), chunk_size)]


def build_global_projection_from_text(
    text: str,
    label_prefix: str = "segment",
    segments: int = 3,
    relation_density: float = 0.60,
    attention_load: float = 0.42,
    coherence_bias: float = 0.68,
) -> dict:
    from RYP_LANGUAGE import text_to_sam

    parts = split_text_into_segments(text, segments=segments)
    local_results = []
    for index, part in enumerate(parts):
        vector = normalize(text_to_sam(part))
        local_results.append(
            {
                "label": f"{label_prefix}_{index + 1}",
                "sam": vector,
                "dominant_axis": ["S", "A", "M"][int(np.argmax(vector))],
                "root_term": label_prefix,
                "operator_names": [],
                "source_text": part,
            }
        )

    stability = evaluate_projection_stability(
        local_results,
        relation_density=relation_density,
        attention_load=attention_load,
        coherence_bias=coherence_bias,
    )
    return {
        "local_projections": local_results,
        "global_projection": stability,
    }


def build_higher_order_nodes_from_text_files(
    file_specs: Iterable[dict],
    family_scheme: str = DEFAULT_FAMILY_SCHEME,
) -> list[dict]:
    nodes = []
    for index, spec in enumerate(file_specs):
        path = Path(spec["file_path"])
        text = path.read_text(encoding="utf-8")
        projection = build_global_projection_from_text(
            text,
            label_prefix=spec.get("label", path.stem.lower()),
            segments=int(spec.get("segments", 3)),
            relation_density=float(spec.get("relation_density", 0.60)),
            attention_load=float(spec.get("attention_load", 0.42)),
            coherence_bias=float(spec.get("coherence_bias", 0.68)),
        )
        node = build_higher_order_node(
            projection,
            order=int(spec["order"]),
            label=spec.get("label", path.stem.lower()),
            relation_mode=spec.get("relation_mode", "general"),
            family_scheme=family_scheme,
        )
        node["source_file"] = str(path)
        node["segments"] = int(spec.get("segments", 3))
        nodes.append(node)
    return nodes