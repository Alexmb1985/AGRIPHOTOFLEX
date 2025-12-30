# -*- coding: utf-8 -*-
"""
Created on Wed Dec 24 09:09:57 2025

@author: Marti
"""

import bifacial_radiance as br
import pandas as pd
import sys, platform
#import matplotlib.pyplot as plt #llibreria per plots i figures
#import seaborn as sns #llibreria de visualtizacio, per al heatmap
print("Working on a", platform.system(),platform.release())
print("Bifacial version:",br.__version__)
print("Python version", sys.version)
print("Pandas version", pd.__version__)

#creació carpeta per a guardar els resultats i documents generats

import os
from pathlib import Path

nom_simulacio='simple_1'

dir_base=Path(__file__).parent #la carpeta on guardes el script
testfolder=dir_base/'Simulacions_bifacial'/nom_simulacio #creem el path desde directori base amb el nom de la simu
testfolder.mkdir(parents=True, exist_ok=True) # crea la carpeta, si ja existeix no
os.chdir(testfolder)# cambia el directori de treball a la carpeta creada
print("Your simulation will be stored in %s" %testfolder)

#creem el objecte radiance
agri=br.RadianceObj(name=nom_simulacio,path=str(testfolder))

#Definim Terra
albedo=0.3 #tipic albedo the grass/herba
agri.setGround(albedo)

# Latitud i longitud de lleida
lat=41.6
lon=0.6

#Fitxer epw
epw=agri.getEPW(lat=lat,lon=lon)

#Sel·leccionem interval de temps, 1 setmana de juny 2023
starttime='2015-06-10_0000'
endtime='2015-06-17_2359'
metdata=agri.readWeatherFile(epw,starttime=starttime,endtime=endtime)

timeindex=metdata.datetime.index(pd.to_datetime('2015-06-13 12:0:0 +1'))
sky=agri.gendaylit(metdata=metdata,timeindex=timeindex)


#DEFINICIO DELS MODULS
moduletype='flexmodule' #nom del modul
numpanels=1 #3 panels each module along the y direction (enunciat)
x=0.992 #m
y=1.251 #m
z=0.0002#thickness of the glass
xgap=0.2 #20 cm entre mòduls contant que passa cable acer galvanitzat d 6 entre mig
ygap=0.3 # dona igual, es per distancia entre panells si un modul esta format per més d'un panell
zgap=0 # no gap with the torque tube

AxisOfRotationTorqueTube=False
torqueTube=False
cellLevelModule=True  
#Paràmetres definició per cel·les
numcellsx=3
numcellsy=12
xcell=0.166
ycell=0.083
xcellgap=0.152
ycellgap=0.01 #0.002
glass=True 
#glassEdge= 80
#dictionary of cell level parameters
cellLevelModuleParams={'numcellsx':numcellsx, 'numcellsy':numcellsy,
                       'xcell':xcell, 'ycell':ycell,'xcellgap':xcellgap,'ycellgap':ycellgap}

module=agri.makeModule(name=moduletype,x=x,y=y,xgap=xgap,ygap=ygap,glass=glass,z=z,numpanels=numpanels,cellModule=cellLevelModuleParams)

#module.saveImage()
#DEFINICIÓ ESCENA
#Parameters of the scene (SceneDict)
pitch=module.sceney+0.142+0.08+0.1 #m distancia entre files 1.5 passa a ser distancia entre mòduls de 0.5
albedo=0.2 #grass cst reflexio del terra
hub_height=4.3 #m 10 cm més que l'alçada dels pals
nMods=5 #num of modules per row
nRows=2 # 2
azimuth=180 # facing south
tilt=0
#Create the scene
#dictionary with the parameters
sceneDict={'tilt':tilt,'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods':nMods,'nRows':nRows}
    


scene=agri.makeScene(module=module,sceneDict=sceneDict)
octfile=agri.makeOct()


    
#visualize image
#!rvu Escena_sense_malla_1_set.oct only when gendaylit used
  
#ESTRUCTURA POSTES
llargadatotal=18 #m
diametre=0.13 #m
alcada=4.2
sep_rencs=3.5 #m
sep_pals= 3 #m

#per defecte l'origen està al centre dels mòduls
origen_palx=module.scenex*2.5
origen_paly=pitch/2

#origen de la escena
# Name='Pilar_origen'
# text=' ! genrev Metal_Grey tube1_1 t*4.2 0.13 32 | xform -t 0 0 0'
# customObject=agri.makeCustomObject(name=Name,text=text)
# scene.appendtoScene(customObject=customObject)
#El origen es el mòdul central de la primera fila

#Creem els 3 pals del mig primer

