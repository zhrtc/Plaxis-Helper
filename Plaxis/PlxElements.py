from enum import Enum
import math
from typing import Any, List, Dict

class MaterialTypeName(Enum):
    Soil = 1
    Anchor = 2
    Plate = 3
    EmbeddedBeam = 4

class PlxElement:
    Name:str = None
    PlxObject = None

    def __init__(self, object) -> None:
        self.Name = object.Name.value
        self.PlxObject = object

class PlxMaterial(PlxElement):
    MaterialName:str = None
    TypeName:MaterialTypeName = None

    def __init__(self, object) -> None:
        super().__init__(object)
        self.MaterialName = object.MaterialName.value

class PlxSoilMaterial(PlxMaterial):
    def __init__(self, object) -> None:
        super().__init__(object)
        self.TypeName = MaterialTypeName.Soil

class PlxAnchorMaterial(PlxMaterial):
    Spacing:float = None
    EA:float = None

    def __init__(self, object) -> None:
        super().__init__(object)
        self.Spacing = object.Lspacing.value
        self.EA = object.EAPerLength.value
        self.TypeName = MaterialTypeName.Anchor

class PlxPlateMaterial(PlxMaterial):
    EA:float = None
    EA2:float = None
    EI:float = None
    Thickness:float = None
    UnitWeight:float = None

    def __init__(self, object) -> None:
        super().__init__(object)
        self.EA = object.EA.value
        self.EA2 = object.EA2.value
        self.EI = object.EI.value
        self.Thickness = object.d.value
        self.UnitWeight = object.w.value
        self.TypeName = MaterialTypeName.Plate

class PlxEmbeddedBeamMaterial(PlxMaterial):

    def __init__(self, object) -> None:
        super().__init__(object)
        self.TypeName = MaterialTypeName.EmbeddedBeam

class PlxPhase(PlxElement):
    PhaseID:str = None
    Previous = None
    PreviousPhaseName:str = None
    Children = None

    def __init__(self, object) -> None:
        super().__init__(object)
        self.PhaseID = object.Identification.value
        self.Children = []
        if self.Name != 'InitialPhase':
            self.PreviousPhaseName = object.PreviousPhase.Name.value

    def __str__(self) -> str:
        return f"{self.Name} [{self.PhaseID}]"

