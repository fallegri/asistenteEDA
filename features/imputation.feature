# language: es

Funcionalidad: Imputación de datos faltantes
  Como analista de datos
  Quiero seleccionar distintos métodos para rellenar los valores nulos
  Para conservar el volumen del dataset sin distorsionar la distribución original.

  Escenario: Relleno de datos utilizando KNN
    Dado un dataset con nulos en la columna "monto" y columnas categóricas "categoria" y "region"
    Cuando el usuario selecciona el método "Imputación Predictiva (KNN)" con K=5
    Entonces el backend debe codificar las variables categóricas temporalmente
    Y aplicar KNNImputer(n_neighbors=5) sobre los datos
    Y la interfaz debe mostrar las nuevas estadísticas comparativas resaltando el cambio en la varianza.

  Escenario: Relleno de datos utilizando Media
    Dado un dataset con nulos en columnas numéricas
    Cuando el usuario selecciona el método "Media"
    Entonces el sistema debe calcular la media de cada columna (omitniedo nulos)
    Y rellenar los valores faltantes con dicha media
    Y mostrar la comparación de estadísticas antes/después.

  Escenario: Relleno de datos utilizando Mediana
    Dado un dataset con nulos y outliers en columnas numéricas
    Cuando el usuario selecciona el método "Mediana"
    Entonces el sistema debe calcular la mediana de cada columna
    Y rellenar los valores faltantes con la mediana (robusta a outliers)
    Y mostrar que la varianza se mantiene más estable que con media.

  Escenario: Relleno de datos utilizando Agrupada
    Dado un dataset con nulos y columnas categóricas de agrupación
    Cuando el usuario selecciona el método "Agrupada" por "categoria"
    Entonces el sistema debe calcular la media/mediana por grupo
    Y rellenar los nulos con el valor del grupo correspondiente.

  Escenario: Validación de parámetros KNN
    Dado que el usuario selecciona método KNN
    Cuando no proporciona el parámetro K
    Entonces el sistema debe usar K=5 por defecto
    Y si proporciona K=3, usar K=3.