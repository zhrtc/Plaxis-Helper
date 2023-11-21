import Plaxis
import xlwings as xw
from pytimedinput import pytimedinput

def GetPlaxisAnchorForces():
    #Plaxis.Initialize(All=True)
    Plaxis.Initialize(FixedAnchors = True, NtNAnchors= True, Phases= True, GotoStage = True, ConnectOutput = True)
    from Plaxis.PlaxisOutput import GenerateAnchorOutput
    for i in range(2):
        anchorOutputList = GenerateAnchorOutput(lambda anchor: abs(anchor.X1 - 100) < 1e-4 or abs(anchor.X1 - 164.4) < 1e-4)
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

def ModifyGWL():
    Plaxis.Initialize(All=False)
    from Plaxis.PlaxisInput import ModifyGWL
    ModifyGWL((45), 42)

def GetPhaseAccumulatedDeformation():
    section_info1 = {}
    section_info1["Section 1A Left"] = ((100, 62.3), (72, 62.3))
    section_info1["Section 1A Reservoir"] = ((72, 58.5), (0, 58.5))
    section_info1["Section 1A Right"] = ((152.8, 58.5), (250, 58.5))

    section_info2 = {}
    section_info2["Section 2 Left"] = ((100, 58.5), (0, 58.5))
    section_info2["Section 2 Right"] = ((164.4, 52.5), (250, 52.5))

    section_info3 = {}
    section_info3["Section 3 Left"] = ((97, 60), (73, 60))
    section_info3["Section 3 Reservoir"] = ((73, 58.5), (0, 58.5))
    section_info3["Section 3 Right"] = ((152.8, 54.5), (250, 54.5))

    section_info4 = {}
    section_info4["Section 4 Left"] = ((95.5, 60), (73, 60))
    section_info4["Section 4 Reservoir"] = ((73, 58.5), (0, 58.5))
    section_info4["Section 4 Right"] = ((152.8, 55.5), (250, 55.5))

    section_info5 = {}
    section_info5["Section 5 Left"] = ((100, 62), (0, 62))
    section_info5["Section 5 Right"] = ((164.4, 58), (250, 58))

    Plaxis.Initialize(Phases= True, ConnectOutput = True)
    project_name = Plaxis.GetProjectName()
    if project_name.find("Section 1A") > 0:
        section_info = section_info1
    elif project_name.find("Section 2") > 0:
        section_info = section_info2
    elif project_name.find("Section 3") > 0:
        section_info = section_info3
    elif project_name.find("Section 4") > 0:
        section_info = section_info4
    elif project_name.find("Section 5") > 0:
        section_info = section_info5
    else:
        raise Exception("Unrecognized Project Name")
    
    from Plaxis.PlaxisOutput import GetPhaseAccumulatedDeformation
    for name, points in section_info.items():
        print(f"Start Ouput for Section {name}")
        results = GetPhaseAccumulatedDeformation(points)
        if results:
            if len(xw.apps) == 0 or len(xw.apps.active.books) == 0:
                xw.Book()
            activeBook = xw.apps.active.books.active
            if name in activeBook.sheet_names:
                targetSheet = activeBook.sheets[name]
            else:
                targetSheet = activeBook.sheets.add(name)
            targetSheet.activate()
            targetSheet[0, 0].value = f"Ground Settlement Summary for {name}"
            targetSheet[0, 0].font.bold = True
            targetSheet[1, 0].value = "X (m)"
            targetSheet[1, 1].value = "Elevation (mPD)"
            phase_names = list(results.keys())[1:]
            index = 2
            for phase_name in phase_names:
                targetSheet[1, index].value = phase_name
                index += 1
            header_row = targetSheet[1, 0:(index)]
            header_row.wrap_text = True
            header_row.api.HorizontalAlignment = xw.constants.HAlign.xlHAlignCenter
            header_row.api.VerticalAlignment = xw.constants.VAlign.xlVAlignCenter
            header_row.autofit = True

            rows = len(results['position'])
            targetSheet[2:(2 + rows), 0:2].options(ndim = 2).value = results['position']
            index = 2
            for phase_name in phase_names:
                targetSheet[2:(2+rows), index].options(ndim = 2).value = [[x * 1000] for x in results[phase_name]]
                min_value = min(results[phase_name])
                for i, value in enumerate(results[phase_name]):
                    if abs(value - min_value) < 1e-5:
                        targetSheet[2+i, index].font.bold = True
                index += 1
            targetSheet[2:(2+rows), 0:(index)].number_format = "0.0"

            targetSheet.api.PageSetup.Zoom = False
            targetSheet.api.PageSetup.FitToPagesWide = 1
            targetSheet.api.PageSetup.FitToPagesTall  = False
            targetSheet.api.PageSetup.PaperSize = xw.constants.PaperSize.xlPaperA4
            targetSheet.api.PageSetup.PrintTitleRows = "$1:2"
            
        else:
            print("No results extracted.")

if  __name__ == "__main__":
    #GetPlaxisAnchorPreloadDeformation()
    #GetPlaxisAnchorForces()
    #GetPhaseAccumulatedDeformation()
    #SetSoilPermeability()
    ModifyGWL()
    exit()
    while 1:
        res = input("Press any ENTRE to Start Plaxis Anchor Force Output...")
        if res != None and len(res) > 0:
            break
        GetPlaxisAnchorForces()