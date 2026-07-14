# RYP Framework v1.0.0 (Universal Standalone Edition)

[![License: BUSL-1.1](https://img.shields.io/badge/License-BUSL--1.1-blue.svg)](LICENSE.md)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-green.svg)](#requisitos)
[![Engine: S-A-M Dynamics](https://img.shields.io/badge/Engine-S--A--M--Dynamics-orange.svg)](#-el-paradigma-s-a-m)

**RYP Framework** es la base autónoma y portable de **Realidades y Perspectivas (RYP)** diseñada para procesar corpus de texto plano (`.txt`), mapear su geometría conceptual en un espacio vectorial de tres dimensiones, y promover descubrimientos estructurados en "Bundles" auditables de la **Serie Q**.

Esta edición 1.0.0 Standalone empaqueta el pipeline completo para investigadores, académicos, editores y evaluadores sin requerir dependencias de servidores en la nube ni infraestructura corporativa propietaria.

---

## 🧠 El Paradigma S-A-M

A diferencia de los modelos de lenguaje (LLM) que operan probabilísticamente, el framework RYP deconstruye el discurso analizando la correlación y balance de tres polos de sentido:

1. **S (Similitud / Naturaleza / Flujo)**: Polaridad de la relación continua, el fondo ontológico y la narrativa pura.
2. **A (Acción / Energía / Cinética)**: Polaridad de la ejecución, el cambio pragmático y el verbo transitivo.
3. **M (Molde / Estructuración / Límite)**: Polaridad de la norma, la sintaxis, el soporte y la restricción formal.

---

## 📂 Arquitectura Standalone

El framework opera de forma local y portable mediante una estructura simplificada de carpetas:

- `ryp_framework/` — Paquete central de Python (contiene submódulos `sam`, `core`, `writer`, `cli`).
- `workspace/01_ENTRADAS/TXT/` — Directorio de entrada para corpus del usuario.
- `workspace/01_ENTRADAS/DESCUBRIMIENTOS/` — Reportes de descubrimientos curados (JSON/Markdown).
- `workspace/04_SERIES_Q/Q_ENTRIES/` — Registro inalterable de Bundles Q estructurados con su evidencia, preparación (Readiness) e historial auditable.

---

## 🚀 Instalación y Uso Rápido

### Requisitos

- Python 3.9 o superior
- Sistemas Operativos: Windows, Linux o macOS

### Instalación Local (Modo Standalone Portable)

1. Clona este repositorio público:

   ```bash
   git clone https://github.com/psirosalesf/ryp_framework.git
   cd ryp_framework
   ```

2. Instala el framework y sus dependencias en modo editable:

   ```bash
   pip install -e .
   ```
3. Activa la variable de ambiente Standalone:
   - PowerShell: `$env:RYP_FRAMEWORK_STANDALONE="1"`
   - Bash / macOS: `export RYP_FRAMEWORK_STANDALONE=1`
4. Copia tus documentos analíticos (`.txt`) en la carpeta:
   - `ryp_framework/workspace/01_ENTRADAS/TXT/`
5. Ejecuta el pipeline completo de análisis configurando el perfil de tu área de interés.
   - Presets disponibles: `general`, `academico`, `educativo`, `editorial`, `investigacion_aplicada`.
   - Ejemplo:

   ```bash
   ryp run-cycle --preset academico
   ```

## 🛠️ Comandos Clave del CLI

- `ryp status` — Comprueba la integridad del framework, versión y registro global.
- `ryp quickstart` — Ejecuta un ciclo de demostración rápido con el corpus cargado.
- `ryp run-cycle` — Aplica filtros de compuerta (Stage-gates) y promueve candidatos a Q sin duplicidad.
- `ryp report` — Compila estadísticas multidominales e indicadores de consistencia.

---

## ⚖️ Licenciamiento y Monetización Profesional

Este repositorio público se distribuye bajo la licencia Business Source License 1.1 (BUSL-1.1).

### ¿Qué significa esto?

- **Apertura y Uso No Comercial (Totalmente Gratuito):** Puedes compilar, bifurcar, estudiar y utilizar este software libremente para investigación científica, evaluación personal, docencia y uso académico.
- **Restricción Comercial Estricta:** Cualquier explotación económica directa, uso en entornos de producción de empresas o distribución como servicio SaaS de hosting comercial por terceros está estrictamente prohibida sin la previa firma de un contrato de licencia comercial con la empresa.
- **Transición a Software Libre:** El 13 de Julio de 2029 (3 años de exclusividad de mercado), la licencia de esta versión transicionará automáticamente a una licencia libre permisiva GNU General Public License v3.0 (GPL-3.0) o posterior.

Este repositorio público se constituye como la plataforma oficial de distribución, difusión y puesta en valor del RYP Framework, abriendo espacios formales de colaboración, co-creación y apoyo estratégico tanto para la investigación científica como para el desarrollo empresarial avanzado.

Como proyecto desarrollado de forma independiente por un equipo de una sola persona, esta iniciativa forma parte de un esfuerzo integral para dar a conocer la profunda filosofía cognitiva detrás de Realidades y Perspectivas (RYP). Asimismo, este espacio promueve activamente la validación y auditoría externa e imparcial de sus métricas, de sus resultados analíticos, del software de simulación y de su creador original, Joaquín Rosales Flores.

Contáctanos en: 📩 ryp.iacognitiva@gmail.com

Copyright © 2026 Realidades y Perspectivas (RYP) Cognitiva. Todos los derechos reservados.
