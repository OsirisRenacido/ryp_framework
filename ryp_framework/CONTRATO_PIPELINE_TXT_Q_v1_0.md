# Contrato Pipeline TXT -> Q (RYP Framework v1.0)

## Objetivo

Definir el contrato estable para convertir TXT en artefactos Q sin depender del workspace historico completo.

## Comandos

- `ryp ingest-txt`
- `ryp run-cycle`
- `ryp run-all`
- `ryp quickstart`
- `ryp analyze`
- `ryp report`

Perfil academico en v1.0:

- `ryp ingest-txt --profile academico`
- `ryp run-all --profile academico`

Perfiles universales en v1.0:

- `general`
- `academico`
- `educativo`
- `editorial`
- `investigacion_aplicada`

## Entradas

- Carpeta TXT por defecto: `ryp_framework/workspace/01_ENTRADAS/TXT`
- Patron por defecto: `*.txt`

## Artefactos intermedios (descubrimientos)

- Carpeta: `ryp_framework/workspace/01_ENTRADAS/DESCUBRIMIENTOS`
- Salidas por TXT:
  - `<stem>_<hash>_DESCUBRIMIENTOS.json`
  - `<stem>_<hash>_DESCUBRIMIENTOS.md`

Campos clave del JSON:

- `timestamp`
- `source_txt`
- `source_hash`
- `metricas_globales`
- `propiedades_candidatas`
- `estado_validacion`
- `perfil_usuario`

## Artefactos finales Q

- Carpeta: `ryp_framework/workspace/04_SERIES_Q/Q_ENTRIES`
- Un bundle por Q (`Q001`, `Q002`, ...):
  - `Qxxx_READINESS.md`
  - `Qxxx_EVIDENCE.json`
  - `Qxxx_MANIFEST.json`
  - `Qxxx_DECISION.json`

## Reglas de estado

`run-cycle` aplica stage-gates:

- `DRAFT -> READY_FOR_REVIEW`
- `DRAFT -> UNDER_REVIEW`
- `DRAFT -> NEEDS_CURATION`
- `DRAFT/UNDER_REVIEW -> REJECTED` (si decision explicita)

## Idempotencia

- Ingestion TXT usa hash de contenido en el nombre del descubrimiento.
- Si el TXT no cambia, se reutiliza el mismo discovery path.
- Promocion evita duplicados por combinacion `source + candidate_key`.

## Criterios de compatibilidad

- No rompe flujo actual basado en discovery JSON preexistente.
- `run-all` solo orquesta: `ingest-txt` + `run-cycle`.
- `--profile academico` extiende el discovery con metricas adicionales sin romper consumidores actuales.
