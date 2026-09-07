# Software Design Document (SDD)
## Plataforma de Imputación y Análisis Multivariado de Datos

**Versión:** 1.0
**Metodología de Especificación:** Agile SDD / Behavior-Driven Development (BDD)

---

## 1. Visión General del Sistema
La aplicación web permite cargar datasets con valores faltantes (archivos `.xlsx` o `.csv`), analizar el impacto de los nulos en la estadística descriptiva y aplicar algoritmos de imputación matemática y de machine learning. El sistema devuelve un análisis comparativo y el dataset procesado listo para su uso.

## 2. Arquitectura Tecnológica
Para garantizar un despliegue ágil, escalabilidad y compatibilidad con el ecosistema de herramientas de desarrollo rápido, se establece el siguiente stack:
*   **Frontend & Hosting:** Aplicación construida en Next.js/React, alojada mediante despliegue serverless en **Vercel**.
*   **Backend & Data Processing:** Funciones serverless en **Python** integradas en el entorno. Utilización de `pandas` para ETL y `scikit-learn` para el modelado predictivo de imputación (KNNImputer).
*   **Capa de Persistencia (Opcional/Auditoría):** Base de datos relacional alojada en **Neon Tech** (PostgreSQL) para registrar metadatos de las operaciones, métricas de calidad de datos de los archivos procesados y logs de auditoría (sin almacenar los datos crudos por privacidad).

---

## 3. Especificaciones de Comportamiento (BDD / Gherkin)

### Feature: Análisis Descriptivo y Detección de Nulos
**Como** analista de datos
**Quiero** subir un archivo tabular con registros de ventas
**Para** visualizar qué porcentaje de la información está ausente y cómo afecta a la varianza y la media.

*   **Scenario:** Carga exitosa de dataset y reporte inicial
    *   **Given** que el usuario se encuentra en el dashboard de análisis
    *   **When** sube un archivo llamado "dataset_ventas.xlsx"
    *   **And** el sistema detecta columnas con valores vacíos (NaN)
    *   **Then** la interfaz debe mostrar una tabla resumen con el conteo total de filas, columnas y el porcentaje de nulos por columna.
    *   **And** debe renderizar las estadísticas descriptivas (Media, Varianza, Desviación Estándar, Cuartiles) omitiendo los nulos.

### Feature: Imputación de Datos Faltantes
**Como** analista de datos
**Quiero** seleccionar distintos métodos para rellenar los valores nulos
**Para** conservar el volumen del dataset sin distorsionar la distribución original.

*   **Scenario:** Relleno de datos utilizando KNN
    *   **Given** un dataset con nulos en la columna "monto" y columnas categóricas "categoria" y "region"
    *   **When** el usuario selecciona el método "Imputación Predictiva (KNN)" con K=5
    *   **Then** el backend en Python debe codificar las variables categóricas temporalmente
    *   **And** aplicar `KNNImputer(n_neighbors=5)` sobre los datos
    *   **And** la interfaz debe mostrar las nuevas estadísticas comparativas resaltando el cambio en la varianza.

### Feature: Exportación de Resultados
**Como** analista de datos
**Quiero** descargar el dataset con los datos imputados
**Para** continuar con la integración en mis pipelines o herramientas de BI.

*   **Scenario:** Descarga del archivo limpio
    *   **Given** que el proceso de imputación ha concluido exitosamente
    *   **When** el usuario hace clic en "Descargar Dataset Procesado"
    *   **Then** el sistema genera y sirve un archivo `.xlsx` o `.csv`
    *   **And** registra el evento (timestamp, filas procesadas, método utilizado) en la base de datos PostgreSQL en Neon Tech.

---

## 4. Estructura de Endpoints (API Vercel Serverless - Python)

### `POST /api/analyze`
*   **Propósito:** Recibir el archivo en crudo, parsearlo con pandas y devolver los metadatos y estadísticas omitiendo nulos.
*   **Payload:** `multipart/form-data` (archivo xlsx/csv).
*   **Respuesta (JSON):** Forma del dataset, diccionario de columnas con nulos, métricas base.

### `POST /api/impute`
*   **Propósito:** Aplicar la estrategia seleccionada sobre el dataset en memoria temporal.
*   **Payload:** `{ "file_reference": "temp_id", "method": "knn", "params": {"k": 5} }`
*   **Respuesta (JSON):** Nuevas métricas estadísticas (media, varianza) para la gráfica comparativa y enlace de descarga del blob final.

## 5. Diseño de Interfaz de Usuario (UI)
1.  **Zona de Dropzone:** Área principal para arrastrar y soltar el archivo.
2.  **Panel de Diagnóstico:** Tarjetas (cards) mostrando el % de completitud de los datos y advertencias si existen outliers extremos.
3.  **Selector de Estrategia:** Un menú desplegable o botones de selección (Mediana, Media, Agrupada, KNN).
4.  **Comparativa Visual:** Dos gráficos de distribución (histograma o boxplot), mostrando "Antes" vs "Después" de la imputación.
