from typing import Dict, cast, Optional
from functools import partial

from pylabrobot.resources import Well
from pylabrobot.resources.tube import Tube
from pylabrobot.resources.tecan.tecan_resource import TecanResource
from pylabrobot.resources.tube_rack import TubeRack
from pylabrobot.resources.utils import create_ordered_items_2d, create_equally_spaced_2d
from pylabrobot.resources import Resource

class TecanTubeRack(TubeRack, TecanResource):
    def __init__(self, name: str, size_x: float, size_y: float, size_z: float, ordered_items: Dict[str, Tube] | None = None, model: str | None = None):
        super().__init__(name, size_x, size_y, size_z, ordered_items, model)

def tecan_tube_rack(name: str) -> TubeRack:
    return TecanTubeRack(
        size_x=23,
        size_y=307,
        size_z=50,
        name=name,
        ordered_items=create_ordered_items_2d(
            klass=test_tube,
            num_items_x=1,
            num_items_y=16,
            dx=4,
            dy=1.375,
            dz=50,
            item_dx=0,
            item_dy=18.75
        ),
        model='Whoknows'
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