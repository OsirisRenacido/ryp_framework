# Modelo creado por Joaquin Rosales Flores, psicologo.
# =====================================================
# RYP LANGUAGE MODULE - VERSION FINAL ESTABLE
# Lenguaje → SAM → Dinámica
# =====================================================

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
import unicodedata
import numpy as np

from ryp_framework.utils.paths import (
    get_documentation_original_path,
    get_framework_root,
    get_private_assets_root,
    get_resource_path,
    get_user_data_path,
    is_standalone_mode,
)


DEFAULT_LEXICON_FILENAME = "RYP_LEXICON.json"
PACKAGE_LEXICON_PATH = get_framework_root() / "resources" / "RYP_LEXICON.json"
LEXICON_BACKUP_DIRNAME = "lexicon_backups"
LEXICON_BUNDLE_VERSION = 2


def _default_known_lexicon_regimes():
    if is_standalone_mode():
        return {
            "acotado": {
                "path": os.fspath(PACKAGE_LEXICON_PATH),
                "description": "lexicon base empaquetado para modo standalone",
            },
        }
    return {
        "acotado": {
            "path": os.fspath(PACKAGE_LEXICON_PATH if PACKAGE_LEXICON_PATH.exists() else get_resource_path(DEFAULT_LEXICON_FILENAME)),
            "description": "lexicon curado base actual",
        },
        "diagnostico_dsm": {
            "path": os.fspath(get_documentation_original_path("RYP_LEXICON_DSM_PREVIEW.json")),
            "description": "expansion preview centrada en lenguaje DSM",
        },
        "terapeutico_ampliado": {
            "path": os.fspath(get_documentation_original_path("RYP_LEXICON_BOOKS_PREVIEW_TERAPIA.json")),
            "description": "expansion preview desde libros de terapia",
        },
    }


def _normalize_regime_map(regimes):
    normalized = {}
    for regime_name, regime_payload in (regimes or {}).items():
        if isinstance(regime_payload, dict):
            path = regime_payload.get("path") or regime_payload.get("lexicon_file") or ""
            description = regime_payload.get("description", "")
        else:
            path = regime_payload
            description = ""
        normalized[str(regime_name)] = {
            "path": os.fspath(path) if path else "",
            "description": str(description or ""),
        }
    return normalized


def is_structured_lexicon_payload(payload):
    return isinstance(payload, dict) and isinstance(payload.get("entries"), dict)


def build_lexicon_bundle(entries, metadata=None, regimes=None, active_regime=None, source_path=None):
    metadata = dict(metadata or {})
    bundle_regimes = _default_known_lexicon_regimes()
    bundle_regimes.update(_normalize_regime_map(regimes))
    source_path = os.fspath(source_path) if source_path else metadata.get("source_path", "")
    metadata.update({
        "bundle_version": int(metadata.get("bundle_version", LEXICON_BUNDLE_VERSION)),
        "entry_count": len(entries),
        "source_path": source_path,
        "default_filename": metadata.get("default_filename", DEFAULT_LEXICON_FILENAME),
        "updated_at": metadata.get("updated_at") or datetime.now().isoformat(),
    })
    active_regime = active_regime or metadata.get("active_regime") or "acotado"
    metadata["active_regime"] = active_regime
    return {
        "metadata": metadata,
        "regimes": bundle_regimes,
        "entries": entries,
    }


def _coerce_lexicon_bundle(raw_payload, source_path):
    if is_structured_lexicon_payload(raw_payload):
        bundle = build_lexicon_bundle(
            raw_payload["entries"],
            metadata=raw_payload.get("metadata"),
            regimes=raw_payload.get("regimes"),
            active_regime=(raw_payload.get("metadata") or {}).get("active_regime"),
            source_path=source_path,
        )
        return bundle
    entries = raw_payload if isinstance(raw_payload, dict) else {}
    return build_lexicon_bundle(entries, metadata={"schema": "flat-legacy"}, source_path=source_path)


def _extract_lexicon_entries(bundle):
    return dict(bundle.get("entries") or {})

