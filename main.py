# djvused -e "set-outline C:\Users\Admin\Desktop\cxz.txt" -s "C:\Users\Admin\Desktop\cxz.djvu"
# OutlineTool -s:C:\Users\Admin\Desktop\cxz.txt -t:C:\Users\Admin\Desktop\asd.pdf
from xml.dom import minidom

# file = open('C:/Users/Admin/Desktop/asd.bookmarks', 'r')

doc = minidom.parse('C:/Users/Admin/Desktop/asd.bookmarks')
# print(doc.getElementsByTagName('bookmarks')[0].getElementsByTagName('bookmark')[0].attributes['page'].value)

bookmarks = doc.getElementsByTagName('bookmarks')[0].getElementsByTagName('bookmark')
result = "(bookmarks\n"
for bookmark in bookmarks:
    title = bookmark.attributes['title'].value
    page = bookmark.attributes['page'].value

    result += '("' + title + '""#' + page + '")\n'

result += ")"

file = open('cxz.txt', 'w')
file.write(result)
file.close()

# (bookmarks
#  ("1 first chapter" "#10" 
#  ("1.1 first section" "#11" 
#  ("1.1.1 first subsection" "#12" ))
#  ("1.2 second section" "#13" ))
#  ("2 second chapter" "#14" 
#  ("2.1 first section" "#16" )
#  ("2.2 second section" "#13" ))
# )

from PyPDF2 import PdfFileWriter, PdfFileReader
output = PdfFileWriter()
input1 = PdfFileReader(open('C:/Users/Admin/Desktop/asd.pdf', 'rb'))

# output.addPage(input1.getPage(0))
# input2 = PdfFileReader(open('C:/Users/Admin/Desktop/asd.pdf', 'rb'))
# output.addPage(input2.getPage(0))

# parent = output.addBookmark('Introduction', 0) # add parent bookmark
# output.addBookmark('Hello, World', 0, parent) # add child bookmark
# output = PdfFileWriter()

pages = input1.numPages
output.addPage(0)
output.addBookmark('Hello, World', 0) # add child bookmark
for page in range(pages):
    output.addPage(input1.getPage(page))
    with open('C:/Users/Admin/Desktop/qwe.pdf','wb') as outputstream: #creating result 
        output.write(outputstream) #writing to result pdf 

outputstream.close()
