# RYP Framework v1.0.0 (Universal Standalone Edition)

*Plataforma oficial de distribución, difusión y puesta en valor de **Realidades y Perspectivas (RYP)**. Un espacio formal para la colaboración, co-creación y validación externa del sistema, su software y su creador original, **Joaquín Rosales Flores**.*

---

[![License: BUSL-1.1](https://img.shields.io/badge/License-BUSL--1.1-blue.svg)](LICENSE.md)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-green.svg)](#requirements)
[![Engine: S-A-M Dynamics](https://img.shields.io/badge/Engine-S--A--M--Dynamics-orange.svg)](#the-s-a-m-paradigm)
[![OSF: Public Science](https://img.shields.io/badge/OSF-Public%20Science-red.svg)](https://osf.io/7vzk4/)

**RYP Framework** es la base autónoma y portable del ecosistema **Realidades y Perspectivas (RYP)** diseñada para procesar corpus de texto plano (`.txt`), mapear su geometría conceptual en un espacio vectorial de tres dimensiones, y promover descubrimientos estructurados en "Bundles" auditables de la **Serie Q** sin depender de servidores en la nube.

Esta versión **v1.0.0 Universal** es mantenida de forma independiente como parte de un esfuerzo por dar a conocer la metodología y dar soporte especializado tanto a la investigación académica libre como al desarrollo estratégico empresarial.

---

## 🧠 El Paradigma S-A-M

A diferencia de los modelos de lenguaje (LLM) que operan sintáctica y probabilísticamente, el framework RYP deconstruye el discurso analizando la correlación y balance de tres polos de sentido:

1. **S (Similitud / Naturaleza / Flujo)**: Polaridad de la relación continua, el fondo ontológico y la narrativa pura.
2. **A (Acción / Energía / Cinética)**: Polaridad de la ejecución, el cambio pragmático y el verbo de acción.
3. **M (Molde / Estructuración / Límite)**: Polaridad de la norma, la sintaxis, el soporte y la restricción formal.

---

## 📂 Arquitectura Standalone

El framework opera de forma local y portable mediante una estructura simplificada de carpetas:

- `ryp_framework/` — Paquete central de Python (contiene submódulos `sam`, `core`, `writer`, `cli`, `automation`).
- `ryp_framework/workspace/01_ENTRADAS/TXT/` — Directorio de entrada para corpus del usuario.
- `ryp_framework/workspace/01_ENTRADAS/DESCUBRIMIENTOS/` — Reportes de descubrimientos curados (JSON/Markdown).
- `ryp_framework/workspace/04_SERIES_Q/Q_ENTRIES/` — Registro inalterable de Bundles Q estructurados con su evidencia, preparación (Readiness) e historial auditable.

---

## 🚀 Instalación y Uso Rápido

### Requisitos
*   Python 3.9 o superior
*   Sistemas Operativos: Windows, Linux o macOS

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
   *   **PowerShell**: `$env:RYP_FRAMEWORK_STANDALONE="1"`
   *   **Bash / macOS**: `export RYP_FRAMEWORK_STANDALONE=1`

4. Copia tus documentos analíticos (`.txt`) en la carpeta:
   `ryp_framework/workspace/01_ENTRADAS/TXT/`

5. Ejecuta el pipeline completo de análisis configurando el perfil de tu área de interés:
   ```bash
   ryp run-all --pattern "*.txt" --profile general
   ```
   *Presets disponibles: `general`, `academico`, `educativo`, `editorial`, `investigacion_aplicada`.*

---

## 🛠️ Comandos Clave del CLI

*   `ryp status` — Comprueba la integridad del framework, versión y registro global.
*   `ryp quickstart` — Ejecuta un ciclo de demostración rápido con el corpus cargado.
*   `ryp run-cycle` — Aplica filtros de compuerta (Stage-gates) y promueve candidatos a Q sin duplicidad.
*   `ryp report` — Compila estadísticas multidominales e indicadores de consistencia.

---

## ⚙️ Instancias de Colaboración y Validación Colectiva

Dado que este ecosistema representa el desarrollo e investigación independiente de un equipo de **una sola persona**, abrimos activamente puertas profesionales en dos vertientes:

*   **Para el Ámbito de Investigación**: Validación, testeo por pares, réplica experimental del motor S-A-M y auditoría externa de las Series Q. Contamos con documentación científica abierta alojada en el Open Science Framework: [OSF Public Registry](https://osf.io/7vzk4/).
*   **Para el Ámbito Empresarial**: Soporte de consultoría estratégica, desarrollo de integraciones personalizadas complejas o acoplamientos con nuestro Enjambre de Agentes privados y la interfaz rica del Cristal Conversacional 3D de producción.

---

## ⚖️ Licenciamiento y Protección Comercial

Este repositorio público se distribuye bajo la licencia **Business Source License 1.1 (BUSL-1.1)**. 

*   **Uso No Comercial (Totalmente Gratuito)**: Puedes compilar, bifurcar, estudiar y utilizar este software de manera 100% gratuita para investigación científica, evaluación personal, docencia y uso académico.
*   **Restricción Comercial Estricta**: Cualquier explotación económica directa, uso en entornos de producción de empresas o distribución como servicio SaaS de hosting comercial por terceros está **estrictamente prohibida** sin la previa firma de un contrato de licencia comercial con la empresa.
*   **Transición a Software Libre**: El 13 de Julio de 2029 (3 años de exclusividad de mercado), la licencia de esta versión transicionará automáticamente a una licencia libre permisiva **GNU General Public License v3.0 (GPL-3.0)** o posterior.

---

## 📯 Contacto Oficial y Redes

*   **Sitio Web**: [rypiacognitiva.cl](https://rypiacognitiva.cl)
*   **OSF Público**: [Open Science Framework Profile (7vzk4)](https://osf.io/7vzk4/)
*   **Correos de Soporte y Licencias Comerciales**: 
    *   📧 `contacto@rypiacognitiva.cl`
    *   📧 `ryp.iacognitiva@gmail.com`

---
**Copyright © 2026 Realidades y Perspectivas (RYP) Cognitiva. Todos los derechos reservados.**
