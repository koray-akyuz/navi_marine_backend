from pydantic import BaseModel

class CoordinateCheck(BaseModel):
    latitude: float
    longitude: float


class MapBounds(BaseModel):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float