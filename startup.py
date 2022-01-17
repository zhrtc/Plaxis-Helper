import Plaxis
import xlwings as xw
from pytimedinput import pytimedinput

def GetPlaxisAnchorForces():
    Plaxis.Initialize()
    anchorOutputList =Plaxis.GenerateAnchorOutput()
    res, timeout = pytimedinput.timedInput("Press any char to disable data update in Excel. (5s to timeout)")
    if  res == None or len(res) == 0:
        if len(xw.apps) == 0 or len(xw.apps.active.books) == 0:
            xw.Book()
        activeBook = xw.apps.active.books.active
        if activeBook.sheets.active.name == "Forces Summary":
            targetSheet = activeBook.sheets.active
        else:
            targetSheet = activeBook.sheets.add()
        activeCell = targetSheet.book.app.selection
        activeCell.value = anchorOutputList


if  __name__ == "__main__":
    GetPlaxisAnchorForces()
    exit()
    while 1:
        res = input("Press any ENTRE to Start Plaxis Anchor Force Output...")
        if res != None and len(res) > 0:
            break
        GetPlaxisAnchorForces()