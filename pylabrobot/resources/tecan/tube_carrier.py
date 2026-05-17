from typing import Dict
from pylabrobot.resources.tube import Tube
from pylabrobot.resources.tecan.tecan_resource import TecanResource
from pylabrobot.resources.carrier import (
    Coordinate,
    ResourceHolder,
    TubeCarrier,
    create_homogeneous_resources
)
class TecanTubeCarrier(TubeCarrier, TecanResource):
    def __init__(self, name: str, size_x: float, size_y: float, size_z: float, sites: Dict[int, ResourceHolder] | None = None, category="tube_carrier", model: str | None = None):
        super().__init__(name, size_x, size_y, size_z, sites, category, model)

def tecan_tube_carrier_16(name: str) -> TubeCarrier:
    """
    Custom tube rack
    1 track wide
    Holds 16 tubes
    """
    return TecanTubeCarrier(
        name=name,
        size_x=23.0,
        size_y=307.0,
        size_z=50,
        sites=create_homogeneous_resources(
            klass=ResourceHolder,
            locations=[
                Coordinate(3.0,15 + x * 18.8, 10.0+1.2) for x in range(16)
            ],
            resource_size_x=16.5,
            resource_size_y=16.5,
            name_prefix=name
        ),
        model="custom"
    )

def test_tube(name:str) -> Tube:
    diameter = 16.5
    return Tube(
    name=name,
    size_x=diameter,
    size_y=diameter,
    size_z=115,
    model="Unknown 10mL",
    max_volume=10_000,
    material_z_thickness=1.2,
  )