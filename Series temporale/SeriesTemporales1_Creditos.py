# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 10:04:03 2023

@author: borja
"""

import pandas as pd
import os

os.chdir(r"C:\Users\borja\Documents\UNAV\Master2023")
# Cargamos los datos
datos = pd.read_csv("DatosCreditosPersonales.csv")

del (datos["Unnamed: 0"])
# Pasamos la fecha a formato fecha
datos["Month-Year"] = pd.to_datetime(datos["Month-Year"], format="%b-%y")

# Pasamos la fecha al indice
datos.index = datos["Month-Year"]
del (datos["Month-Year"])

print(datos.head())

# Graficamos la serie original
import matplotlib.pyplot as plt
import seaborn as sns

plt.plot(datos)


# Observamos que existe la serie no es estacionaria:
    # La media es creciente.
    # La varianza es creciete


# Procedemos a calcular el numero de diferencias
import pmdarima

# Respecto a la observacion anterior
pmdarima.arima.ndiffs(datos)

# Estacionalmente con estacionalidad anual.
pmdarima.arima.nsdiffs(datos, m = 12)


# Vemos que en ambos casos recomienda la diferenciacion.
# Inicamos la diferenciacion respecto a la observacion anterior.

datosdiff = pmdarima.utils.diff(datos,lag = 1, differences= 1)

# Graficamos los datos diferenciados.
plt.plot(datosdiff)

# Se soluciona el problema de la media (se vuelve mas constante)
# Pero no el de la varianza, aumenta con el tiempo.

# Determinamos si hay que volver a diferenciarlo
pmdarima.arima.ndiffs(datosdiff)

# Indica que no pero lo comprobamos
datosdiff2 = pmdarima.utils.diff(datosdiff,lag = 1, differences= 1)

# Graficamos
plt.plot(datosdiff2)

# Vemos que el problema no se soluciona

# Pasamos a probar la via estacional.
datosdiff_Est = pmdarima.utils.diff(datos,lag = 12, differences= 1)

# Graficamos.
plt.plot(datosdiff_Est)

# Vemos que mejora pero no es algo claro.

# Vemos si hay que diferenciar respecto a la anteior y estacionalmente.
pmdarima.arima.ndiffs(datosdiff_Est)
pmdarima.arima.nsdiffs(datosdiff_Est, m = 12)

# Recomienda diferenciarlos respecto a la anterior.
datosdiff_Est2 = pmdarima.utils.diff(datosdiff_Est,lag = 1, differences= 1)

# Graficamos
plt.plot(datosdiff_Est2)

# Parece que mejora el problema de la varianza pero se aprecian 3 zonas.


# Probamos tomando logaritmos.
import numpy as np

datos["Creditos_Personales"] = datos["Creditos_Personales"].astype(float)
Log_Datos = pd.DataFrame(np.log(datos["Creditos_Personales"]))

# Graficamos.
plt.plot(Log_Datos)

# Vemos que los logaritmos solos no solucionan nada.

# Vemos si hay que diferenciar
pmdarima.arima.ndiffs(Log_Datos)

# Procedemos a diferenciar.
Log_Datos_Dif = pd.DataFrame(pmdarima.utils.diff(Log_Datos,lag = 1, differences= 1))

# Graficamos
plt.plot(Log_Datos_Dif)

# Parece que es el camino correcto.


# Continuamos analizando la serie y procedemos a descomponerla y graficarla.

from statsmodels.tsa.seasonal import seasonal_decompose

# De manera aditiva
SerieDescompuesta = seasonal_decompose(datos, model='additive')

# La graficamos.
SerieDescompuesta.plot(observed=True, seasonal=True, trend=True, resid=True, weights=False)

# Vemos la difernecia con los ultimos datos.
datos2 = datos.iloc[96:144,]
SerieDescompuesta2 = seasonal_decompose(datos2, model='additive')
SerieDescompuesta2.plot(observed=True, seasonal=True, trend=True, resid=True, weights=False)

# Calculamos la Serie sin la componente estacional
SerieNoEstacional = datos["Creditos_Personales"] - SerieDescompuesta.seasonal

# La graficamos.
plt.plot(SerieNoEstacional)



# Calculamos la serie sin ctendencia
SerieSinTendencia = datos["Creditos_Personales"] - SerieDescompuesta.trend

Residuos = datos["Creditos_Personales"] - SerieDescompuesta.seasonal - SerieDescompuesta.trend
# La graficamos.
plt.plot(SerieSinTendencia)

# Eliminamos la componente aleatoria.
SerieSinResiduos = datos["Creditos_Personales"] - SerieDescompuesta.resid

# La graficamos.
plt.plot(SerieSinResiduos)


# La decomponemos de forma multiplicativa
# De manera aditiva
SerieDescompuestaMult = seasonal_decompose(datos, model='multiplicative')

# La graficamos.
SerieDescompuestaMult.plot(observed=True, seasonal=True, trend=True, resid=True, weights=False)



# Procedemos a suavizar la serie buscando algo mas armonico

# Suavizado basado en medias moviles
datos['mov_avg'] = datos['Creditos_Personales'].rolling(4).mean()
# Graficamos esta nueva serie
plt.plot(datos)

# La eliminamos
del (datos['mov_avg'])



# Tambien podemos realizar un suavizado exponencial
from statsmodels.tsa.holtwinters import ExponentialSmoothing as HWES

model = HWES(datos, seasonal_periods=12, trend='add', seasonal='add').fit()

# Graficamos el suavizado expoencial
datos["HWES"] = model.fittedvalues
plt.plot(datos)

# La eliminamos 
del (datos["HWES"])

# Procedemos a analizar la estariedad de la serie original y de la logaritmica

# ADF
from statsmodels.tsa.stattools import adfuller

# H0: No estacionario (raiz unitaria)


ADF = adfuller(datos["Creditos_Personales"])

# Mostramos los resultados
print('ADF Statistic: %f' % ADF[0])
print('p-value: %f' % ADF[1])

# No tenemos suficiente evidencia estadistica para rechazar H0 -> Serie no estacionaria


# KPSS
from statsmodels.tsa.stattools import kpss

# H0: Serie Estacionaria

KPSS = kpss(datos["Creditos_Personales"])

# Mostramos los valores
print('KPSS Statistic: %f' % KPSS[0])
print('p-value: %f' % KPSS[1])

# Rechazamos H0 -> Serie No estacionaria


# PP
from arch.unitroot import PhillipsPerron as PP

# H0: Serie  NO Estacionaria

PP = PP(datos["Creditos_Personales"])

# Mostramos los valores
PP

# No tenemos suficiente evidencia estadistica para rechazar H0 -> Serie no estacionaria


# ERS
from arch.unitroot import DFGLS

# H0: Serie  NO Estacionaria

ERS = DFGLS(datos["Creditos_Personales"])

# Mostramos los valores
ERS

# No tenemos suficiente evidencia estadistica para rechazar H0 -> Serie no estacionaria


# Podemos observar en todos los contrastes realizados que la serie origina
# es claramente no estacionaria.


# Repetimos con las primeras diferencias de los logaritmos.
# Esta es la serie que graficamente parecia la "mejor".


# ADF

ADF = adfuller(Log_Datos_Dif[0])

# Mostramos los resultados
print('ADF Statistic: %f' % ADF[0])
print('p-value: %f' % ADF[1])

# Rechazamos H0 al 90%, no al 95%.


# KPSS
KPSS = kpss(Log_Datos_Dif[0])

# Mostramos los valores
print('KPSS Statistic: %f' % KPSS[0])
print('p-value: %f' % KPSS[1])

# Rechazamos H0 -> Serie Estacionaria.



# ERS
ERS = DFGLS(Log_Datos_Dif)
ERS

# No rechazamos H0


# En este caso parece que es una buena aproximacion.


# Pasamos a la fase de modelizacion.

# Analizamos la correlacion y la correlacion parcial
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

plot_acf(Log_Datos)
plot_pacf(Log_Datos)

# Dividimos los datos en train y test

train = Log_Datos.loc[:"2010-12-01 00:00:00"]
test = Log_Datos["2011-01-01 00:00:00":]


import statsmodels.api as sm

model = sm.tsa.statespace.SARIMAX(train.iloc[:,0], order=(2,1,1), seasonal_order=(1,0,1,12))


ArimaModel = model.fit()
print (ArimaModel.summary())

test["Predicciones"] = ArimaModel.forecast(len(test))


import numpy as np
test["Creditos_Personales"]  = np.exp(test["Creditos_Personales"])
test["Predicciones"]  = np.exp(test["Predicciones"])

import matplotlib.pyplot as plt
plt.plot(test)


# Analizamos los residuos
ArimaModel.plot_diagnostics(figsize = (14,10))

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


plot_acf(ArimaModel.resid)
plot_pacf(ArimaModel.resid)


# Pasamos a utilizar el AutoArima  (No lo hace bien)
ArimaModel = pmdarima.auto_arima(train, error_action='ignore', seasonal=True, m=12)

ArimaModel.summary()

# Sacamos las predicciones del modelo.
test["Predicciones"] = Predicciones = ArimaModel.predict(len(test))


# Estas predicciones son logaritmos por lo que hay que invertir el proceso
test["Creditos_Personales"]  = np.exp(test["Creditos_Personales"])
test["Predicciones"]  = np.exp(test["Predicciones"])

# Graficamos los datos de test.
plt.plot(test)


# Analizamos los residuos del modelo.
plt.plot(ArimaModel.resid())

# Comprobamos que los residuos iniciales son altos

# Analizamos el correlograma y el correlograma parcial de los errores
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


plot_acf(ArimaModel.resid())
plot_pacf(ArimaModel.resid())

ArimaModel.plot_diagnostics(figsize = (14,10))
