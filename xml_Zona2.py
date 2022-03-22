# -*- coding: utf-8 -*-

import glob
import os.path
import xml.etree.ElementTree as etree
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog
from qgis.PyQt.QtGui import *
from qgis.core import (QgsProject,
                       QgsFeature, QgsGeometry,
                       QgsCoordinateReferenceSystem,
                       QgsVectorLayer, QgsField)
from qgis.utils import iface
from time import time

dirlist = QFileDialog.getExistingDirectory(None, "Выбрать папку", ".")
tic = time()
sridob = iface.mapCanvas().mapSettings().destinationCrs().authid()
srid = QgsCoordinateReferenceSystem(sridob)
vl = QgsVectorLayer("Polygon", "temporary_terzona", "memory")
pr = vl.dataProvider()
vl.setCrs(srid)
pr.addAttributes([QgsField("reg_num", QVariant.String), QgsField("name_by_doc", QVariant.String),
                  QgsField("type_zone", QVariant.String), QgsField("code_zone", QVariant.String),
                  QgsField("index", QVariant.String), QgsField("nas_punkt", QVariant.String),
                  QgsField("data", QVariant.String)])
vl.updateFields()

def contur_sloy(contura, vl, attrib):
    # global nomer, xk, yk
    xk = ''
    yk = ''
    contur = []
    point = QPointF()
    fet = QgsFeature()
    for cont in contura:
        if cont.tag == 'contour':
            for ent_sp in cont.getchildren():
                if ent_sp.tag == 'entity_spatial':
                    for spat_els in ent_sp.getchildren():
                        if spat_els.tag == 'spatials_elements':
                                for spat_el in spat_els.getchildren():
                                    if spat_el.tag == 'spatial_element':
                                        contur = QPolygonF()
                                        for ordins in spat_el.getchildren():
                                            if ordins.tag == 'ordinates':
                                                for ordin in ordins.getchildren():
                                                    if ordin.tag == 'ordinate':
                                                        for coor in ordin.getchildren():
                                                            if coor.tag == 'x':
                                                                xk = coor.text
                                                        for coor in ordin.getchildren():
                                                            if coor.tag == 'y':
                                                                yk = coor.text

                                                        xcoor = float(xk)
                                                        ycoor = float(yk)
                                                        point.setX(ycoor)
                                                        point.setY(xcoor)
                                                        contur.append(point)
                                        poly = QgsGeometry.fromQPolygonF(contur)
                                        fet.setAttributes(attrib)
                                        fet.setGeometry(poly)
                                        pr.addFeatures([fet])
                                        vl.updateExtents()

    for f in vl.getFeatures():
        diff = QgsFeature()
        multi_polygon = []
        for i in vl.getFeatures():
            if f.id() != i.id() and f['reg_num'] == i['reg_num']:
                if i.geometry().intersects(f.geometry()):
                    try:
                        multi_polygon.append(i.geometry().asPolygon())
                    except TypeError:
                        for b in i.geometry().asMultiPolygon():
                            multi_polygon.append(b)
                            print("MULT")

        geo = QgsGeometry.fromMultiPolygonXY(multi_polygon)
        diff.setGeometry(f.geometry().difference(geo))
        attributes = f.attributes()
        diff.setAttributes(attributes)
        pr.addFeatures([diff])
        pr.deleteFeatures([f.id()])
        vl.updateExtents()

    nomer = attrib[0]
    QgsProject.instance().addMapLayer(vl)
    ochistka(vl, pr, nomer)
    del attrib

def ochistka(vl, pr, num):

    for f in vl.getFeatures():
        if f['reg_num'] == num:
            fnom = 0
            inom = 0
            for i in vl.getFeatures():
                if f.id() != i.id() and f['reg_num'] == i['reg_num']:
                    if i.geometry().intersects(f.geometry()):
                        # cn = str(f.geometry().vertices())
                        # cni = str(i.geometry().vertices())
                        # fnom = len(f.geometry().vertices())
                        # inom = len(f.geometry().vertices())
                        for fn in f.geometry().vertices():
                            fnom += 1
                        for ifn in i.geometry().vertices():
                            inom += 1
                        if fnom > inom:
                            pr.deleteFeatures([i.id()])
                        else:
                            pr.deleteFeatures([f.id()])

def attributy(in_file):
    # global contura, reg_data
    with open(in_file) as filename:
        # filename = open(in_file)
        tree = etree.parse(filename)
        # traci = time()
        # print(traci - tam, "ETREE root")
        root = tree.getroot()
        print(root.tag)
        if root.tag == 'extract_about_zone':
            code_zone = ''
            reg_num = ""
            name_by_doc = ""
            type_zone = ''
            index = ''
            nas_punkt = ''
            reg_data = ''
            contura = ''

            for elem in root.iter():
                if elem.tag == 'reg_numb_border':
                    reg_num = elem.text
                if elem.tag == 'registration_date':
                    reg_data = elem.text
                if elem.tag == 'name_by_doc':
                    name_by_doc = elem.text
                if elem.tag == 'type_zone':
                    for typ_zon in elem.getchildren():
                        if typ_zon.tag == 'value':
                            type_zone = typ_zon.text
                if elem.tag == 'type_zone':
                    for typ_zon in elem.getchildren():
                        if typ_zon.tag == 'code':
                            code_zone = typ_zon.text
                if elem.tag == 'index':
                    index = elem.text
                if elem.tag == 'contours':
                    contura = elem.getchildren()

            attrib = [reg_num, name_by_doc, type_zone,
                      code_zone, index, nas_punkt, reg_data]
            contur_sloy(contura, vl, attrib)
            # elem.clear()

            del tree
            # del attrib
            filename.close()
        else:
            print("Eto ne zony")

for in_file in glob.glob(os.path.join(dirlist, '*.xml')):
    # tam = time()
    # print(tam - tama, "ATTRR")
    if not in_file:
        pass
    else:
        # print(in_file, "FAIL")
        attributy(in_file)

tar = time()
print((tar - tic)/60, "ATTRRIBYT")
    # del in_file
