from .PlxElements import *
from typing import List, Any
from plxscripting.plx_scripting_exceptions import PlxScriptingError
from .PhasesSelectDialog import PhasesSelectDialog
import logging

logger = logging.getLogger("Plaxis")

def GenerateAnchorOutput() -> List[Any]:
    print("\nStart Output\nExtracting Resuts...")
    PlxOutput = GV.PlxOutput
    timeout = 1

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
                if anchor.Mark == 0 and i == 0:
                    anchor.Mark = 1
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
                    if anchor.Mark == 0 and i == 0:
                        anchor.Mark = 1
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
        if anchor.Y1 != None and anchor.Mark == 1:
            resultStr += str(anchor)
            resultList.append(anchor.ToList())
    print(resultStr)
    return resultList

def UpdatePrestressDeformation():
    logger.info("Obtain Preload Information")
    PlxOutput = GV.PlxOutput
    for item in GV.PlxFixedAnchors.values():
        logger.info(f"Processing {item.Name}")
        if item.PrestressPhaseName != None:
            Xs = PlxOutput.getresults(item.PlxObject, item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.FixedEndAnchor.X, 'node')
            Ys = PlxOutput.getresults(item.PlxObject, item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.FixedEndAnchor.Y, 'node')
            PUxs = PlxOutput.getresults(item.PlxObject, item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.FixedEndAnchor.PUx, 'node')
            LocalNumbers = PlxOutput.getresults(item.PlxObject, item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.FixedEndAnchor.LocalNumber, 'node')

            tmp = zip(Xs, Ys, PUxs, LocalNumbers)
            for x, y, pux, ln in tmp:
                if  ln == 1:
                    item.PrestressDeformX1 = pux
            
    for item in GV.PlxNtNAnchors.values():
        logger.info(f"Processing {item.Name}")
        if item.PrestressPhaseName != None:
            Xs = PlxOutput.getresults(item.PlxObject, item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.NodeToNodeAnchor.X, 'node')
            Ys = PlxOutput.getresults(item.PlxObject, item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.NodeToNodeAnchor.Y, 'node')
            PUxs = PlxOutput.getresults(item.PlxObject, item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.NodeToNodeAnchor.PUx, 'node')
            LocalNumbers = PlxOutput.getresults(item.PlxObject, item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.NodeToNodeAnchor.LocalNumber, 'node')

            tmp = zip(Xs, Ys, PUxs, LocalNumbers)
            for x, y, pux, ln in tmp:
                if  ln == 1:
                    item.PrestressDeformX1 = pux
                elif ln == 2:
                    item.PrestressDeformX2 = pux

    tmpAnchors = list(GV.PlxFixedAnchors.values()) + list(GV.PlxNtNAnchors.values())
    resultStr = "Anchor Name \tLevel \tPreload Stage \tPreload Value \tX1 \tY1 \tDeformation \tX2 \tY2 \tDeformation\r\n"
    for anchor in sorted(tmpAnchors, key=PlxAnchor.LevelCompare):
        if anchor.PrestressDeformX1 != None:
            resultStr += f"{anchor.Name}\t{anchor.Y1}\t{anchor.PrestressPhaseName}\t{anchor.PrestressForce:8.2f}\t{anchor.X1:8.3f}\t{anchor.Y1:8.2f}\t{anchor.PrestressDeformX1*1000:8.1f}"
            if anchor.PrestressDeformX2 != None:
                resultStr += f"\t{anchor.X2:8.3f}\t{anchor.Y2:8.2f}\t{anchor.PrestressDeformX2*1000:8.1f}"
            resultStr += "\r\n"
    print(resultStr)

# def UpdatePrestressDeformation():
#     PlxOutput = GV.PlxOutput
#     PhasedDeformation = {}
#     for item in GV.PlxFixedAnchors.values():
#         if item.PrestressPhaseName != None:
#             deformation = None
#             if item.PrestressPhaseName in PhasedDeformation:
#                 deformation = PhasedDeformation[item.PrestressPhaseName]
#             else:    
#                 x = PlxOutput.getresults(item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.Soil.X, 'node')
#                 y = PlxOutput.getresults(item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.Soil.Y, 'node')
#                 PUx = PlxOutput.getresults(item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.Soil.PUx, 'node')
#                 deformation = zip(x, y, PUx)
#                 PhasedDeformation[item.PrestressPhaseName] = deformation
#             if deformation == None:
#                 continue
            
#             for x, y, PUx in deformation:
#                 if abs(x - item.X1) < 1e-4 and abs(y - item.Y1) < 1e-4:
#                     item.PrestressDeformX1 = PUx

#     for item in GV.PlxNtNAnchors.values():
#         if item.PrestressPhaseName != None:
#             deformation = None
#             if item.PrestressPhaseName in PhasedDeformation:
#                 deformation = PhasedDeformation[item.PrestressPhaseName]
#             else:    
#                 x = PlxOutput.getresults(item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.Soil.X, 'node')
#                 y = PlxOutput.getresults(item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.Soil.Y, 'node')
#                 PUx = PlxOutput.getresults(item.PrestressPhase.PlxObject, PlxOutput.ResultTypes.Soil.PUx, 'node')
#                 deformation = zip(x, y, PUx)
#                 PhasedDeformation[item.PrestressPhaseName] = deformation
#             if deformation == None:
#                 continue
            
#             for x, y, PUx in deformation:
#                 if abs(x - item.X1) < 1e-4 and abs(y - item.Y1) < 1e-4:
#                     item.PrestressDeformX1 = PUx
#                 if abs(x - item.X2) < 1e-4 and abs(y - item.Y2) < 1e-4:
#                     item.PrestressDeformX2 = PUx

#     tmpAnchors = list(GV.PlxFixedAnchors.values()) + list(GV.PlxNtNAnchors.values())
#     resultStr = "Anchor Name \tLevel \tPreload Stage \tPreload Value \tX1 \tY1 \tDeformation \tX2 \tY2 \tDeformation\r\n"
#     for anchor in sorted(tmpAnchors, key=PlxAnchor.LevelCompare):
#         if anchor.PrestressPhaseName != None:
#             resultStr += f"{anchor.Name}\t{anchor.Y1}\t{anchor.PrestressPhaseName}\t{anchor.PrestressForce:8.2f}\t{anchor.X1:8.3f}\t{anchor.Y1:8.2f}\t{anchor.PrestressDeformX1:8.2f}"
#             if anchor.PrestressDeformX2 != None:
#                 resultStr += f"\t{anchor.X2:8.3f}\t{anchor.Y2:8.2f}\t{anchor.PrestressDeformX2:8.2f}"
#             resultStr += "\r\n"
#     print(resultStr)