# =====================================================
# 1. CARGA SEGURA DEL LEXICON
# =====================================================

def get_lexicon_path(filename=DEFAULT_LEXICON_FILENAME):
    candidate_path = Path(filename)
    if candidate_path.is_absolute() and candidate_path.exists():
        return os.fspath(candidate_path)
    if candidate_path.exists():
        return os.fspath(candidate_path.resolve())
    if filename == DEFAULT_LEXICON_FILENAME and PACKAGE_LEXICON_PATH.exists():
        return os.fspath(PACKAGE_LEXICON_PATH)
    if is_standalone_mode():
        bundled_candidate = get_framework_root() / "resources" / filename
        if bundled_candidate.exists():
            return os.fspath(bundled_candidate)
    user_path = get_user_data_path(filename)
    if user_path.exists():
        return os.fspath(user_path)
    private_path = get_private_assets_root(create=False) / filename
    if private_path.exists():
        return os.fspath(private_path)
    return os.fspath(get_resource_path(filename))


def resolve_lexicon_input(lexicon_file=None, lexicon_regime=None):
    if lexicon_regime:
        known_regimes = get_known_lexicon_regimes()
        if lexicon_regime not in known_regimes:
            raise ValueError(
                f"Regimen de lexicon desconocido: {lexicon_regime}. "
                f"Usa uno de {sorted(known_regimes)}"
            )
        return known_regimes[lexicon_regime]["path"]

    if lexicon_file:
        return get_lexicon_path(lexicon_file)

    return get_lexicon_path(DEFAULT_LEXICON_FILENAME)


def get_lexicon_backup_dir():
    return os.fspath(get_user_data_path(LEXICON_BACKUP_DIRNAME, create_parent=False))


def load_lexicon_bundle(filename=DEFAULT_LEXICON_FILENAME):
    path = get_lexicon_path(filename)

    if not os.path.exists(path):
        print("\nWARNING: No se encontro RYP_LEXICON.json")
        return build_lexicon_bundle({}, metadata={"schema": "missing"}, source_path=path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_payload = json.load(f)
            bundle = _coerce_lexicon_bundle(raw_payload, path)
            print(f"Lexicon cargado: {len(bundle['entries'])} palabras")
            return bundle
    except Exception as e:
        print("Error cargando JSON:", e)
        return build_lexicon_bundle({}, metadata={"schema": "error", "error": str(e)}, source_path=path)


def load_lexicon(filename=DEFAULT_LEXICON_FILENAME):
    bundle = load_lexicon_bundle(filename)
    return _extract_lexicon_entries(bundle)

LEXICON_BUNDLE = load_lexicon_bundle()
SAM_DICT = _extract_lexicon_entries(LEXICON_BUNDLE)
LEXICON_METADATA = dict(LEXICON_BUNDLE.get("metadata") or {})
LEXICON_REGIMES = _normalize_regime_map(LEXICON_BUNDLE.get("regimes"))
ACTIVE_LEXICON_REGIME = LEXICON_METADATA.get("active_regime", "acotado")
LEXICON_LOOKUP_MODE = "mixed"
VALID_LOOKUP_MODES = {"exact", "normalized", "mixed"}
SPANISH_STOPWORDS = {
    "a", "al", "ante", "asi", "así", "bajo", "cabe", "como", "con", "contra", "de", "del", "desde", "durante",
    "el", "ella", "ellas", "ello", "ellos", "en", "entre", "es", "esa", "ese", "eso",
    "e", "esta", "está", "estas", "este", "esto", "ha", "hacia", "la", "las", "le", "les",
    "lo", "los", "mas", "más", "mi", "mis", "o", "para", "pero", "por", "que", "se",
    "segun", "según", "si", "siempre", "sin", "sino", "sobre", "su", "sus", "toda", "todas", "todo", "todos",
    "tras", "tu", "un", "una", "uno", "unos", "unas", "y"
}
ENGLISH_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for", "from",
    "has", "have", "if", "in", "into", "is", "it", "its", "of", "on", "or", "that",
    "the", "their", "there", "these", "this", "those", "to", "was", "were", "with",
}
STOPWORDS = SPANISH_STOPWORDS | ENGLISH_STOPWORDS
TOKEN_REPLACEMENTS = {
    "\n": " ",
    "\t": " ",
    "\r": " ",
    ",": " ",
    ".": " ",
    ";": " ",
    ":": " ",
    "¿": " ",
    "?": " ",
    "¡": " ",
    "!": " ",
    "(": " ",
    ")": " ",
    "[": " ",
    "]": " ",
    "{": " ",
    "}": " ",
    '"': " ",
    "'": " ",
    "“": " ",
    "”": " ",
    "‘": " ",
    "’": " ",
    "«": " ",
    "»": " ",
    "/": " ",
    "\\": " ",
    "|": " ",
    "_": " ",
    "-": " ",
    "–": " ",
    "—": " ",
    "…": " ",
}

