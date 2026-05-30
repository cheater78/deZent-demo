from enum import StrEnum

class GatewayProfileType(StrEnum):
    STANDARD = "standard"
    MIETER = "mieter" # TODO: landlord or tennant? - what selection?
    INDUSTRY = "industry"
