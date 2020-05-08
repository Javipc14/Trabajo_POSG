# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FotoShapeDialog
                                 A QGIS plugin
 Este plugin transforma un archivo csv en un shp y ademas muestra imagenes
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-05-05
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Javier
        email                : j_pisonero@usal.es
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import qgis.core

from qgis.PyQt import QtGui, QtWidgets, QtCore, uic
from qgis.PyQt.QtCore import pyqtSignal,QVariant
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.gui import QgsMessageBar
from qgis.core import QgsVectorLayer
from qgis.core import QgsRasterLayer
from qgis.core import QgsProject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'FotoShape_dialog_base.ui'))


class FotoShapeDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(FotoShapeDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setupUi(self)
        # Filtros
        self.qfw_ruta.setFilter("Archivos csv separado por comas(*.csv)")
        self.qfw_rutaortofoto.setFilter("Archivos ortofoto(*.ecw)")
        # Añadir accion en el boton
        self.btn_cargar.clicked.connect(self.cargar_datos)
        self.qtw_tabla.clicked.connect(self.cargar_imagen)

    def cargar_datos(self, event):
        # Cargar la ortofoto
        directorio = str(self.qfw_rutaortofoto.filePath())
        lettertochange = directorio[2]
        for letter in directorio:
            if letter == lettertochange:
                ruta_ortofoto = directorio.replace('\\', '/')

        qgis.core.QgsMessageLog.logMessage(ruta_ortofoto, 'Javi', qgis.core.Qgis.Warning)
        layer_name = "Ortofoto"
        rasterLyr = QgsRasterLayer(ruta_ortofoto, layer_name)

        if not rasterLyr.isValid():
            QgsMessageLog.logMessage('Capa Raster - Ortofoto no válida', 'Javi', qgis.core.Qgis.Warning)
            iface.messageBar().pushMessage("Error", "Capa no valida", level=qgis.core.Qgis.Critical, duration=5)
        else:
            QgsProject.instance().addMapLayers([rasterLyr])
            new_extent = rasterLyr.extent()

        # Cargar las capas a partir del csv
        ruta_csv = str(self.qfw_ruta.filePath())

        # Rutas y variables para las capas de salida: Plaza - Parque - Iglesia - Puente
        uriPlaza = ruta_csv
        uriParque = ruta_csv
        uriIglesia = ruta_csv
        uriPuentes = ruta_csv

        # Crear los ficheros de slaida a partir de donde esté el csv. Reemplazamos .csv por lo que queramos
        # QMessageLog, para ir dejando un registro de mensajes de evolución del proceso
        rutaPlaza = uriPlaza.replace(".csv", "_plazas.shp")
        qgis.core.QgsMessageLog.logMessage(rutaPlaza, 'Javi', qgis.core.Qgis.Warning)

        rutaParque = uriParque.replace(".csv", "_parques.shp")
        qgis.core.QgsMessageLog.logMessage(rutaParque, 'Javi', qgis.core.Qgis.Warning)

        rutaIglesia = uriIglesia.replace(".csv", "_iglesias.shp")
        qgis.core.QgsMessageLog.logMessage(rutaIglesia, 'Javi', qgis.core.Qgis.Warning)

        rutaPuentes = uriPuentes.replace(".csv", "_puentes.shp")
        qgis.core.QgsMessageLog.logMessage(rutaPuentes, 'Javi', qgis.core.Qgis.Warning)

        # Crear una capa por cada tipo de elemennto. Seran capas para almacenar puntos
        plazas = QgsVectorLayer("Point", "plazas", "memory")
        parques = QgsVectorLayer("Point", "parques", "memory")
        iglesias = QgsVectorLayer("Point", "iglesias", "memory")
        puentes = QgsVectorLayer("Point", "puentes", "memory")

        # dataProvider de cada una de las capas para poder acceder a sus datos y atributos
        # Asignar a cada capa los atributos de Nombre e imagen. (las coordenadas van aparte)
        dp_Plazas = plazas.dataProvider()
        dp_Plazas.addAttributes([qgis.core.QgsField("Nombre", QVariant.String),
                                 qgis.core.QgsField("Imagen", QVariant.String)])
        plazas.updateFields()

        dp_Parques = parques.dataProvider()
        dp_Parques.addAttributes([qgis.core.QgsField("Nombre", QVariant.String),
                                  qgis.core.QgsField("Imagen", QVariant.String)])
        parques.updateFields()

        dp_Iglesias = iglesias.dataProvider()
        dp_Iglesias.addAttributes([qgis.core.QgsField("Nombre", QVariant.String),
                                   qgis.core.QgsField("Imagen", QVariant.String)])
        iglesias.updateFields()

        dp_Puentes = puentes.dataProvider()
        dp_Puentes.addAttributes([qgis.core.QgsField("Nombre", QVariant.String),
                                qgis.core.QgsField("Imagen", QVariant.String)])
        puentes.updateFields()

        # Cargamr los datos del csv en la tabla
        self.qtw_tabla.setEnabled(True)

        with open(ruta_csv, 'r') as leer_csv:  # abrir el archivo para leer
            lineas = leer_csv.read().splitlines()  # Separar por lineas
            contar = 0
            for linea in lineas:  # Recorrer linea a linea
                if contar > 0:
                    campos = linea.split(';')  # Separa la posicion del ; y almacena en campos un vector con toda la informacion
                    self.qtw_tabla.insertRow(self.qtw_tabla.rowCount())  # Se inserta una fila en la tabla
                    self.qtw_tabla.setItem(self.qtw_tabla.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(str(campos[0])))
                    self.qtw_tabla.setItem(self.qtw_tabla.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(str(campos[1])))
                    self.qtw_tabla.setItem(self.qtw_tabla.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(str(campos[2])))
                    self.qtw_tabla.setItem(self.qtw_tabla.rowCount() - 1, 3, QtWidgets.QTableWidgetItem(str(campos[3])))
                    self.qtw_tabla.setItem(self.qtw_tabla.rowCount() - 1, 4, QtWidgets.QTableWidgetItem(str(campos[4])))
                    # Se carga cada fila de la tabla con la informacion en cada columna

                    # Ahora en funcion del valor del primer atributo, añadir el punto a una capa u otra.
                    if (str(campos[0]) == "Plaza"):
                        qgis.core.QgsMessageLog.logMessage(str(campos[0]), 'Javi', qgis.core.Qgis.Warning)
                        f = qgis.core.QgsFeature()
                        f.setGeometry(qgis.core.QgsGeometry.fromPointXY(qgis.core.QgsPointXY(float(campos[2]), float(campos[3]))))
                        f.setAttributes([str(campos[1]), str(campos[4])])
                        dp_Plazas.addFeature(f)
                    elif (str(campos[0]) == "Parque"):
                        qgis.core.QgsMessageLog.logMessage(str(campos[0]), 'Javi', qgis.core.Qgis.Warning)
                        f = qgis.core.QgsFeature()
                        f.setGeometry(qgis.core.QgsGeometry.fromPointXY(qgis.core.QgsPointXY(float(campos[2]), float(campos[3]))))
                        f.setAttributes([str(campos[1]), str(campos[4])])
                        dp_Parques.addFeature(f)
                    elif (str(campos[0]) == "Iglesia"):
                        qgis.core.QgsMessageLog.logMessage(str(campos[0]), 'Javi', qgis.core.Qgis.Warning)
                        f = qgis.core.QgsFeature()
                        f.setGeometry(qgis.core.QgsGeometry.fromPointXY(qgis.core.QgsPointXY(float(campos[2]), float(campos[3]))))
                        f.setAttributes([str(campos[1]), str(campos[4])])
                        dp_Iglesias.addFeature(f)
                    else:
                        qgis.core.QgsMessageLog.logMessage(str(campos[0]), 'Javi', qgis.core.Qgis.Warning)
                        f = qgis.core.QgsFeature()
                        f.setGeometry(qgis.core.QgsGeometry.fromPointXY(qgis.core.QgsPointXY(float(campos[2]), float(campos[3]))))
                        f.setAttributes([str(campos[1]), str(campos[4])])
                        dp_Puentes.addFeature(f)
                contar = contar + 1

        # Actualizar las capas para que los datos cargados estén en ellas.
        plazas.updateExtents()
        parques.updateExtents()
        iglesias.updateExtents()
        puentes.updateExtents()



        # Añadir las capas
        QgsProject.instance().addMapLayer(plazas)
        QgsProject.instance().addMapLayer(parques)
        QgsProject.instance().addMapLayer(iglesias)
        QgsProject.instance().addMapLayer(puentes)



        # Guardar las capas
        qgis.core.QgsVectorFileWriter.writeAsVectorFormat(plazas, rutaPlaza, "UTF-8", plazas.crs(), "ESRI Shapefile")
        qgis.core.QgsVectorFileWriter.writeAsVectorFormat(parques, rutaParque, "UTF-8", parques.crs(), "ESRI Shapefile")
        qgis.core.QgsVectorFileWriter.writeAsVectorFormat(iglesias, rutaIglesia, "UTF-8", iglesias.crs(), "ESRI Shapefile")
        qgis.core.QgsVectorFileWriter.writeAsVectorFormat(puentes, rutaPuentes, "UTF-8", puentes.crs(), "ESRI Shapefile")
        #Activar etiqueta y qbox para visualizar foto
        self.lbl_foto.setEnabled(True)
        self.GB_foto.setEnabled(True)

    def cargar_imagen(self,event):
        self.lbl_foto.clear()#Limpiar etiqueta

        fila=self.qtw_tabla.currentRow() #Ver en que fila ha pinchado el usuario
        ruta=self.qtw_tabla.item(fila,4).text()#Transformar el item de la cuarta columna en texto, es donde esta la ruta
        print("fila seleccionada"+str(fila))#Comprobar que la ruta esta bien
        print(ruta)

        label= QLabel( self.lbl_foto)


        pixmap = QPixmap(ruta).scaled(400,400, QtCore.Qt.KeepAspectRatio)

        label.setPixmap(pixmap)
        label.show()


    def closeEvent(self, event):
        # REiniciar todas las cosas por si ya hubiera datos en ellas
        # Eliminar lo que haya en la tabla
        while self.qtw_tabla.rowCount() > 0:
            self.qtw_tabla.removeRow(0)

        # Eliminar las rutas introducidas
        self.qfw_ruta.setFilePath("")
        self.qfw_rutaortofoto.setFilePath("")
        # Eliminar la imagen
        self.lbl_foto.clear()

        event.accept()  # let the window close