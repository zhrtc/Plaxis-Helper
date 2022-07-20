from .PlxElements import *
from typing import List, Any
from plxscripting.plx_scripting_exceptions import PlxScriptingError
from .PhasesSelectDialog import PhasesSelectDialog

def GenerateAnchorOutput() -> List[Any]:
    print("\nStart Output\nExtracting Resuts...")
    PlxOutput = GV.PlxOutput
    timeout = 5

    phaseNameList = []
    startPhase = 0
    endPhase = len(GV.PlxPhasesList) - 1
    for i, plxPhase in enumerate(GV.PlxPhasesList):
        phaseNameList.append(f"{i+1:3}: {plxPhase.PhaseID}[{plxPhase.Name}]")
        tmpName = plxPhase.PhaseID.lower()
        if tmpName.find("final") >= 0 or tmpName.find("fel") >= 0:
            startPhase = i
    selectedPlxPhaseList:List[PlxPhase] = []
    phasesSelectDialog = PhasesSelectDialog(phaseNameList, [startPhase, endPhase], timeout = timeout)
    while 1:
        try:
            dlgResult = phasesSelectDialog.exec()
            if dlgResult != 1:
                return None
            phasesSelectDialog.SelectedItems.sort()
            startPhase = phasesSelectDialog.SelectedItems[0]
            endPhase = phasesSelectDialog.SelectedItems[1]
            parentPhase = GV.PlxPhasesList[endPhase]
            targetPhase = GV.PlxPhasesList[startPhase]
            isInLine = False
            while 1:
                selectedPlxPhaseList.append(parentPhase)
                if parentPhase == targetPhase:
                    isInLine = True
                    break
                parentPhase = parentPhase.Previous
            if isInLine == True:
                break
            else:
                print("start phase and end phase are not in the same tree.")
        except Exception as ex:
            print(ex)
    
    selectedPlxPhaseList.reverse()
    for i, plxPhase in enumerate(selectedPlxPhaseList):
        phaseName = plxPhase.Name
        print("{}: {}".format(phaseName, plxPhase.PhaseID))
        try:
            Fs = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.FixedEndAnchor.AnchorForce2D, 'node') 
            Xs = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.FixedEndAnchor.X, 'node') 
            Ys = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.FixedEndAnchor.Y, 'node') 
            MinFs = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.FixedEndAnchor.AnchorForceMin2D, 'node') 
            MaxFs = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.FixedEndAnchor.AnchorForceMax2D, 'node') 
            ElementIDs = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.FixedEndAnchor.ElementID, 'node') 
            LocalNumbers = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.FixedEndAnchor.LocalNumber, 'node') 
            tmp = zip(Fs, Xs, Ys, MinFs, MaxFs, ElementIDs, LocalNumbers)
            for f, x, y, minF, maxF, eleId, localN in tmp: 
                anchor = GV.PlxFixedAnchors[eleId]
                anchor.UpdateCoordinates(x, y, localN)
                anchor.UpdateMaxForce(phaseName, minF, maxF)
                anchor.UpdateAxialForces(phaseName, f)
                if anchor.Mark == 0:
                    anchor.Mark = i + 1
                print("    {} (Element ID {}): Force {:.2f}: Max C {:.2f} at {}; Max T {:.2f} at {}".format(anchor.Name, eleId, f,
                    anchor.MaxCompression, anchor.MaxCompressionPhaseName, anchor.MaxTension, anchor.MaxTensionPhaseName))
        except PlxScriptingError as ex:
            if str(ex).find("The command did not deliver any results") >= 0 or str(ex).find("No \"Fixed-end anchor\" found") >= 0:
                print("\033[33m{}\033[0m".format('    ' + str(ex).replace('\n', '\n        ')))
            else:
                raise

        try:
            Fs = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.NodeToNodeAnchor.AnchorForce2D, 'node') 
            Xs = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.NodeToNodeAnchor.X, 'node') 
            Ys = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.NodeToNodeAnchor.Y, 'node') 
            MinFs = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.NodeToNodeAnchor.AnchorForceMin2D, 'node') 
            MaxFs = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.NodeToNodeAnchor.AnchorForceMax2D, 'node') 
            ElementIDs = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.NodeToNodeAnchor.ElementID, 'node') 
            LocalNumbers = PlxOutput.getresults(plxPhase.PlxObject, PlxOutput.ResultTypes.NodeToNodeAnchor.LocalNumber, 'node') 
            tmp = zip(Fs, Xs, Ys, MinFs, MaxFs, ElementIDs, LocalNumbers)
            for f, x, y, minF, maxF, eleId, localN in tmp: 
                anchor = GV.PlxNtNAnchors[eleId]
                anchor.UpdateCoordinates(x, y, localN)
                if localN == 1:
                    anchor.UpdateMaxForce(phaseName, minF, maxF)
                    anchor.UpdateAxialForces(phaseName, f)
                    if anchor.Mark == 0:
                        anchor.Mark = i + 1
                    print("    {} (Element ID {}): Force {:.2f}: Max C {:.2f} at {}; Max T {:.2f} at {}".format(anchor.Name, eleId, f,
                        anchor.MaxCompression, anchor.MaxCompressionPhaseName, anchor.MaxTension, anchor.MaxTensionPhaseName))
        except PlxScriptingError as ex:
            if str(ex).find("The command did not deliver any results") >= 0 or str(ex).find("No \"Fixed-end anchor\" found") >= 0:
                print("\033[33m{}\033[0m".format('    ' + str(ex).replace('\n', '\n        ')))
            else:
                raise
    
    print("")
    resultStr = "Anchor Name             \tLevel \tLength\tSpacing\tForce   \tPreload \tMaterial Name       \tRemark\r\n"
    resultList = []
    resultList.append([item.strip() for item in resultStr.split("\t")])
    resultList[0][-1] = "Max. Force Phase"
    resultList[0].append("Preload Phase")
    tmpAnchors = list(GV.PlxFixedAnchors.values()) + list(GV.PlxNtNAnchors.values())
    for anchor in sorted(tmpAnchors, key=PlxAnchor.LevelCompare):
        if anchor.Y1 != None and anchor.Mark >= 1:
            resultStr += str(anchor)
            resultList.append(anchor.ToList())
    print(resultStr)
    return resultList
