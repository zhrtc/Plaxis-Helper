from .PlxElements import *
from typing import List, Any, Callable
from plxscripting.plx_scripting_exceptions import PlxScriptingError
from .PhasesSelectDialog import PhasesSelectDialog
import logging

logger = logging.getLogger("Plaxis")

def GenerateAnchorOutput(anchorFilter: Callable[[PlxAnchor], bool] = None) -> List[Any]:
    print("\nStart Output\nExtracting Resuts...")
    PlxOutput = GV.PlxOutput
    timeout = 10

    phaseNameList = []
    startPhase = 0
    endPhase = len(GV.PlxPhasesList) - 1
    for i, plxPhase in enumerate(GV.PlxPhasesList):
        phaseNameList.append(f"{i+1:3}: {plxPhase.PhaseID}[{plxPhase.Name}]")
        tmpName = plxPhase.PhaseID.lower()
        if tmpName.find("final") >= 0 or tmpName.find("fel") >= 0:
            startPhase = i
    selectedPlxPhaseList:List[PlxPhase] = []
    phasesSelectDialog = PhasesSelectDialog(phaseNameList, [startPhase, endPhase],
                                            timeout = timeout, unlimited_items= True)
    while 1:
        try:
            dlgResult = phasesSelectDialog.exec()
            if dlgResult != 1:
                return None
            if len(phasesSelectDialog.SelectedItems) == 1:
                selectedPlxPhaseList.append(GV.PlxPhasesList[phasesSelectDialog.SelectedItems[0]])
                break
            else:
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
                if eleId in GV.PlxFixedAnchors.keys():
                    anchor = GV.PlxFixedAnchors[eleId]
                    anchor.UpdateCoordinates(x, y, localN)
                    anchor.UpdateMaxForce(phaseName, minF, maxF)
                    anchor.UpdateAxialForces(phaseName, f)
                    if anchor.Mark == 0 and i == 0:
                        if anchorFilter != None and \
                            anchorFilter(anchor):
                            anchor.Mark = 1
                        else:
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
                if eleId in GV.PlxNtNAnchors.keys():
                    anchor = GV.PlxNtNAnchors[eleId]
                    anchor.UpdateCoordinates(x, y, localN)
                    if localN == 1:
                        anchor.UpdateMaxForce(phaseName, minF, maxF)
                        anchor.UpdateAxialForces(phaseName, f)
                    if localN == 2:
                        if anchor.Mark == 0 and i == 0:
                            if anchorFilter != None and \
                                anchorFilter(anchor):
                                anchor.Mark = 1
                            else:
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

def GeneratePhasedAnchorOutput() -> List[Any]:
    print("\nStart Output\nExtracting Resuts...")
    PlxOutput = GV.PlxOutput
    timeout = 100

    phaseNameList = []
    for i, plxPhase in enumerate(GV.PlxPhasesList):
        phaseNameList.append(f"{i+1:3}: {plxPhase.PhaseID}[{plxPhase.Name}]")
    selectedPlxPhaseList:List[PlxPhase] = []
    phasesSelectDialog = PhasesSelectDialog(phaseNameList, None, timeout = timeout, rangeSelect=False)

    dlgResult = phasesSelectDialog.exec()
    if dlgResult != 1:
        return None
    for index in phasesSelectDialog.SelectedItems:
        selectedPlxPhaseList.append(GV.PlxPhasesList[index])

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
                print("    {} (Element ID {}) [X: {:.3f}, Y: {:.3f}]: Force {:.2f}: Max C {:.2f} at {}; Max T {:.2f} at {}".format(
                    anchor.Name, eleId, x, y, f, anchor.MaxCompression, anchor.MaxCompressionPhaseName,
                    anchor.MaxTension, anchor.MaxTensionPhaseName))
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
                    print("    {} (Element ID {}) [X: {:.3f}, Y: {:.3f}]: Force {:.2f}: Max C {:.2f} at {}; Max T {:.2f} at {}".format(
                        anchor.Name, eleId, x, y, f, anchor.MaxCompression, anchor.MaxCompressionPhaseName,
                        anchor.MaxTension, anchor.MaxTensionPhaseName))
        except PlxScriptingError as ex:
            if str(ex).find("The command did not deliver any results") >= 0 or str(ex).find("No \"Fixed-end anchor\" found") >= 0:
                print("\033[33m{}\033[0m".format('    ' + str(ex).replace('\n', '\n        ')))
            else:
                raise
    return None