class PlxAnchor(PlxElement):
    X1:float = None
    Y1:float = None
    X2:float = None
    Y2:float = None
    PrestressForce:float = None
    PrestressPhaseName:str = None
    Forces:Dict[str, float] = None
    MaxTension:float = None
    MaxTensionPhaseName:str = None
    MaxCompression:float = None
    MaxCompressionPhaseName:str = None
    Material:PlxAnchorMaterial = None
    MaterialName:str = None
    Spacing:float = None
    Length:float = None
    Mark:int = 0

    def __init__(self, object) -> None:
        super().__init__(object)
        self.Forces:Dict[str, float] = {}
        self.UpdatePrestress()

    def UpdatePrestress(self) -> None:
        for phase in GV.PlxPhasesList:
            isPrestressActivated = self.PlxObject.AdjustPrestress[phase.PlxObject].value
            if isPrestressActivated == True:
                self.PrestressForce = self.PlxObject.PrestressForce[phase.PlxObject].value
                self.PrestressPhaseName = phase.Name
                break


    def UpdateMaxForce(self, phaseName:str, *args) -> None:
        for item in args:
            if isinstance(item, float) or isinstance(item, int):
                if item <= 0 and (self.MaxCompression is None or item < self.MaxCompression):
                    self.MaxCompression = item
                    self.MaxCompressionPhaseName = phaseName
                if item >= 0 and (self.MaxTension is None or item > self.MaxTension):
                    self.MaxTension = item
                    self.MaxTensionPhaseName = phaseName

    def UpdateCoordinates(self, X:float, Y:float, localID:int = 1) -> None:
        if localID == 1:
            self.X1 = X
            self.Y1 = Y
        elif localID == 2:
            self.X2 = X
            self.Y2 = Y
        if self.Length is None and self.X1 != None and self.X2 != None and self.Y1 != None and self.Y2 != None:
            self.Length = math.sqrt((self.X1 - self.X2)*(self.X1 - self.X2) + (self.Y2 - self.Y2)*(self.Y2 - self.Y2))

    def UpdateAxialForces(self, phaseName:str, force:float) -> None:
        self.Forces[phaseName] = force

    def __str__(self) -> str:
        if self.Y2 is None or abs(self.Y1 - self.Y2) < 1e-4:
            level = f"{self.Y1:+7.2f}"
        else:
            level = f"{self.Y1:+7.2f}~{self.Y2:+7.2f}"
        preloadStr = f", Preloaded at Phase: {GV.PlxPhases[self.PrestressPhaseName].PhaseID} [{self.PrestressPhaseName}])" if self.PrestressForce != None else ""
        return (f"{self.Name:24}\t{level}\t{self.Length:6.2f}\t{self.Spacing:5.2f}\t{abs(self.MaxCompression):8.1f}\t"
                f"{abs(self.PrestressForce) if self.PrestressForce != None else 0:8.1f}\t{self.MaterialName}\t"
                f"Max Force accured at Phase: {GV.PlxPhases[self.MaxCompressionPhaseName].PhaseID} [{self.MaxCompressionPhaseName}]"
                f"{preloadStr}\r\n")

    def ToList(self) -> List[Any]:
        return [self.Name,
                self.Y1 if self.Y2 is None or abs(self.Y1 - self.Y2) < 1e-4 else f"{self.Y1:+7.2f}~{self.Y2:+7.2f}",
                round(self.Length, 3),
                round(self.Spacing, 3),
                round(abs(self.MaxCompression), 3),
                round(abs(self.PrestressForce), 3) if self.PrestressForce != None else 0,
                self.MaterialName,
                f"{GV.PlxPhases[self.MaxCompressionPhaseName].PhaseID} [{self.MaxCompressionPhaseName}]",
                f"{GV.PlxPhases[self.PrestressPhaseName].PhaseID} [{self.PrestressPhaseName}]" if self.PrestressForce != None else ""]

    @staticmethod
    def LevelCompare(x):
        if x.Y1 != None and x.Y2 != None:
            return -(x.Y1 + x.Y2)/2 + (x.X1 + x.X2)/2*10000
        elif x.Y1 != None:
            return -x.Y1 + x.X1*10000
        else:
            return float("inf")

class PlxPlate(PlxElement):
    X1:float = None
    Y1:float = None
    X2:float = None
    Y2:float = None
    MaxAxialForce:float = None
    MaxAxialForcePhaseName:str = None
    MaxShearForce:float = None
    MaxShearForcePhaseName:str = None
    MaxBendingMoment:float = None
    MaxBendingMomentPhaseName:str = None
    MaterialName:str = None

    def __init__(self, object) -> None:
        super().__init__(object)      

class GV():
    """Gloabal Variables"""

    SeverInput = None
    SeverOutput = None
    PlxInput = None
    PlxOutput = None

    PlxPhases:Dict[str, PlxPhase] = {}
    PlxPhasesList:List[PlxPhase] = []

    PlxPlates:Dict[str, str] = {}
    PlxInterfaces:Dict[str, str] = {}
    PlxFixedAnchors:Dict[str, PlxAnchor] = {}
    PlxNtNAnchors:Dict[str, PlxAnchor] = {}

    SoilMats:Dict[int, PlxSoilMaterial] = {}
    PlateMats:Dict[int, PlxPlateMaterial] = {}
    AnchorMatsByID:Dict[int, PlxAnchorMaterial] = {}
    AnchorMatsByName:Dict[str, PlxAnchorMaterial] = {}
    EmbeddedBeamMats:Dict[int, PlxEmbeddedBeamMaterial] = {}

    @classmethod
    def Reset(cls):
        cls.SeverInput = None
        cls.SeverOutput = None
        cls.PlxInput = None
        cls.PlxOutput = None

        cls.PlxPhases.clear()
        cls.PlxPhasesList.clear()

        cls.PlxPlates.clear()
        cls.PlxInterfaces.clear()
        cls.PlxFixedAnchors.clear()
        cls.PlxNtNAnchors.clear()

        cls.SoilMats.clear()
        cls.PlateMats.clear()
        cls.AnchorMatsByID.clear()
        cls.AnchorMatsByName.clear()
        cls.EmbeddedBeamMats.clear()