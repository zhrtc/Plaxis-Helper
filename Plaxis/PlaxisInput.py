from operator import truediv
from .PlxElements import *
from typing import List, Any
from plxscripting.plx_scripting_exceptions import PlxScriptingError
import re


def SetSoilProperties(namePattern: str | List, propertyName: str | List, value: int | float | str | List) -> None:
    if isinstance(namePattern, list):
        if (not isinstance(value, list)) or len(value) != len(namePattern):
            print("Arguments Error!")
            return
    GV.PlxInput.gotostructures()

    def _SetProperties(soilMat, propName, value):
        print(
            f"Soil Material {soilMat.MaterialName} Matched. Setting {propName} to {value}")
        soilMat.SetProperty(propName, value)

    for soilMat in GV.SoilMats.values():
        isMatFound = False
        if isinstance(namePattern, list):
            for index, item in enumerate(namePattern):
                if re.search(item, soilMat.MaterialName) != None:
                    isMatFound = True
                    if isinstance(propertyName, list):
                        for propName in propertyName:
                            _SetProperties(soilMat, propName, value[index])
                    else:
                        _SetProperties(soilMat, propertyName, value[index])
        else:
            if re.search(namePattern, soilMat.MaterialName) != None:
                isMatFound = True
                if isinstance(propertyName, list):
                    for propName in propertyName:
                        _SetProperties(soilMat, propName, value)
                else:
                    _SetProperties(soilMat, propertyName, value)
        if isMatFound == False:
            print(
                f"Soil Material {soilMat.MaterialName} Dose NOT Match ANY Patterns.")