last_selected_accumulatedPlxPhase = []
last_selected_selectedPlxPhaseList = []
def GetPhaseAccumulatedDeformation(section_points: tuple[tuple[float, float]], interval: float = 1,
                                   deformation_direction: str = "y", is_total: bool = True): #-> tuple(tuple(float, float, float)):
    ''' Input a series of point coordinates by (x, y) and a list of Phase,
        return a list of points of (x, y, value)
    '''
    global last_selected_accumulatedPlxPhase, last_selected_selectedPlxPhaseList
    print("\nStart Output\nExtracting Deformation Resuts...")
    PlxOutput = GV.PlxOutput
    if is_total:
        if deformation_direction == "y":
            result_type = PlxOutput.ResultTypes.Soil.Uy
        elif deformation_direction == "x":
            result_type = PlxOutput.ResultTypes.Soil.Ux
        else:
            print("Unsupported Result Direction.")
            return
    else:
        if deformation_direction == "y":
            result_type = PlxOutput.ResultTypes.Soil.PUy
        elif deformation_direction == "x":
            result_type = PlxOutput.ResultTypes.Soil.PUx
        else:
            print("Unsupported Result Direction.")
            return
    if section_points == None or len(section_points) < 2:
        print("A least 2 points to define a Section.")

    # select phases
    timeout = 9999

    phaseNameList = []
    tmp_last_selected_accumulatedPlxPhase = []
    tmp_last_selected_selectedPlxPhaseList = []
    for i, plxPhase in enumerate(GV.PlxPhasesList):
        phaseNameList.append(f"{i+1:3}: {plxPhase.PhaseID}[{plxPhase.Name}]")
        tmpName = plxPhase.PhaseID.lower()
        if not last_selected_accumulatedPlxPhase:
            if tmpName.startswith("gwl to"):
                tmp_last_selected_accumulatedPlxPhase.append(i-1)
        if not last_selected_selectedPlxPhaseList:
            if tmpName.startswith("ex to final") or tmpName.startswith("dismantle "):
                tmp_last_selected_selectedPlxPhaseList.append(i)
    if not last_selected_accumulatedPlxPhase:
        last_selected_accumulatedPlxPhase = tmp_last_selected_accumulatedPlxPhase
    if not last_selected_selectedPlxPhaseList:
        last_selected_selectedPlxPhaseList = tmp_last_selected_selectedPlxPhaseList
    phasesSelectDialog = PhasesSelectDialog(phaseNameList, last_selected_accumulatedPlxPhase,
                                            timeout = timeout, unlimited_items=True,
                                            title="Please select the Phases to be accumulated:")
    dlgResult = phasesSelectDialog.exec()
    if dlgResult != 1:
        return None
    last_selected_accumulatedPlxPhase = phasesSelectDialog.SelectedItems[:]
    phasesSelectDialog.SelectedItems.sort()
    accumulatedPlxPhaseList = [GV.PlxPhasesList[phase] for phase in phasesSelectDialog.SelectedItems]
    phasesSelectDialog = PhasesSelectDialog(phaseNameList, last_selected_selectedPlxPhaseList,
                                            timeout = timeout, unlimited_items=True,
                                            title="Please select the Phases to be exported:")
    dlgResult = phasesSelectDialog.exec()
    if dlgResult != 1:
        return None
    last_selected_selectedPlxPhaseList = phasesSelectDialog.SelectedItems[:]
    phasesSelectDialog.SelectedItems.sort()
    selectedPlxPhaseList = [GV.PlxPhasesList[phase] for phase in phasesSelectDialog.SelectedItems]
    sample_points = []
    for i in range(len(section_points) - 1):
        point1 = section_points[i]
        point2 = section_points[i+1]
        length = math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        segments = math.ceil(length / interval)
        for j in range(0, segments):
            inter_point = (point1[0] + (point2[0] - point1[0])/segments*j, \
                          point1[1] + (point2[1] - point1[1])/segments*j)
            sample_points.append(inter_point)
    sample_points.append(section_points[-1])
    
    results = {}
    results['position'] = sample_points
    sample_points_count = len(sample_points)
    accumulated_deformation = [0] * sample_points_count
    for phase in accumulatedPlxPhaseList:
        print(f"  Extracting data for Phase: [{phase.PhaseID}] (Accumulated)")
        for i, position in enumerate(sample_points):
            if i % 100 == 0:
                print(f"Exacting {i} out of {sample_points_count} points.")
            plaxis_result = PlxOutput.getsingleresult(phase.PlxObject, result_type, position)
            if plaxis_result == "not found":
                raise Exception("Used getsingleresult for point outside mesh.")
            accumulated_deformation[i] += plaxis_result
    print("accumulated ground settlements:")
    print(accumulated_deformation)
    for phase in selectedPlxPhaseList:
        print(f"  Extracting data for Phase: [{phase.PhaseID}] (Output)")
        phased_results = []
        for i, position in enumerate(sample_points):
            if i % 100 == 0:
                print(f"Exacting {i} out of {sample_points_count} points.")
            plaxis_result = PlxOutput.getsingleresult(phase.PlxObject, result_type, position)
            if plaxis_result == "not found":
                raise Exception("Used getsingleresult for point outside mesh.")
            phased_results.append(plaxis_result + accumulated_deformation[i])
        results[phase.PhaseID] = phased_results

    return results