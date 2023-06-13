import Plaxis
import xlwings as xw
from pytimedinput import pytimedinput

def GetPlaxisAnchorForces():
    Plaxis.Initialize(All=True)
    from Plaxis.PlaxisOutput import GenerateAnchorOutput
    anchorOutputList = GenerateAnchorOutput()
    if anchorOutputList is None or len(anchorOutputList) == 0:
        print("No output data generated!")
    else:
        res, timeout = pytimedinput.timedInput("Press any char to disable data update in Excel. (5s to timeout)")
        if  res is None or len(res) == 0:
            if len(xw.apps) == 0 or len(xw.apps.active.books) == 0:
                xw.Book()
            activeBook = xw.apps.active.books.active
            if activeBook.sheets.active.name == "Forces Summary":
                targetSheet = activeBook.sheets.active
            else:
                targetSheet = activeBook.sheets.add()
            activeCell = targetSheet.book.app.selection
            activeCell.value = anchorOutputList

def GetPlaxisAnchorPreloadDeformation():
    Plaxis.Initialize(All=True)
    from Plaxis.PlaxisOutput import UpdatePrestressDeformation
    UpdatePrestressDeformation()


def SetSoilPermeability():
    Plaxis.Initialize(Materials=True)
    from Plaxis.PlaxisInput import SetSoilProperties
    SetSoilProperties([" Fill ", " CDG( |$)"],
                      [Plaxis.PlxSoilMaterial.Kx, Plaxis.PlxSoilMaterial.Ky],
                      [5.5e-6, 1e-5])

if  __name__ == "__main__":
    GetPlaxisAnchorPreloadDeformation()
    #GetPlaxisAnchorForces()
    #SetSoilPermeability()
    exit()
    while 1:
        res = input("Press any ENTRE to Start Plaxis Anchor Force Output...")
        if res != None and len(res) > 0:
            break
        GetPlaxisAnchorForces()