# =====================================================
# 2. UTILIDADES
# =====================================================

def normalize(x):
    x = np.maximum(x, 0)
    s = np.sum(x)
    if s == 0:
        return np.array([1/3, 1/3, 1/3])
    return x / s


def infer_sam_from_metadata(entry):
    if not isinstance(entry, dict):
        return np.array([1 / 3, 1 / 3, 1 / 3], dtype=float)

    # Legacy-safe: some enriched entries only expose category/domain metadata.
    category = str(entry.get("category", "")).strip().upper()
    domain = str(entry.get("domain", "")).strip().lower()

    if category == "S":
        return np.array([0.70, 0.15, 0.15], dtype=float)
    if category == "A":
        return np.array([0.15, 0.70, 0.15], dtype=float)
    if category == "M":
        return np.array([0.15, 0.15, 0.70], dtype=float)

    if "psico" in domain or "social" in domain or "relac" in domain:
        return np.array([0.20, 0.60, 0.20], dtype=float)
    if "comput" in domain or "mat" in domain or "formal" in domain:
        return np.array([0.20, 0.20, 0.60], dtype=float)
    if "bio" in domain or "salud" in domain or "cuerpo" in domain:
        return np.array([0.45, 0.30, 0.25], dtype=float)

    return np.array([1 / 3, 1 / 3, 1 / 3], dtype=float)


def extract_entry_sam(entry):
    if isinstance(entry, dict):
        if "sam" in entry:
            return np.array(entry["sam"], dtype=float)
        return infer_sam_from_metadata(entry)
    return np.array(entry, dtype=float)


def get_entry_metadata(term, entry):
    vector = extract_entry_sam(entry)
    dominant = ["S", "A", "M"][int(np.argmax(vector))]
    aliases = []
    if isinstance(entry, dict):
        raw_aliases = entry.get("aliases", [])
        aliases = [str(alias).strip().lower() for alias in raw_aliases if str(alias).strip()]
        return {
            "term": term,
            "sam": vector,
            "category": entry.get("category", dominant),
            "description": entry.get("description", ""),
            "aliases": aliases,
        }
    return {
        "term": term,
        "sam": vector,
        "category": dominant,
        "description": "",
        "aliases": [],
    }


def normalize_lexicon_entry(term, entry):
    metadata = get_entry_metadata(term, entry)
    aliases = []
    seen_aliases = {term.lower()}
    for alias in metadata["aliases"]:
        normalized_alias = alias.lower().strip()
        if normalized_alias and normalized_alias not in seen_aliases:
            aliases.append(normalized_alias)
            seen_aliases.add(normalized_alias)

    normalized_entry = {
        "sam": normalize(metadata["sam"]).tolist(),
        "category": metadata["category"],
        "description": metadata["description"],
    }
    if aliases:
        normalized_entry["aliases"] = aliases
    return normalized_entry


def normalize_full_lexicon(lexicon):
    normalized_lexicon = {}
    for term, entry in lexicon.items():
        normalized_lexicon[term.lower().strip()] = normalize_lexicon_entry(term, entry)
    return normalized_lexicon


def strip_diacritics(text):
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_token(token):
    return strip_diacritics(token.lower().strip())


