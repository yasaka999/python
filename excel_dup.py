import xlrd
import xlwt
 
# 用xlrd打开待处理的excel文件，读取待处理的数据
xlsfile = "/root/Series_Program_Movie_Poster.xlsx"
book = xlrd.open_workbook(xlsfile) # 获取Excel文件的book对象
 
# sheet0 = book.sheet_by_index(0) # 通过sheet索引获得sheet对象
# nrows = sheet0.nrows # 获取需要处理的数据的行数
 
sheet_name = book.sheet_names()[0] # 尝试通过sheet名字来获取，当然如果知道sheet名字就可以直接指定
sheet1 = book.sheet_by_name(sheet_name)
nrows = sheet1.nrows # 获取需要处理的数据的行数
 
# 用xlwt创建一个excel对象,并初始化第一行的数据，为写入数据做准备
book_new = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet_new = book_new.add_sheet("sheet1", cell_overwrite_ok=True)
#sheet_new.write(0, 0, "型号规格")
#sheet_new.write(0, 1, "数量")
line = 0 #后面自动写入的数据从第一行开始
 
 
# 处理逻辑, calc list用来记录行是否已经处理过的标志，先将所有待处理的行初始为“待处理”的标志
calc = []
for k in range(1,nrows+1): # 第一行是列名，无须处理
    calc.append(False)     # False表示对应的行未被处理过
 
# 读取数据进行合并处理，并写入xlwt创建的对象中
for i in range(1,nrows):
    if calc[i] == False:  # False表示对应的行未被处理过相加过，True表示已相加过，跳过这条数据
#        totol_i = sheet1.row_values(i)[1]  # 获取该行型号的初始数量
 
        for j in range(i+1, nrows):
            if sheet1.row_values(i)[1] == sheet1.row_values(j)[1]: #表示查到了同型号规格的数据
#                totol_i += sheet1.row_values(j)[1]
                calc[j] = True #将第j列标志为已处理
 
        #将计算的值写入新建的sheet_new
        for m in range(len(sheet1.row_values(j))):
            sheet_new.write(line,m,sheet1.row_values(i)[m])
#        sheet_new.write(line, 1, totol_i)
        line += 1
 
# 处理完毕，保存文件
book_new.save("/root/Series_Program.xlsx")
print ("convert success !")