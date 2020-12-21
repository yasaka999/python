#!/usr/bin/python
# -*- coding:utf-8 -*-

import xml.dom.minidom as Dom    
import codecs, sys
import cx_Oracle
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
    (name,code,searchname,licensingwindowstart,licensingwindowend,description,moviecode,fileurl,picturecode,picture)=(programrecord[0],programrecord[1],programrecord[3],programrecord[4],programrecord[5],programrecord[6],programrecord[7],programrecord[8],programrecord[9],programrecord[10])

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
     
    Property_node=doc.createElement("Property")
    Property_node.setAttribute("Name","Description")
    if description:
        Property_value = doc.createTextNode(str(description)) 
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
    Property_node.setAttribute("Name","SearchName")
    if searchname:
        Property_value = doc.createTextNode(str(searchname)) 
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
#            (moviecode,fileurl,programcode)=(programrecord[7],programrecord[8],programrecord[1])
            mapping_node = doc.createElement("Mapping")
            mapping_node.setAttribute("Action","REGIST")
            mapping_node.setAttribute("ElementCode",str(moviecode))
            mapping_node.setAttribute("ElementID",str(moviecode))
            mapping_node.setAttribute("ElementType","Movie")
            mapping_node.setAttribute("ParentCode",str(programcode))
            mapping_node.setAttribute("ParentID",str(programcode))
            mapping_node.setAttribute("ParentType","Program")
            mappings_node.appendChild(mapping_node)

        if picturecode :
            mapping_node = doc.createElement("Mapping")
            mapping_node.setAttribute("Action","REGIST")

            mapping_node.setAttribute("ElementCode",str(programcode))
            mapping_node.setAttribute("ElementID",str(programcode))
            mapping_node.setAttribute("ElementType","Program")
            mapping_node.setAttribute("ParentCode",str(picturecode))
            mapping_node.setAttribute("ParentID",str(picturecode))
            mapping_node.setAttribute("ParentType","Picture")
            
            mappings_node.appendChild(mapping_node)
                        
        root_node.appendChild(mappings_node) 
          
    domcopy = doc.cloneNode(True)                      
    Indent(domcopy, domcopy.documentElement)    
    f = open('/root/xml/Program_'+str(1000000000)+str(programcode)+'.xml', 'wb')                     
    writer = codecs.lookup('utf-8')[3](f)       
    domcopy.writexml(writer, encoding = 'utf-8')
    domcopy.unlink() 
    f.close()
    print ('generate %s success!' %(programcode))
   

#readExcelFile(filename)
# 打开工作表
workbook = xlrd.open_workbook(filename="/root/program_movie_poster.xlsx")
# 用索引取第一个工作薄
booksheet = workbook.sheet_by_index(0)
for i in range(1,booksheet.nrows):
    programrecord = booksheet.row_values(i)
    dealprogram(programrecord)
      
    



