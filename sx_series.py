#!/usr/bin/python
# -*- coding:utf-8 -*-

import xml.dom.minidom as Dom    
import codecs, sys
import os
import shutil
import time
import datetime
import xlrd

def Indent(dom, node, indent = 0):
    children = node.childNodes[:]
    if indent:
        text = dom.createTextNode('\n' + '\t' * indent)
        node.parentNode.insertBefore(text, node)
    if children:
        if children[-1].nodeType == node.ELEMENT_NODE:
            text = dom.createTextNode('\n' + '\t' * indent)
            node.appendChild(text)
        for n in children:
            if n.nodeType == node.ELEMENT_NODE:
                Indent(dom, n, indent + 1)

def dealprogram(programrecord):
    (seriescode,name,code,seq,searchname,licensingwindowstart,licensingwindowend,moviecode,fileurl,picturecode,picture)=(programrecord[1],programrecord[2],programrecord[3],programrecord[4],programrecord[6],programrecord[7],programrecord[8],programrecord[10],programrecord[11],programrecord[12],programrecord[13])
#设置默认的图片，可下载
    picture = 'ftp://iptv:iptvadmin@10.43.180.27//opt/wacos/CTMSData/picture/2020/11/23/20201123151956_100142470.png'
    doc = Dom.Document()  
    root_node = doc.createElement("ADI")  
    root_node.setAttribute("StaffID", "999999999")   
    root_node.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")  
    doc.appendChild(root_node)  
    objects_node = doc.createElement("Objects")
    object_node = doc.createElement("Object")
    
    object_node.setAttribute("Action","REGIST")
    object_node.setAttribute("Code",str(code))
    object_node.setAttribute("ElementType","Program")
    object_node.setAttribute("ID",str(code))

    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","Name")
    Property_value = doc.createTextNode(str(name)) 
    Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)
    
#    Property_node=doc.createElement("Property")
#    Property_node.setAttribute("Name","Description")
#    if description:
#        Property_value = doc.createTextNode(str(description)) 
#       Property_node.appendChild(Property_value)
#   object_node.appendChild(Property_node)

    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","LicensingWindowStart")
    Property_value = doc.createTextNode(str(licensingwindowstart)) 
    Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)
    
    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","LicensingWindowEnd")
    Property_value = doc.createTextNode(str(licensingwindowend)) 
    Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)

    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","SearchName")
    if searchname:
        Property_value = doc.createTextNode(str(searchname)) 
        Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)
    
    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","SeriesFlag")
    Property_value = doc.createTextNode("1") 
    Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)
    
    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","Status")
    Property_value = doc.createTextNode("1") 
    Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)


    objects_node.appendChild(object_node)
    
    if  moviecode:
        object_node = doc.createElement("Object")
       
        object_node.setAttribute("Action","REGIST")
        object_node.setAttribute("Code",str(moviecode))
        object_node.setAttribute("ElementType","Movie")
        object_node.setAttribute("ID",str(moviecode))

        Property_node=doc.createElement("Property")
        Property_node.setAttribute("Name","FileURL")
        Property_value = doc.createTextNode(str(fileurl)) 
        Property_node.appendChild(Property_value)
        object_node.appendChild(Property_node)
        
        Property_node=doc.createElement("Property")
        Property_node.setAttribute("Name","Type")
        Property_value = doc.createTextNode('1') 
        Property_node.appendChild(Property_value)
        object_node.appendChild(Property_node)
       
        objects_node.appendChild(object_node)
  
    if  picturecode:       
        object_node = doc.createElement("Object")
       
        object_node.setAttribute("Action","REGIST")
        object_node.setAttribute("Code",str(picturecode))
        object_node.setAttribute("ElementType","Picture")
        object_node.setAttribute("ID",str(picturecode))
      

        Property_node=doc.createElement("Property")
        Property_node.setAttribute("Name","FileURL")
        Property_value = doc.createTextNode(str(picture)) 
        Property_node.appendChild(Property_value)
        object_node.appendChild(Property_node)
