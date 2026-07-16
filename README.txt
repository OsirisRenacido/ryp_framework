# RYP Framework v1.0.0 (Version Universal)

RYP Framework es la base autonoma de Realidades y Perspectivas para convertir corpus TXT en descubrimientos estructurados y bundles Serie Q auditables.

Esta version 1.0.0 incorpora una capa de usuario universal con presets por perfil y comandos de experiencia rapida para distintos tipos de usuarios.

## Objetivo de esta version

- Ejecutar un pipeline reproducible y compartible sin depender del workspace historico completo.
- Entregar artefactos listos para usuarios generales y tecnicos (resumen + evidencia auditables).
- Mantener idempotencia en re-ejecuciones para evitar duplicados.

## Requisitos

- Python 3.9+
- Windows, Linux o macOS

## Instalacion

Desde la raiz del repositorio:

```bash
git clone https://github.com/OsirisRenacido/ryp_framework.git
cd ryp_framework
pip install -e .
```

En PowerShell (recomendado para modo standalone):

```powershell
$env:RYP_FRAMEWORK_STANDALONE="1"
```

## Inicio rapido (universal)

1. Copia tus TXT en:

- `ryp_framework/workspace/01_ENTRADAS/TXT`

1. Ejecuta el pipeline completo con el perfil que necesites:

```bash
ryp run-all --pattern "*.txt" --profile general
```

1. Revisa resultados:

- Descubrimientos JSON/MD:
  - `ryp_framework/workspace/01_ENTRADAS/DESCUBRIMIENTOS`
- Bundles Q:
  - `ryp_framework/workspace/04_SERIES_Q/Q_ENTRIES/Qxxx/`
- Registro global:
  - `ryp_framework/workspace/11_OPERACION/runtime/q_series_registry.json`

## Comandos clave

```bash
ryp status
ryp quickstart --profile educativo
ryp ingest-txt --pattern "*.txt" --profile academico
ryp run-cycle
ryp run-all --pattern "*.txt" --profile editorial
ryp analyze --profile investigacion_aplicada
ryp report --profile general
```

## Presets universales disponibles

- `general`
- `academico`
- `educativo`
- `editorial`
- `investigacion_aplicada`

## Que agrega cada preset

Campos en `metricas_globales` segun perfil:

- `academic_signal_score`
- `citation_density`
- `method_coverage`
- `argumentation_index`
- `paragraph_pressure`
- `educational_signal_score`
- `didactic_density`
- `pedagogic_flow`
- `editorial_signal_score`
- `style_signal`
- `readability_signal`
- `applied_signal_score`
- `empirical_density`
- `operational_resolution`

Candidatos especificos por perfil:

- `subcapa_argumentacion_metodologica`
- `subcapa_claridad_pedagogica`
- `subcapa_coherencia_editorial`
- `subcapa_evidencia_operativa`

Reportes por perfil:

- El discovery markdown incorpora resumen contextual por perfil.
- `ryp report` genera reporte universal en `workspace/11_OPERACION/runtime/reports`.

## Contrato operativo v1.0

- Ingesta TXT deterministica con hash de contenido.
- Promocion a Q sin duplicados (`source + candidate_key`).
- Stage-gates aplicados por `run-cycle`.
- `run-all` como orquestacion de `ingest-txt + run-cycle`.

Consulta el contrato formal en:

- [CONTRATO_PIPELINE_TXT_Q_v1_0.md](CONTRATO_PIPELINE_TXT_Q_v1_0.md)

## Estado y alcance

v1.0.0 cubre un flujo autonomo, testeado y documentado para produccion academica inicial.

Alcance actual:

- Pipeline TXT -> Q estable.
- Idempotencia verificada.
- Presets universales integrados por CLI.
- Comandos `quickstart`, `analyze` y `report`.

Limitacion actual:

- El desacople total de todos los puentes legacy avanzados sigue como linea de evolucion posterior.

## Validacion incluida

Suite de contrato ejecutada:

- `ryp_framework/tests/test_pipeline_contract.py`
- Resultado esperado: `7/7 OK`

## Referencias

- Quickstart: [QUICKSTART_RYP_FRAMEWORK_v1_0.md](QUICKSTART_RYP_FRAMEWORK_v1_0.md)
- Plan universal: [UNIVERSAL_47_PUNTOS_v1_0.md](UNIVERSAL_47_PUNTOS_v1_0.md)
- ZIP instalable: [GUIA_ZIP_INSTALABLE_v1_0.md](GUIA_ZIP_INSTALABLE_v1_0.md)
- Workspace interno: [workspace/README.md](workspace/README.md)
