# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 16:00:48 2018

@author: herre
"""

import pandas as pd
import math
import numpy as np
import geopandas as gp
#import matplotlib as plt
#import seaborn as sns
#import  scipy as  scipy
import Tkinter as tk
import easygui as eg

"CARGAR SHP AL PROGRAMA"

def shp():

    extension = ["*.shp"]

    archivo = eg.fileopenbox(msg="Abrir archivo",
                             title="Escoge el Shapefile",
                             default='',
                             filetypes=extension)

    shape = gp.read_file(archivo) 
    #shp = gp.GeoDataFrame.from_file(shape)
    #sh= gp.GeoDataFrame.plot(shape)
    print (shape[shape.columns[1:5]])
    "CARGA DE DATOS Y CONVERSION A DATAFRAME"
    #print (datos)
    nuevo= pd.DataFrame(shape)

    return nuevo

"PARAMETROS"

def procesamiento():

    nuevo = shp()

    #LONGITUD DE CAUCE PRINCIPAL

    L= nuevo['L_CP'] #KILOMETROS
    L_MILLAS=L*0.621371 #MILLAS

    #AREA
    A=nuevo['AREA'] #KILOMETROS
    A_MILLAS= A* 0.386102  #MILLAS

    #DIAMETRO CUENCA CIRCULAR

    D= np.sqrt(4*nuevo['AREA']/math.pi) #KILOMETROS 
    D_MILLAS= D*0.621371 #MILLAS

    #PENDIENTES A GRADOS
    S= nuevo['PM_CP']# Pendiente en m/m
    r=180/math.pi
    S_G= np.arctan(S)*r #PENDIENTE EN GRADOS

    #DELTA DE ALTURAS
    H= nuevo['C_MAX_CP']-nuevo['C_MIN_CP'] #DELTA EN KM
    H_PIES= H*3.28084 #DELTA EN PIES

    #CURVA NUMERO

    CN= nuevo['CN']

    #############################################################

    "GENERACION DE COLUMNAS CON TIEMPOS DE CONCENTRACION"

    #WILLIAMS

    a=nuevo['Williams']= (((L_MILLAS)*(A_MILLAS)**0.4)/((D_MILLAS)*(S_G)**0.25))*60

    #KIRPICH
    b= nuevo['Kirpich']= 0.06628*(((L)/np.sqrt(S))**0.77)*60

    # California Culvert Practice

    c=nuevo['Cali_Cul_Pra']= 60*(11.9*(L_MILLAS**3)/(H_PIES))

    #TEMEZ

    d=nuevo['Temez']= (0.3*(L/(S_G)**(0.25))**0.75)*60

    #GIANDOTTI
    e= nuevo['Guiandotti']= (((4*np.sqrt(A))+(1.5*L))/(0.8*np.sqrt(H)))*60

    #SCS - Ranser

    f= nuevo['SCS_Ranser']= (0.97*(L**3/H)**0.385)*60

    #SCS

    g= nuevo['SCS']= (((0.0136*(L*1000)**0.8))*(((1000/CN)-9)**0.7))/(S**0.5)

    #VENTURA-HERAS
    h=nuevo['Ventura-Heras']= ((L/np.sqrt(A))*((A**0.5)/S_G))*60
    #h=nuevo['Ventura-Heras']= ((0.3)*((A**0.5)/S_G))*60

    #Bransby - Williams
    i=nuevo['Bransby-Williams']= (21.3*L_MILLAS *(1/(A_MILLAS**0.1)*(S**0.2)))

    #Clark

    j=nuevo['Clark']= (0.335*(A*(S**0.5))**0.593)*60

    #Valencia y Zuluaga

    k=nuevo['Valencia_Zuluaga']= (1.7694*(A**0.325)*(L**(-0.096))*(S_G**(-0.290)))*60

    #Pilgrim y McDermott

    l= nuevo['Pilgrim_McDermott']= (0.76*(A**0.38))*60
    #PROMEDIO ACOTADO

    ######################################################################
    "NUEVO ARREGLO"

    TC = nuevo[['ID_UH','Williams','Kirpich','Cali_Cul_Pra','Temez','Guiandotti','SCS_Ranser','SCS','Ventura-Heras','Bransby-Williams','Clark','Valencia_Zuluaga', 'Pilgrim_McDermott']]
    ######################################################################
    "CALCULO DEL PRIMEDIO"
    s=TC[['Williams','Kirpich','Cali_Cul_Pra','Temez','Guiandotti','SCS_Ranser','SCS','Ventura-Heras','Bransby-Williams','Clark','Valencia_Zuluaga', 'Pilgrim_McDermott']]
    TC['Promedio']= np.mean(s,axis=1)
    ######################################################################

    "CALCULO DE LA DESVIACIÓN ESTANDAR"

    TC['STD_Tipica']= np.std(s,axis=1)                  

    "PROMEDIO_ACOTADO"

    TC['u_min']= TC['Promedio'] - TC['STD_Tipica']
    TC['u_max']= TC['Promedio'] + TC['STD_Tipica']

    u_min= TC['Promedio'] - TC['STD_Tipica']
    u_max= TC['Promedio'] + TC['STD_Tipica']

    #print (TC[TC.columns[13]])

    #resultado= []
    Data =  s.values
    maximo = u_max.values
    minimo = u_min.values

    medicion = Data.transpose()

    tamano = np.arange(len(Data))
    tamano1 = np.arange(len(medicion))

    resultado = []
    contador = 0

    for x in tamano:
        sum=0
        n = 0
        Dato = Data[x]    
        for y in tamano1:
            if Dato[y] < maximo[contador] and Dato[y] > minimo[contador]:
                sum = sum + Dato[y]
                n = n + 1
                promacot= sum/n
        resultado.append(promacot)
        contador = contador + 1

    TC['Promedio_Acotado'] = resultado
    ##############################################################################
    "Eleccion del más cercano"
    prom_acot= TC['Promedio_Acotado'] 
    promacota= prom_acot.values

    medicion = Data.transpose()

    tamano = np.arange(len(Data))
    tamano1 = np.arange(len(medicion))

    resultado1 = []
    contador = 0
    for x in tamano:
        Dato = Data[x]    
        aproxc=10000000000
        for y in tamano1:
            aprox= np.absolute(promacota[contador] - Dato[y])
            #print (aprox)
            if aprox < aproxc:
                aproxc= aprox
                aproxi= Dato[y]
                #print(aproxi)
                
        resultado1.append(aproxi)
        contador = contador + 1

    TC['Promedio_Aproximado'] = resultado1
    #############################################################################
    "NOMBRE DEL ESCOGIDO"
    tc_aprox= TC['Promedio_Aproximado'] 
    indices = []
    contador = 0
    for x in tamano:
        Dato = Data[x]    
        for y in tamano1:
            if tc_aprox[contador] == Dato[y]:
                nom = s.columns.values[y]
        indices.append(nom)
        contador = contador + 1
        
    TC['Tc_Escogido'] = indices

    #print(TC)
    ############################################################################
    "Tiempo de Resago"
    ###########################################################################
    #Distancia Centroidal de la Cuenca
    #MILLAS
    d1=TC['d1']= (1.4*(A**0.568))*0.386102
    d2=TC['d2']= ((1.7*(A_MILLAS**0.58)))
    d3=TC['d3']= (((1.64*(A_MILLAS**0.55))))
    d4=TC['d4']= (((1.6*(A_MILLAS**0.55))))

    DCCA= TC[['d1','d2','d3','d4']]
    DCC = TC['Dist_Centr_C']= (0.54*np.mean(DCCA, axis=1)**0.96)  #DISTANCIA AL CENTROIDE EN MILLAS
    DCC_KM= DCC/0.621371  # DISTANCIA AL CENTROIDE EN KILOMETROS
    ###############################################################################

    # PENDIENTE EN PIES SOBRE MILLAS

    S_P_M = H_PIES/ L_MILLAS
    ####################################################################################
    #PERMEABILIDAD
    
    PERM= nuevo['IMP']
    ##################################################################################
    # Tiempos de Retardo

    TC['Eagleson']=(0.32*((L_MILLAS*DCC)/np.sqrt(S_P_M))**0.39)*60
    
    TC['Putnam']= (0.49*(np.sqrt(L_MILLAS/np.sqrt(S_P_M))*(PERM**-0.57)))*60
        
    TC['SCS']= ((L**0.8)*((((1000/CN)-9)**0.7)/((1900*S_G)**0.5)))*60
    TC['Snyder']= 0.32*(((DCC*L_MILLAS)/S**0.5)**1.42)
    TC['Chow']= tc_aprox*0.6
    ####################################################################################
    # Promedio Lag Time
    T_lag= TC[['Eagleson','Putnam','SCS','Snyder','Chow']]
    TC['Promedio_T_Lag']= np.mean(T_lag, axis=1)

    # Desviación Estandar

    TC['STD_Tip_T_lag']= np.std(T_lag,axis=1)
    ######################################################################################
    # Promedio Acotado
    u_min_T= TC['Promedio_T_Lag'] - TC['STD_Tip_T_lag']
    u_max_T= TC['Promedio_T_Lag'] + TC['STD_Tip_T_lag']

    T_L = T_lag.values
    max = u_max_T.values
    min = u_min_T.values

    med = T_L.transpose()

    i = np.arange(len(T_L))
    j = np.arange(len(med))

     
    prom_t_lag = []
    cont = 0

    for x in i:
        suma=0
        m = 0
        Dat = T_L[x]    
        for y in j:
            if Dat[y] < max[cont] and Dat[y] > min[cont]:
                suma = suma + Dat[y]
                m = m + 1
                promacota= suma/m
        prom_t_lag.append(promacota)
        cont = cont + 1

    TC['Prom_Ac_T_Lag'] = prom_t_lag
    ######################################################################################
    "Eleccion del más cercano"

    prom_acotad= TC['Prom_Ac_T_Lag']
    a_prom_acot= prom_acotad.values

    a_prom_aprox = []
    contador = 0
    for x in i:
        Dat = T_L[x]    
        aproxc=10000000000
        for y in j:
            aprox= np.absolute(a_prom_acot[contador] - Dat[y])
            #print (aprox)
            if aprox < aproxc:
                aproxc= aprox
                aproxi= Dat[y]
                #print(aproxi)
                
        a_prom_aprox.append(aproxi)
        contador = contador + 1

    TC['Prom_Aprox_T_Lag'] = a_prom_aprox
    #####################################################################################
    "NOMBRE DEL ESCOGIDO"
    tc_aprox_t_lag= TC['Prom_Aprox_T_Lag']
    indice = []
    contador = 0
    for x in i:
        Dat = T_L[x]    
        for y in j:
            if tc_aprox_t_lag[contador] == Dat[y]:
                nomb = T_lag.columns.values[y]
        indice.append(nomb)
        contador = contador + 1
        
    TC['Tl_Escog'] = indice
    #########################################################################################
    Salida=TC[['ID_UH','Williams','Kirpich','Cali_Cul_Pra','Temez','Guiandotti','SCS_Ranser','SCS','Ventura-Heras','Bransby-Williams','Clark','Valencia_Zuluaga', 'Pilgrim_McDermott','Promedio','STD_Tipica','Promedio_Acotado','Promedio_Aproximado', 'Tc_Escogido','Eagleson','Putnam','SCS','Snyder','Chow','Promedio_T_Lag','STD_Tip_T_lag', 'Prom_Ac_T_Lag','Prom_Aprox_T_Lag','Tl_Escog']]
    #print(A)
    #print(A_MILLAS)
    #print(TC[['d1','d2','d3','d4','Dist_Centr_C']])

    extension = ["*.csv"]

    csv = eg.filesavebox(msg="Guardar archivo",
                         title="Guardar:",
                         default='',
                         filetypes=extension)
                        
    Salida.reset_index().to_csv(csv,header=True,index=False)
    #print(T_lag)
    #print(TC[['Promedio_T_Lag', 'STD_Tip_T_lag', 'Prom_Ac_T_Lag']])
    #print(TC[['Prom_Aprox_T_Lag', 'Tl_Escog']])

###############################################################
"INTERFAZ"

ventana= tk.Tk()
ventana.title("CALCULO DE TIEMPO DE CONCENTRACION")
#ANCHOYALTO
ventana.geometry('480x100')
ventana.configure(background= 'lavender')
etiqueta1= tk.Label(ventana, text="Procesamiento de datos", font='Garamond 12 bold' ,bg='lavender', fg="black")
etiqueta1.pack(fill=tk.X)
boton = tk.Button(ventana, text="procesamiento", command = procesamiento)
boton.pack()
ventana.mainloop()
#############################################################
###########################################################