#       copyfile(str(picture))
        objects_node.appendChild(object_node)
     
    root_node.appendChild(objects_node)  
    if  moviecode or picturecode :
        mappings_node = doc.createElement("Mappings")
        if moviecode :
            mapping_node = doc.createElement("Mapping")
            mapping_node.setAttribute("Action","REGIST")
            mapping_node.setAttribute("ElementCode",str(moviecode))
            mapping_node.setAttribute("ElementID",str(moviecode))
            mapping_node.setAttribute("ElementType","Movie")
            mapping_node.setAttribute("ParentCode",str(code))
            mapping_node.setAttribute("ParentID",str(code))
            mapping_node.setAttribute("ParentType","Program")
            mappings_node.appendChild(mapping_node)

        if picturecode :
            mapping_node = doc.createElement("Mapping")
            mapping_node.setAttribute("Action","REGIST")

            mapping_node.setAttribute("ElementCode",str(code))
            mapping_node.setAttribute("ElementID",str(code))
            mapping_node.setAttribute("ElementType","Program")
            mapping_node.setAttribute("ParentCode",str(picturecode))
            mapping_node.setAttribute("ParentID",str(picturecode))
            mapping_node.setAttribute("ParentType","Picture")
            mappings_node.appendChild(mapping_node)
            
            Property_node=doc.createElement("Property")
            Property_node.setAttribute("Name","Type")
            Property_value = doc.createTextNode('1') 
            Property_node.appendChild(Property_value)
            mapping_node.appendChild(Property_node)
        
        mapping_node = doc.createElement("Mapping")
        mapping_node.setAttribute("Action","REGIST")
        mapping_node.setAttribute("ElementCode",str(code))
        mapping_node.setAttribute("ElementID",str(code))
        mapping_node.setAttribute("ElementType","Program")
        mapping_node.setAttribute("ParentCode",str(seriescode))
        mapping_node.setAttribute("ParentID",str(seriescode))
        mapping_node.setAttribute("ParentType","Series")

        Property_node=doc.createElement("Property")
        Property_node.setAttribute("Name","Sequence")
        Property_value = doc.createTextNode(str(int(seq))) 
        Property_node.appendChild(Property_value)
        mapping_node.appendChild(Property_node)

        mappings_node.appendChild(mapping_node) 
        
        
        root_node.appendChild(mappings_node) 
    domcopy = doc.cloneNode(True)                      
    Indent(domcopy, domcopy.documentElement)    
    f = open('/root/xml/series/Program_'+str(code)+'.xml', 'wb')                     
    writer = codecs.lookup('utf-8')[3](f)       
    domcopy.writexml(writer, encoding = 'utf-8')
    domcopy.unlink() 
    f.close()
    print ('generate program %s success!' %(code))
    
def dealseries(seriesrecord):
    (name,code,SearchName,licensingwindowstart,licensingwindowend,Description,volumncount,kpeople,director)=(seriesrecord[0],seriesrecord[1],seriesrecord[2],seriesrecord[3],seriesrecord[4],seriesrecord[5],seriesrecord[7],seriesrecord[8],seriesrecord[9])
    picture = 'ftp://iptv:iptvadmin@10.43.180.27//opt/wacos/CTMSData/picture/2020/11/23/20201123151956_100142470.png'
    doc = Dom.Document()  
    root_node = doc.createElement("ADI")  
    root_node.setAttribute("StaffID", "999999999")   
    root_node.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")  
    doc.appendChild(root_node)  
    objects_node = doc.createElement("Objects")
    object_node = doc.createElement("Object")
    
    object_node.setAttribute("Action","REGIST")
    object_node.setAttribute("Code",str(code))
    object_node.setAttribute("ElementType","Series")
    object_node.setAttribute("ID",str(code))

    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","Name")
    Property_value = doc.createTextNode(str(name)) 
    Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)
    
    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","SearchName")
    if SearchName:
        Property_value = doc.createTextNode(str(SearchName)) 
        Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)
    
    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","LicensingWindowStart")
    Property_value = doc.createTextNode(str(licensingwindowstart)) 
    Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)
    
    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","LicensingWindowEnd")
    Property_value = doc.createTextNode(str(licensingwindowend)) 
    Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)
    
    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","Description")
    if Description:
        Property_value = doc.createTextNode(str(Description)) 
        Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)
    
    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","VolumnCount")
    Property_value = doc.createTextNode(str(int(volumncount))) 
    Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)

    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","ActorDisplay")
    if kpeople:
        Property_value = doc.createTextNode(str(kpeople)) 
        Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)
    
    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","Director")
    if director:
        Property_value = doc.createTextNode(str(director)) 
        Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)

    objects_node.appendChild(object_node)

    
    root_node.appendChild(objects_node) 

              
    domcopy = doc.cloneNode(True)                      
    Indent(domcopy, domcopy.documentElement)    
    f = open('/root/xml/series/Series_'+str(code)+'.xml', 'wb')    
    writer = codecs.lookup('utf-8')[3](f)       
    domcopy.writexml(writer, encoding = 'utf-8')
    domcopy.unlink() 
    f.close()
    
    print ('generate series %s success!' %(code))
    
#用xlrd模块读取excel数据，按行读取为列表    
workbook = xlrd.open_workbook(filename="/root/Series_202011231448.xlsx")
booksheet = workbook.sheet_by_index(0)
for i in range(1,booksheet.nrows):
    seriesrecord = booksheet.row_values(i)
    dealseries(seriesrecord)
    
workbook = xlrd.open_workbook(filename="/root/Series_Program_Movie_Poster.xlsx")
booksheet = workbook.sheet_by_index(0)
for i in range(1,booksheet.nrows):
    programrecord = booksheet.row_values(i)
    dealprogram(programrecord)

    