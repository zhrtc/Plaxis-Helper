from plxscripting.easy import *
from .ServerConfig import ServerConfig
from .CommonFuncs import *
from .PlxElements import *
from .PlaxisOutput import *
import logging

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)

def Initialize(serverConfig:ServerConfig = ServerConfig(), initAnchors:bool = True, initPlates:bool = False):
    GV.Reset()
    logger = logging.getLogger("InitPlaxis")
    logger.setLevel(logging.INFO)
    logger.info("Initialize Plaxis Module")

    try:
        logger.info("Connect to Plaxis Input")
        GV.SeverInput, GV.PlxInput = new_server(serverConfig.Host, serverConfig.InputPort, password=serverConfig.InputPassword, request_timeout=serverConfig.RequestTimeout)
        logger.info("Connect to Plaxis Input Succeed!")
    except:
        logger.warning("Connect to Plaxis Input Failed!")
        GV.SeverInput, GV.PlxInput = None, None

    try:
        logger.info("Connect to Plaxis Output")
        GV.SeverOutput, GV.PlxOutput = new_server(serverConfig.Host, serverConfig.OutputPort, password=serverConfig.OutputPassword, request_timeout=serverConfig.RequestTimeout)
        logger.info("Connect to Plaxis Output Succeed!")
    except:
        logger.warning("Connect to Plaxis Output Failed!")
        GV.SeverOutput, GV.PlxOutput = None, None

    PlxInput = GV.PlxInput
    PlxInput.gotostages()
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

    if initAnchors:
        logger.info("Enumerate FixedEndAnchors...")
        for i, item in enumerate(PlxInput.FixedEndAnchors):
            GV.PlxFixedAnchors[i+1] = PlxAnchor(item)
            logger.info(f"    {GV.PlxFixedAnchors[i+1].Name}")
            tmpMaterialName = item.Material[GV.PlxPhases["InitialPhase"].PlxObject].Name.value
            GV.PlxFixedAnchors[i+1].Material = GV.AnchorMatsByName[tmpMaterialName]
            GV.PlxFixedAnchors[i+1].MaterialName = GV.PlxFixedAnchors[i+1].Material.MaterialName
            GV.PlxFixedAnchors[i+1].Spacing = GV.PlxFixedAnchors[i+1].Material.Spacing
            GV.PlxFixedAnchors[i+1].Length = item.EquivalentLength[GV.PlxPhases["InitialPhase"].PlxObject].value

        logger.info("Enumerate NodeToNodeAnchors...")
        for i, item in enumerate(PlxInput.NodeToNodeAnchors):
            GV.PlxNtNAnchors[i+1] = PlxAnchor(item)
            logger.info(f"    {GV.PlxNtNAnchors[i+1].Name}")
            tmpMaterialName = item.Material[GV.PlxPhases["InitialPhase"].PlxObject].Name.value
            GV.PlxNtNAnchors[i+1].Material = GV.AnchorMatsByName[tmpMaterialName]
            GV.PlxNtNAnchors[i+1].MaterialName = GV.PlxNtNAnchors[i+1].Material.MaterialName
            GV.PlxNtNAnchors[i+1].Spacing = GV.PlxNtNAnchors[i+1].Material.Spacing

    if initPlates:
        logger.info("Enumerate Plates...")
        for i, item in enumerate(PlxInput.Plates):
            GV.PlxPlates[i+1] = PlxPlate(item)
            logger.info(f"    {GV.PlxPlates[i+1].Name}")
            GV.PlxPlates[i+1].MaterialName = item.Material[GV.PlxPhases["InitialPhase"].PlxObject].Name.value

    logger.info("Initialization Finished.")