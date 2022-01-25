# -*- coding: utf-8 -*-
import codecs
import csv

from qgis.utils import iface

zan =[]
zon = {}
zony_vse = []
np = []
nas_p = []
naselennye_punkty = ['г. Богданович','д. Алешина','с. Байны','с. Бараба','д. Билейка',
                    'д. Билейский рыбопитомник','д. Быкова','д. Верхняя Полдневая','с. Волковское','с. Гарашкинское',
                    'с. Грязновское','п. Грязновская','п. Дубровный','х. Дубровный','с. Ильинское','с. Кулики',
                    'с. Коменки','с. Кунарское','с. Каменноозерское','п. Куртугуз','п. Красный Маяк','д. Кашина',
                    'д. Кондратьева','п. Луч','д. Мелехина','д. Октябрина','д. Орлова','п. Полдневой',
                    'д. Поповка','д. Прищаново','д. Паршина','д. Раскатиха','с. Суворы','п. Сосновский','с. Троицкое',
                    'с. Тыгиш','с. Чернокоровское','д. Чудова','д. Черданцы','с. Щипачи','д. Щипачи',
                    ]

for clayer in iface.mapCanvas().layers():
    if clayer.name() == u'fz_nash':
        kptLayer = clayer
    if clayer.name() == u'zona_rosreestr':
        rosreestrLayer = clayer
# for zona in kptLayer.getFeatures():
    # zan.append(zona[3])
    # zony = set(zan)
kol_kontur_rosr = 0
kol_kontur_fz = 0
nas_punkt = ''
type_zone = ''
index = ''
data_reg = ''
reg_num = ''
ter_zona_pzz = ''
for punkt in naselennye_punkty:
    for nasp in rosreestrLayer.getFeatures():
        if punkt == nasp['nas_punkt']:
            
            zon_np = nasp['index'] + nasp['nas_punkt']
            # print(np, "NP")
            if zon_np not in np:
                np.append(zon_np)
                # print(zon_np, "ZONNP")
                kol_kontur_rosr = 0
                kol_kontur_fz = 0
                nas_punkt = nasp['nas_punkt'] 
                type_zone = nasp['type_zone']
                index = nasp['index']
                data_reg = nasp['data']
                reg_num = nasp['reg_num']
                ter_zona_pzz = nasp['index']
                for indnp in rosreestrLayer.getFeatures():
                    zon_npind = indnp['index'] + indnp['nas_punkt']
                    if zon_npind == zon_np:
                        kol_kontur_rosr += 1

                for indfz in kptLayer.getFeatures():
                    zon_npifz = indfz['ZONA_PS'] + indfz['np_punkt_n']
                    if zon_npifz == zon_np:
                        
                        kol_kontur_fz += 1
                 
                zona_naspunkt ={'nas_punkt': nas_punkt, 'type_zone': type_zone, 'index': index,
                                'ter_zona_pzz': ter_zona_pzz, 'kol_kontur_fz': kol_kontur_fz, 'data_reg': data_reg,
                                'reg_num': reg_num, 'kol_kontur_rosr': kol_kontur_rosr}  
                # print(zona_naspunkt)                
                zony_vse.append(zona_naspunkt)    
            

# print(zony_vse)
zony = ['nas_punkt', 'type_zone', 'index', 'ter_zona_pzz', 'kol_kontur_fz', 'data_reg', 'reg_num', 'kol_kontur_rosr']

with codecs.open('example4.csv', 'w', encoding='cp1251') as csvfile:
    fieldnames = zony
    writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames)
    writer.writeheader()
    for i in zony_vse:
        writer.writerow(i)
            
                    