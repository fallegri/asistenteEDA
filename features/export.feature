# language: es

Funcionalidad: Exportación de resultados
  Como analista de datos
  Quiero descargar el dataset con los datos imputados
  Para continuar con la integración en mis pipelines o herramientas de BI.

  Escenario: Descarga del archivo limpio en XLSX
    Dado que el proceso de imputación ha concluido exitosamente
    Cuando el usuario hace clic en "Descargar Dataset Procesado"
    Y selecciona formato XLSX
    Entonces el sistema genera y sirve un archivo .xlsx
    Y registra el evento (timestamp, filas procesadas, método utilizado) en la base de datos PostgreSQL en Neon Tech.

  Escenario: Descarga del archivo limpio en CSV
    Dado que el proceso de imputación ha concluido exitosamente
    Cuando el usuario hace clic en "Descargar Dataset Procesado"
    Y selecciona formato CSV
    Entonces el sistema genera y sirve un archivo .csv
    Y registra el evento de descarga en auditoría.

  Escenario: Validación de registro de auditoría
    Dado que un usuario ha completado un proceso de imputación
    Cuando consulta el log de auditoría
    Entonces debe ver un registro con: timestamp, user_id, método utilizado, filas procesadas, formato de descarga.