def build_normalized_lexicon(lexicon):
    normalized_lexicon = {}
    for key, value in lexicon.items():
        normalized_key = normalize_token(key)
        if normalized_key not in normalized_lexicon:
            normalized_lexicon[normalized_key] = value
    return normalized_lexicon


def build_alias_lexicons(lexicon):
    exact_alias_lexicon = {}
    normalized_alias_lexicon = {}

    for term, entry in lexicon.items():
        metadata = get_entry_metadata(term, entry)
        for alias in metadata["aliases"]:
            exact_alias_lexicon.setdefault(alias, (term, entry))
            normalized_alias = normalize_token(alias)
            normalized_alias_lexicon.setdefault(normalized_alias, (term, entry))

    return exact_alias_lexicon, normalized_alias_lexicon


def set_lookup_mode(mode):
    global LEXICON_LOOKUP_MODE
    if mode not in VALID_LOOKUP_MODES:
        raise ValueError(f"Modo invalido: {mode}. Usa uno de {sorted(VALID_LOOKUP_MODES)}")
    LEXICON_LOOKUP_MODE = mode


def get_lookup_mode():
    return LEXICON_LOOKUP_MODE


def get_lexicon_bundle():
    return {
        "metadata": dict(LEXICON_METADATA),
        "regimes": _normalize_regime_map(LEXICON_REGIMES),
        "entries": dict(SAM_DICT),
    }


def get_lexicon_metadata():
    return dict(LEXICON_METADATA)


def get_active_lexicon_regime():
    return ACTIVE_LEXICON_REGIME


def get_known_lexicon_regimes():
    return _normalize_regime_map(LEXICON_REGIMES)


def describe_lexicon_architecture():
    return {
        "bundle_version": LEXICON_METADATA.get("bundle_version", 1),
        "entry_count": len(SAM_DICT),
        "active_regime": ACTIVE_LEXICON_REGIME,
        "lookup_mode": LEXICON_LOOKUP_MODE,
        "regimes": get_known_lexicon_regimes(),
        "source_path": LEXICON_METADATA.get("source_path", get_lexicon_path(DEFAULT_LEXICON_FILENAME)),
    }


NORMALIZED_SAM_DICT = build_normalized_lexicon(SAM_DICT)
EXACT_ALIAS_SAM_DICT, NORMALIZED_ALIAS_SAM_DICT = build_alias_lexicons(SAM_DICT)


def reload_lexicon(filename=DEFAULT_LEXICON_FILENAME):
    global LEXICON_BUNDLE, SAM_DICT, LEXICON_METADATA, LEXICON_REGIMES, ACTIVE_LEXICON_REGIME
    global NORMALIZED_SAM_DICT, EXACT_ALIAS_SAM_DICT, NORMALIZED_ALIAS_SAM_DICT
    LEXICON_BUNDLE = load_lexicon_bundle(filename)
    SAM_DICT = _extract_lexicon_entries(LEXICON_BUNDLE)
    LEXICON_METADATA = dict(LEXICON_BUNDLE.get("metadata") or {})
    LEXICON_REGIMES = _normalize_regime_map(LEXICON_BUNDLE.get("regimes"))
    ACTIVE_LEXICON_REGIME = LEXICON_METADATA.get("active_regime", "acotado")
    NORMALIZED_SAM_DICT = build_normalized_lexicon(SAM_DICT)
    EXACT_ALIAS_SAM_DICT, NORMALIZED_ALIAS_SAM_DICT = build_alias_lexicons(SAM_DICT)
    return SAM_DICT


