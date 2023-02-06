# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 10:25:44 2023

@author: borja
"""

import pandas as pd
import os

os.chdir(r"C:\Users\borja\Documents\UNAV\Master2023")
# Cargamos los datos
datos = pd.read_excel("Inflation.xlsx")

# Eliminamos la variable que no nos interesa
del (datos["Monthly_Rate"])
datos.columns
# Pasamos la fecha a formato fecha
datos["observation_date"] = pd.to_datetime(datos["observation_date"], format="%Y-%m-%d %H:%M:%S")

# Pasamos la fecha al indice
datos.index = datos["observation_date"]
del (datos["observation_date"])

# Ya disponemos de los datos en el formato adecuado.

# Procedemos a analizar la inflacion
import matplotlib.pyplot as plt
plt.plot(datos["Monthly_Inflation"])

# En este primer grafico parece una serie estacionaria.
# Hay que destacar que esta serie ya esta diferenciada.
# La inflacion es el IPC diferenciado

# Procedemos a comprobar si seria necesario diferenciarla
import pmdarima

# Respecto a la observacion anterior
pmdarima.arima.ndiffs(datos["Monthly_Inflation"])

# Da error ya que tenemos valores perdidos.

# Procedemos a analizar donde se encuentran esos valores.
datos.describe()

# Al analizar el count vemos que tenemos los valores perdidos.
# Procedemos a localizarlos.

# Extraemos los datos con NaN
datosNoComp = datos[datos.isna().any(axis=1)]

# Vemos que son el primer y el ultimo dato.
# Podemos (y debemos eliminar esos datos)

datos=datos.dropna()

# Repetimos el proceso.
pmdarima.arima.ndiffs(datos["Monthly_Inflation"])

# Nos muestra que no es necesario diferenciarlo.

# Estacionalmente con estacionalidad anual.
pmdarima.arima.nsdiffs(datos["Monthly_Inflation"], m = 12)

# Tampoco habria que diferenciarla estacilnalmente.


# Pasamos a comprobarlo mediante los test que conocemos.

# ADF
from statsmodels.tsa.stattools import adfuller

# H0: No estacionario (raiz unitaria)


ADF = adfuller(datos["Monthly_Inflation"])

# Mostramos los resultados
print('ADF Statistic: %f' % ADF[0])
print('p-value: %f' % ADF[1])

# Rechazamos H0 -> Serie estacionaria


# KPSS
from statsmodels.tsa.stattools import kpss

# H0: Serie Estacionaria

KPSS = kpss(datos["Monthly_Inflation"])

# Mostramos los valores
print('KPSS Statistic: %f' % KPSS[0])
print('p-value: %f' % KPSS[1])

# No tenemos suficiente evidencia estadistica para rechazar H0 -> Serie Estacionaria


# PP
from arch.unitroot import PhillipsPerron as PP

# H0: Serie  NO Estacionaria

PP = PP(datos["Monthly_Inflation"])

# Mostramos los valores
PP

# Rechazamos H0 -> Serie estacionaria


# ERS
from arch.unitroot import DFGLS

# H0: Serie  NO Estacionaria

ERS = DFGLS(datos["Monthly_Inflation"])

# Mostramos los valores
ERS

# Rechazamos H0 -> Serie estacionaria


# En este caso podemos afirmar sin duda alguna que la serie es estacionaria.

# Pasamos a visualizar su descomposicion.

from statsmodels.tsa.seasonal import seasonal_decompose

# De manera aditiva
SerieDescompuesta = seasonal_decompose(datos["Monthly_Inflation"], model='additive')

# La graficamos.
SerieDescompuesta.plot(observed=True, seasonal=True, trend=True, resid=True, weights=False)


# En este caso observamos varios aspectos:
    # La componente estacional tiene un peso minimo.
    # Los residuos se semejan a un ruido blanco.
    # No se aprecian ciclos pese a que hay ciertos picos.
    
# Tras ello procedemos a la realizacion del correlograma y el correlograma parcial.

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

plot_acf(datos["Monthly_Inflation"])
plot_pacf(datos["Monthly_Inflation"])

# Sin embargo al visualizar ambos graficos se aprecia una componente estacional.
# Con una periodicidad de 12 meses.

# El correlograma muestra estacionalidad por lo que la parte MA sera 2 y 2 estacional.
# El correlograma parcial se trunca en el uno por lo que muestra un AR(1)

# Separamos en train y test
train = datos.loc[:"2014-12-01 00:00:00"]
test = datos["2015-01-01 00:00:00":]

# Entrenaos el modelo segun lo descrito anteriormente.

import statsmodels.api as sm

model = sm.tsa.statespace.SARIMAX(train.iloc[:,1], order=(1,0,2), seasonal_order=(1,0,2,12))

# Visualizamos el modelo
ArimaModel = model.fit()
print (ArimaModel.summary())

# Todos los valores son significativos

# Sacamos las predicciones
test["Predicciones"] = ArimaModel.forecast(len(test))


# Comprobamos que el modelo se ha estimado de forma correcta
# Analizamos los residuos
ArimaModel.plot_diagnostics(figsize = (14,10))

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Parece correcto.

plot_acf(ArimaModel.resid)
plot_pacf(ArimaModel.resid)

# Esto confirma lo anterior con un mayor numero de Lags


# Analizamos las predicciones mediante el ECM
test.dtypes
ECM = sum((test["Monthly_Inflation"] - test["Predicciones"])**2)/len(test)
ECM

plt.plot(test[["Monthly_Inflation","Predicciones"]])

# Procedemos a añadir el ratio de los bancos al modelo ARIMAX
train = datos.loc[:"2014-12-01 00:00:00"]
test = datos["2015-01-01 00:00:00":]

Modelo2 = sm.tsa.statespace.SARIMAX(train["Monthly_Inflation"], order=(1,0,2), seasonal_order=(1,0,2,12),exog = train["Bank Rate"])

ArimaModel2 = Modelo2.fit()
print (ArimaModel2.summary())

# Observamos que el Bank Rate es relevente.

# Comprobamos que el modelo sea correcto
ArimaModel2.plot_diagnostics(figsize = (14,10))

# A primera vista parece peor estimado.

plot_acf(ArimaModel2.resid)
plot_pacf(ArimaModel2.resid)

# Si Comparamos AIC y BIC se corrobora lo mismo



# Realizamos las predicciones
test["Predicciones"] = ArimaModel2.forecast(len(test), exog= test["Bank Rate"])

ECM2 = sum((test["Monthly_Inflation"] - test["Predicciones"])**2)/len(test)
ECM2

plt.plot(test[["Monthly_Inflation","Predicciones"]])

# El ECM se dispara.

# En este caso no parece una buena alternativa añadir
# Una variable externa ya que se sobreentrena.

# Otro posible problema seria definir mal el ARIMA

train = datos.loc[:"2014-12-01 00:00:00"]
test = datos["2015-01-01 00:00:00":]

# Entrenaos el modelo segun lo descrito anteriormente.

import statsmodels.api as sm

model = sm.tsa.statespace.SARIMAX(train.iloc[:,1], order=(1,0,0), seasonal_order=(1,0,0,12))

# Visualizamos el modelo
ArimaModel = model.fit()
print (ArimaModel.summary())

# Todos los valores son significativos

# Sacamos las predicciones
test["Predicciones"] = ArimaModel.forecast(len(test))


# Comprobamos que el modelo se ha estimado de forma correcta
# Analizamos los residuos
ArimaModel.plot_diagnostics(figsize = (14,10))

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Parece correcto.

plot_acf(ArimaModel.resid)
plot_pacf(ArimaModel.resid)

# Esto confirma lo anterior con un mayor numero de Lags


# Analizamos las predicciones mediante el ECM
test.dtypes
ECM = sum((test["Monthly_Inflation"] - test["Predicciones"])**2)/len(test)
ECM

plt.plot(test[["Monthly_Inflation","Predicciones"]])
