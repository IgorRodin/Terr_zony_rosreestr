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


def __init__(iface):
    iface = iface

dirlist = QFileDialog.getExistingDirectory(None, "Выбрать папку", ".")
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
    # print(attrib)   
    global nomer, xk, yk
    point = QPointF()
    fet = QgsFeature()
    for ent_sp in contura:
        if ent_sp.tag == 'entity_spatial':
            for syny in ent_sp.getchildren():
                if syny.tag == 'spatials_elements':
                    nodes = syny.getchildren()
                    for syn in nodes:
                        if syn.tag == 'spatial_element':
                            contur = QPolygonF()
                            for synak in syn.getchildren():
                                if synak.tag == 'ordinates':
                                    deti_syn = synak.getchildren()
                                    for synsyn in deti_syn:
                                        if synsyn.tag == 'ordinate':
                                            for coor in synsyn.getchildren():
                                                if coor.tag == 'x':
                                                    xk = coor.text
                                            for coor in synsyn.getchildren():
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
        uchastkizon = []
        nomer = attrib[0]

        for f in vl.getFeatures():
            diff = QgsFeature()
            multi_polygon = []

            for i in vl.getFeatures():
                if f.id() != i.id() and f['reg_num'] == i['reg_num']:
                    if i.geometry().intersects(f.geometry()):
                        try:
                            multi_polygon.append(i.geometry().asPolygon())
                            # print("POLYGON")
                        except TypeError:
                            for b in i.geometry().asMultiPolygon():
                                # print(b, "BB")
                                multi_polygon.append(b)
                                print("MULT")

            geo = QgsGeometry.fromMultiPolygonXY(multi_polygon)

            diff.setGeometry(f.geometry().difference(geo))

            attributes = f.attributes()
            diff.setAttributes(attributes)
            pr.addFeatures([diff])
            pr.deleteFeatures([f.id()])
            vl.updateExtents()
            uchastkizon.append(diff)
    # print(nomer, "NN")    
    QgsProject.instance().addMapLayer(vl)
    print("UZ")
    ochistka(vl, pr, nomer)

def ochistka(vl, pr, num):
    for f in vl.getFeatures():
        if f['reg_num'] == num:
            fnom = 0
            inom = 0
            for i in vl.getFeatures():
                if f.id() != i.id() and f['reg_num'] == i['reg_num']:
                    if i.geometry().intersects(f.geometry()):
                        for fn in f.geometry().vertices():
                            fnom += 1
                        for ifn in i.geometry().vertices():
                            inom += 1
                        if fnom > inom:
                            pr.deleteFeatures([i.id()])
                        else:
                            pr.deleteFeatures([f.id()])

    # for f in vl.getFeatures():
    # print(f['reg_num'], "OCHISTKA F")
    # if f['reg_num'] == num:
    # fnom = 0
    # inom = 0
    # for i in vl.getFeatures():
    # print(i['reg_num'], "OCHISTKA I")
    # if f != i and i['reg_num'] == num:
    # print("OCH")
    # if i.geometry().intersects(f.geometry()):
    # for fn in f.geometry().vertices():
    # fnom+=1
    # for ifn in i.geometry().vertices():
    # inom+=1
    # if fnom > inom:
    # pr.deleteFeatures([i.id()])
    # else:
    # pr.deleteFeatures([f.id()])


def attributy(in_file):
    global contura, reg_data
    attrib = []
    filename = open(in_file)
    tree = etree.parse(filename)
    root = tree.getroot()
    code_zone = ''
    reg_num = ""
    name_by_doc = ""
    type_zone = ''
    index = ''
    nas_punkt = ''

    for elem in root.iter():
        if elem.tag == 'reg_numb_border':
            reg_num = elem.text
        if elem.tag == 'registration_date':
            reg_data = elem.text
        if elem.tag == 'name_by_doc':
            name_by_doc = elem.text
            # for key in dikt:
            # if key in name_by_doc:
            # nas_punkt = dikt[key]
        if elem.tag == 'type_zone':
            for typ_zon in elem.getchildren():
                if typ_zon.tag == 'value':
                    type_zone = typ_zon.text
        if elem.tag == 'type_zone':
            for typ_zon in elem.getchildren():
                if typ_zon.tag == 'code':
                    code_zone = typ_zon.text
        if elem.tag == 'index':
            # print(elem.text,"index")
            index = elem.text
        if elem.tag == 'contour':
            contura = elem.getchildren()
    attrib = [reg_num, name_by_doc, type_zone,
              code_zone, index, nas_punkt, reg_data]

    contur_sloy(contura, vl, attrib)
    del tree
    filename.close()


for in_file in glob.glob(os.path.join(dirlist, '*.xml')):
    if not in_file:
        pass
    else:
        print(in_file, "FAIL")
        attributy(in_file)
