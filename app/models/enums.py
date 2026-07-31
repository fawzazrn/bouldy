# app/models/enums.py
from enum import Enum

class RouteStyle(str, Enum):
    CRIMPS = "Crimps"
    SLOPERS = "Slopers"
    PINCHES = "Pinches"
    JUGS = "Jugs"
    POCKETS = "Pockets"

    DYNO = "Dyno"
    DEADPOINT = "Deadpoint"
    STATIC = "Static"
    COORDINATION = "Coordination"

    SLAB = "Slab"
    VERTICAL = "Vertical"
    OVERHANG = "Overhang"
    ROOF = "Roof"

    COMPRESSION = "Compression"
    BALANCE = "Balance"
    MANTLE = "Mantle"
    HEEL_HOOK = "Heel Hook"
    TOE_HOOK = "Toe Hook"
    GASTON = "Gaston"
    
class AttemptResult(str, Enum):
    FLASH = "flash"
    ZONE = "zone"
    SEND = "send"
    PROJECT = "project"
    
class RouteStatus(str, Enum):
    ACTIVE = "active"
    RETIRED = "retired"