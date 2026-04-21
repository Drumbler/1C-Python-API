from dataclasses import dataclass


@dataclass(slots=True)
class BaseParams:
    width: float
    depth: float
    height: float   
