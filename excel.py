import xlwings as xw
app = xw.apps.active

def func1():
    count = 0
    for wb in app.books:
        #wb.save()
        for sheet in wb.sheets:
            if sheet.visible:
                count += 1
                print(wb.name + "\t" + sheet.name)
    print(f"total opened sheets: {count}")

def func2():
    bookSummary = app.books["Plaxis Summary.xlsx"]
    sheetSummary = bookSummary.sheets["ForceSizeSummary"]
    rangeNames = sheetSummary.range("$H$7:$H$68")
    print(rangeNames.value)

    bookTarget = app.books["Strut Waling Weld.xlsx"]
    bookTarget.activate()
    sheet1 = bookTarget.sheets["S.Welding T1L1A"]
    sheet2 = bookTarget.sheets["W.Stiffener T1L1A"]

    for name in rangeNames.value[1:]:
        if name[0:5] == "Strut":
            name = name.replace("Strut ", "")
            if name == "T1L1A":
                continue
            print("Copying sheet " + name)
            sheet1.copy(name=f"S.Welding {name}")
            sheet2.copy(name=f"W.Stiffener {name}")

def func3():
    wb = app.books.active
    for ws in wb.sheets:
        if ws.visible and ws.name[:3] == "S.W":
            print(ws.name)

def func4():
    import time 
    import pyautogui
    print("staring waiting...")
    time.sleep(5)
    print("start typing....")
    pyautogui.write("600.0\t 550.0\t\t\t\t 600.0\t 392.9\t\t\t\t 600.0\t 235.7\t\t\t\t 600.0\t 78.6\t\t\t\t 600.0\t -78.6\t\t\t\t 600.0\t -235.7\t\t\t\t 600.0\t -392.9\t\t\t\t 600.0\t -550.0\t\t\t\t -600.0\t 550.0\t\t\t\t -600.0\t 392.9\t\t\t\t -600.0\t 235.7\t\t\t\t -600.0\t 78.6\t\t\t\t -600.0\t -78.6\t\t\t\t -600.0\t -235.7\t\t\t\t -600.0\t -392.9\t\t\t\t -600.0\t -550.0\t\t\t\t -428.6\t -550.0\t\t\t\t -257.1\t -550.0\t\t\t\t -85.7\t -550.0\t\t\t\t 85.7\t -550.0\t\t\t\t 257.1\t -550.0\t\t\t\t 428.6\t -550.0\t\t\t\t -428.6\t 550.0\t\t\t\t -257.1\t 550.0\t\t\t\t -85.7\t 550.0\t\t\t\t 85.7\t 550.0\t\t\t\t 257.1\t 550.0\t\t\t\t 428.6\t 550.0\t\t\t\t ", interval=0.1)

func4()

