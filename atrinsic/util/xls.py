import xlrd
import pyExcelerator as xl

import datetime


def get_rows(filename):
    ''' Helper method to return the rows of a Spreadsheet'''

    book = xlrd.open_workbook(filename)
    sh = book.sheet_by_index(0)
    res = []
    for i in range(sh.nrows):
        line = []
        for j in sh.row(i):
            if j.ctype == xlrd.XL_CELL_DATE:
                line.append(datetime.datetime(*xlrd.xldate_as_tuple(j.value,book.datemode)[:6]).strftime("%Y-%m-%d"))
            else:
                if isinstance(j.value, unicode):
                    line.append(j.value)
                else:
                    line.append(str(j.value))

        res.append(line)

    return res

def get_rows_string(input):
    file_id,file_path = tempfile.mkstemp()
    a = open(file_path,"wb")
    a.write(input)
    a.close()
    output = get_rows(file_path)
    os.unlink(file_path)
    return output
    
def write_rows(filename,rows):
    ''' Creates a Spreadsheet with the specified rows ''' 

    mydoc = xl.Workbook()
    mysheet = mydoc.add_sheet("Sheet")
    for row_num,row in enumerate(rows):
        for col,value in enumerate(row):
            mysheet.write(row_num,col,value)
            
    mydoc.save(filename)

import tempfile
def write_rows_string(rows):
    file_id,file_path = tempfile.mkstemp()
    write_rows(file_path,res)
    res = open(file_path).read()
    os.unlink(file_path)

if __name__ == "__main__":
    import random
    print "creating an xls document first"
    rows = []
    for x in range(0,20):
        row = []
        for y in range(0,5):
            row.append(random.randint(0,10))

        rows.append(row)

    print rows
    write_rows("/tmp/test.xls",rows)

    rows2 = get_rows("/tmp/test.xls")

    print rows2
    print rows==rows2

    