def save_lexicon(lexicon, filename=DEFAULT_LEXICON_FILENAME):
    path = get_lexicon_path(filename)
    normalized_lexicon = normalize_full_lexicon(lexicon)
    existing_payload = None
    if os.path.exists(path):
        backup_dir = get_lexicon_backup_dir()
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_name)
        with open(path, "r", encoding="utf-8") as source, open(backup_path, "w", encoding="utf-8") as target:
            existing_text = source.read()
            target.write(existing_text)
        try:
            existing_payload = json.loads(existing_text)
        except json.JSONDecodeError:
            existing_payload = None

    with open(path, "w", encoding="utf-8") as handle:
        if is_structured_lexicon_payload(existing_payload):
            existing_metadata = dict(existing_payload.get("metadata") or {})
            existing_metadata["updated_at"] = datetime.now().isoformat()
            structured_payload = build_lexicon_bundle(
                normalized_lexicon,
                metadata=existing_metadata,
                regimes=existing_payload.get("regimes"),
                active_regime=existing_metadata.get("active_regime"),
                source_path=path,
            )
            json.dump(structured_payload, handle, ensure_ascii=False, indent=2)
        else:
            json.dump(normalized_lexicon, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return reload_lexicon(filename)

# =====================================================
# 3. TOKENIZACIÓN
# =====================================================

def tokenize(text):
    text = text.lower()
    for source, target in TOKEN_REPLACEMENTS.items():
        text = text.replace(source, target)
    return [token for token in text.split() if token and token not in STOPWORDS]


def lookup_lexicon_entry(word):
    exact_word = word.lower()
    normalized_word = normalize_token(word)

    if LEXICON_LOOKUP_MODE in {"exact", "mixed"}:
        if exact_word in SAM_DICT:
            return exact_word, SAM_DICT[exact_word], "exact"
        if exact_word in EXACT_ALIAS_SAM_DICT:
            canonical_term, entry = EXACT_ALIAS_SAM_DICT[exact_word]
            return canonical_term, entry, "exact-alias"

    if LEXICON_LOOKUP_MODE in {"normalized", "mixed"}:
        if normalized_word in NORMALIZED_SAM_DICT:
            return normalized_word, NORMALIZED_SAM_DICT[normalized_word], "normalized"
        if normalized_word in NORMALIZED_ALIAS_SAM_DICT:
            canonical_term, entry = NORMALIZED_ALIAS_SAM_DICT[normalized_word]
            return canonical_term, entry, "normalized-alias"

    return None, None, "noise"


def _deterministic_noise_for_token(token):
    """Return a stable pseudo-random noise vector for unknown tokens."""
    normalized = normalize_token(token or "")
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    seed = int(digest[:16], 16)
    rng = np.random.default_rng(seed)
    return rng.uniform(-0.05, 0.05, 3)

# =====================================================
# 4. PALABRA → SAM
# =====================================================

def word_to_sam(word):
    _canonical_term, entry, _source = lookup_lexicon_entry(word)
    if entry is not None:
        return extract_entry_sam(entry)

    base = np.array([1/3, 1/3, 1/3])
    noise = _deterministic_noise_for_token(word)
    return normalize(base + noise)

# =====================================================
# 5. TEXTO → VECTOR SAM
# =====================================================

def text_to_sam(text):
    tokens = tokenize(text)
    if len(tokens) == 0:
        return np.array([1/3, 1/3, 1/3])
    vectors = np.array([word_to_sam(w) for w in tokens])
    mean_vec = np.mean(vectors, axis=0)
    return normalize(mean_vec)

# =====================================================
# 6. TEXTO → TRAYECTORIA (PALABRA A PALABRA)
# =====================================================

def text_to_trajectory(text):
    tokens = tokenize(text)
    traj = []
    for w in tokens:
        traj.append(word_to_sam(w))
    if len(traj) == 0:
        traj.append(np.array([1/3, 1/3, 1/3]))
    return np.array(traj)

# =====================================================
# 7. ENTROPÍA
# =====================================================

def entropy(x):
    return -np.sum(x * np.log(x + 1e-8))

# =====================================================
# 8. SIMULACIÓN DESDE TEXTO (FIX CORRECTO)
# =====================================================

def simulate_text(text, steps=100):
    """
    Convierte texto → SAM → ejecuta simulación.
    """
    x0 = text_to_sam(text)
    from ryp_framework.core._core import simulate
    traj = simulate(initial_state=x0, steps_override=steps)
    return traj

# =====================================================
# 9. DEBUG
# =====================================================

if __name__ == "__main__":
    print("RYP_LANGUAGE cargado")