# language: es

Funcionalidad: Análisis descriptivo y detección de nulos
  Como analista de datos
  Quiero subir un archivo tabular con registros de ventas
  Para visualizar qué porcentaje de la información está ausente y cómo afecta a la varianza y la media.

  Escenario: Carga exitosa de dataset y reporte inicial
    Dado que el usuario se encuentra en el dashboard de análisis
    Cuando sube un archivo llamado "dataset_ventas.xlsx"
    Y el sistema detecta columnas con valores vacíos (NaN)
    Entonces la interfaz debe mostrar una tabla resumen con el conteo total de filas, columnas y el porcentaje de nulos por columna
    Y debe renderizar las estadísticas descriptivas (Media, Varianza, Desviación Estándar, Cuartiles) omitiendo los nulos.

  Escenario: Carga de archivo CSV con nulos
    Dado que el usuario tiene un archivo CSV con datos de ventas
    Cuando sube el archivo "ventas.csv"
    Y el archivo contiene 1000 filas y 10 columnas
    Y 3 columnas tienen valores nulos
    Entonces el sistema debe mostrar el porcentaje de nulos por cada columna afectada
    Y las estadísticas descriptivas deben calcularse solo con valores no nulos.

  Escenario: Archivo sin nulos
    Dado un archivo completo sin valores faltantes
    Cuando el usuario lo sube
    Entonces el sistema debe reportar 0% de nulos en todas las columnas
    Y las estadísticas deben coincidir con el dataset completo.