Name='Pilars_c'
text=' ! genrev Metal_Grey tube1_1 t*4.2 0.13 32 | xform -t {} {} 0'.format(origen_palx,origen_paly)
customObject=agri.makeCustomObject(name=Name,text=text)
scene.appendtoScene(customObject=customObject)
Name='Pilars_a'
text=' ! genrev Metal_Grey tube1_1 t*4.2 0.13 32 | xform -t {} {} 0'.format(origen_palx,origen_paly+3.5)
customObject=agri.makeCustomObject(name=Name,text=text)
scene.appendtoScene(customObject=customObject)
Name='Pilars_b'
text=' ! genrev Metal_Grey tube1_1 t*4.2 0.13 32 | xform -t {} {} 0'.format(origen_palx,origen_paly-3.5)
customObject=agri.makeCustomObject(name=Name,text=text)
scene.appendtoScene(customObject=customObject)

#línies de pilars
for i in range(1,5):
    Name='Pilarslinia_%s' %i
    text=' ! genrev Metal_Grey tube1_{} t*4.2 0.13 32 | xform -t {} {} 0'.format(i,origen_palx-3*i,origen_paly)
    #\r\n comença una nova linia de text sota el anterior
    text+='\r\n! genrev Metal_Grey tube2_{} t*4.2 0.13 32 | xform -t {} {} 0'.format(i,origen_palx-3*i,origen_paly+3.5)
    text+='\r\n! genrev Metal_Grey tube3_{} t*4.2 0.13 32 | xform -t {} {} 0'.format(i,origen_palx+-3*i,origen_paly-3.5)
    customObject=agri.makeCustomObject(name=Name,text=text)
    scene.appendtoScene(customObject=customObject)

#materials arbres

#creats directament amb funcions de radiance perquè dona error l'instruccio de br amb materials translúcids
def create_tree_materials(filename='materials/apple_tree.rad'):
    """Generar els materials per model·lar pomeres"""
    os.makedirs('materials',exist_ok=True)
    content="""#Apple tree materials for AgriPV research
# Material fulla, per model·lar la superfície cilíndrica que representa la copa de la pomera
void trans leaf
0
0
7 0.10 0.20 0.10 0.02 0.05 0.30 0.0
    
# Material imita la fusta del tronc
void plastic applewood
0
0
5 0.18 0.15 0.12 0.02 0.3
"""

    with open(filename, 'w') as f:
        f.write(content)
    print(f"Created {filename}")
    return filename
apple_tree_mat=create_tree_materials()
agri.returnMaterialFiles()


#paràmetres arbres

rcop=1/2 #m2 radi de la copa
rtronc=0.2/2 #m 20 centimetres de radi tronc
alcada_arbre=3 #3 m alçada dels arbres
sep_arbres=0.5 # separació entre arbres
zcopa=1.5 #Z on comença la copa dels arbres

sep_c_arbres=1.4 #separació entre el centre dels arbres
sep_ap=0.8# separacio entre centre arbres i pilars
origen_ax=origen_palx-sep_ap
origen_ay=origen_paly

# creem un paquet de 2 arbres entre pilars, i amb el for en col·loquem un a cada espai 
# operador op es per quan estigui a una alternar la construcció de files d'arbres, amunt i avall del central
for j in range(0,3):
    for jj in range (0,4):
        op= 0 if j==0 else (-1 if j % 2 == 0 else 1)
        name='arbres'+str(j)+str(jj)
        text='! genrev leaf arbrecopa1_{} t*{} {} 32 | xform -t {} {} {}'.format(str(j)+str(jj),alcada_arbre-zcopa,rcop,origen_ax-jj*3,origen_ay+op*3.5,zcopa)
        text+=' \r\n! genrev leaf arbrecopa2_{} t*{} {} 32 | xform -t {} {} {}'.format(str(j)+str(jj),alcada_arbre-zcopa,rcop,origen_ax-jj*3-sep_c_arbres,origen_ay+op*3.5,zcopa)
        text+=' \r\n! genrev applewood arbretronc_1{} t*{} {} 32 | xform -t {} {} 0'.format(str(j)+str(jj),alcada_arbre,rtronc,origen_ax-jj*3,origen_ay+op*3.5)
        text+=' \r\n! genrev applewood arbretronc2_{} t*{} {} 32 | xform -t {} {} 0'.format(str(j)+str(jj),alcada_arbre,rtronc,origen_ax-jj*3-sep_c_arbres,origen_ay+op*3.5)
        customObject=agri.makeCustomObject(name=name,text=text)
        scene.appendtoScene(customObject=customObject)

    
octfile=agri.makeOct()

#Quan s'obri el render -> cambiar exposure a Natural
!rvu -vf views\front.vp -e .08 -ab 2 -ad 256 -as 128 simple_1.oct


   
# analysis=br.AnalysisObj(octfile,agri.name)
# frontscan, backscan = analysis.moduleAnalysis(scene)
# analysis.analysis(octfile=octfile,name=agri.name,frontscan=frontscan,backscan=backscan,accuracy='high')
# results=br.load.read1Result(r'results\irr_Escena_sense_malla_3_set_Row1_Module3.csv')
# print(results.Wm2Back)
# print(results.Wm2Front)