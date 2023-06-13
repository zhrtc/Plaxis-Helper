from plxscripting.easy import *
import plxscripting.requests.exceptions6
from .ServerConfig import ServerConfig
from .CommonFuncs import *
from .PlxElements import *
#from .PlaxisOutput import *
import logging

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)

def SwitchToStagedConstruction(maxTryTimes: int = 3):
    succeed = False
    for i in range(maxTryTimes):
        try:
            GV.PlxInput.gotostages()
        except plxscripting.requests.exceptions.Timeout as ex:
            if i == maxTryTimes - 1:
                raise ex
            

def Initialize(serverConfig:ServerConfig = ServerConfig(), All:bool = False, Anchors:bool = False,
               Plates:bool = False, Materials:bool = False, Phases:bool = False, GotoStage:bool = False,
               ConnectOutput:bool = False):
    GV.Reset()
    logger = logging.getLogger("Plaxis")
    logger.setLevel(logging.INFO)
    logger.info("Initialize Plaxis Module")

    try:
        logger.info("Connect to Plaxis Input")
        GV.SeverInput, GV.PlxInput = new_server(serverConfig.Host, serverConfig.InputPort, password=serverConfig.InputPassword, request_timeout=serverConfig.RequestTimeout)
        logger.info("Connect to Plaxis Input Succeed!")
    except Exception as ex:
        logger.warning("Connect to Plaxis Input Failed!")
        logger.warning(ex)
        GV.SeverInput, GV.PlxInput = None, None
        exit()

    if All or ConnectOutput:
        try:
            logger.info("Connect to Plaxis Output")
            GV.SeverOutput, GV.PlxOutput = new_server(serverConfig.Host, serverConfig.OutputPort, password=serverConfig.OutputPassword, request_timeout=serverConfig.RequestTimeout)
            logger.info("Connect to Plaxis Output Succeed!")
        except:
            logger.warning("Connect to Plaxis Output Failed!")
            logger.warning(ex)
            GV.SeverOutput, GV.PlxOutput = None, None
            exit()

    PlxInput = GV.PlxInput
    GV.PlxInput.SwitchToStagedConstruction = SwitchToStagedConstruction

    if All or GotoStage:
        PlxInput.gotostages()

    if All or Phases:
        logger.info("Enumerate Phases...")
        for phase in PlxInput.Phases:
            obj = PlxPhase(phase)
            logger.info(f"    {obj.PhaseID} [{obj.Name}]")
            GV.PlxPhases[obj.Name] = obj
        for phaseObj in GV.PlxPhases.values():
            if phaseObj.PreviousPhaseName != None:
                phaseObj.Previous = GV.PlxPhases[phaseObj.PreviousPhaseName]
                phaseObj.Previous.Children.append(phaseObj)
        GV.PlxPhasesList = PreOrderDeepList(GV.PlxPhases['InitialPhase'])

    if All or Materials:
        logger.info("Enumerate Materials...")
        for mat in PlxInput.Materials:
            matType = mat.TypeName.value
            logger.info(f"    {mat.MaterialName.value}")
            if matType == "SoilMat":
                GV.SoilMats[mat.MaterialNumber.value] = PlxSoilMaterial(mat)
            elif matType == "PlateMat2D":
                GV.PlateMats[mat.MaterialNumber.value] = PlxPlateMaterial(mat)
            elif matType == "AnchorMat2D":
                tmp = PlxAnchorMaterial(mat)
                GV.AnchorMatsByID[mat.MaterialNumber.value] = tmp
                GV.AnchorMatsByName[tmp.Name] = tmp
            elif matType == "EmbeddedBeam2DMat":
                GV.EmbeddedBeamMats[mat.MaterialNumber.value] = PlxEmbeddedBeamMaterial(mat)

    if All or Anchors:
        logger.info("Enumerate FixedEndAnchors...")
        for i, item in enumerate(PlxInput.FixedEndAnchors):
            anchor = PlxAnchor(item)
            logger.info(f"    {anchor.Name}")
            tmpMaterialName = item.Material[GV.PlxPhases["InitialPhase"].PlxObject].Name.value
            anchor.Material = GV.AnchorMatsByName[tmpMaterialName]
            anchor.MaterialName = anchor.Material.MaterialName
            anchor.Spacing = anchor.Material.Spacing
            anchor.Length = item.EquivalentLength[GV.PlxPhases["InitialPhase"].PlxObject].value
            anchor.UpdatePrestress()
            GV.PlxFixedAnchors[i+1] = anchor

        logger.info("Enumerate NodeToNodeAnchors...")
        for i, item in enumerate(PlxInput.NodeToNodeAnchors):
            anchor =  PlxAnchor(item)
            logger.info(f"    {anchor.Name}")
            tmpMaterialName = item.Material[GV.PlxPhases["InitialPhase"].PlxObject].Name.value
            anchor.Material = GV.AnchorMatsByName[tmpMaterialName]
            anchor.MaterialName = anchor.Material.MaterialName
            anchor.Spacing = anchor.Material.Spacing
            anchor.UpdatePrestress()
            GV.PlxNtNAnchors[i+1] = anchor

            #GV.PlxNtNAnchors[i+1].X1 = item.Parent.First.x.value
            #GV.PlxNtNAnchors[i+1].Y1 = item.Parent.First.y.value
            ##GV.PlxNtNAnchors[i+1].X2 = item.Parent.Second.x.value
            #GV.PlxNtNAnchors[i+1].Y2 = item.Parent.Second.y.value
        
        logger.info("Go to Structures to obtain coordinates...")
        PlxInput.gotostructures()
        for item in GV.PlxFixedAnchors.values():
            parentName = item.Name[:item.Name.rfind("_")]
            for anchor in PlxInput.FixedEndAnchors:
                if anchor.Name.value == parentName:
                    item.X1 = anchor.Parent.x.value
                    item.Y1 = anchor.Parent.y.value
        for item in GV.PlxNtNAnchors.values():
            parentName = item.Name[:item.Name.rfind("_")]
            for anchor in PlxInput.NodeToNodeAnchors:
                if anchor.Name.value == parentName:
                    item.X1 = anchor.Parent.First.x.value
                    item.Y1 = anchor.Parent.First.y.value
                    item.X2 = anchor.Parent.Second.x.value
                    item.Y2 = anchor.Parent.Second.y.value
        
        logger.info("Switch back to Staged Construction...")
        PlxInput.SwitchToStagedConstruction()
        
    if All or Plates:
        logger.info("Enumerate Plates...")
        for i, item in enumerate(PlxInput.Plates):
            GV.PlxPlates[i+1] = PlxPlate(item)
            logger.info(f"    {GV.PlxPlates[i+1].Name}")
            GV.PlxPlates[i+1].MaterialName = item.Material[GV.PlxPhases["InitialPhase"].PlxObject].Name.value

    logger.info("Initialization Finished.")