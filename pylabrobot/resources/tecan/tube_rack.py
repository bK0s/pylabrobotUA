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

# class TubeSpot(Resource):
#     # def __init__(self, name: str, size_x=9, size_y=9, size_z=45):
#     #     self.name = name
#     #     self.size_x = size_x
#     #     self.size_y = size_y
#     #     self.size_z = size_z
#         def __init__(self, name: str, size_x: float, size_y: float, size_z: float, rotation: Rotation | None = None, category: str | None = None, model: str | None = None, barcode: Barcode | None = None):
#             super().__init__(name, size_x, size_y, size_z, rotation, category, model, barcode)

#             self.parent: Optional["TecanTubeRack"] = None

def tecan_tube_rack(name: str) -> TubeRack:
    return TecanTubeRack(
        size_x=40,
        size_y=200,
        size_z=3,
        name='tubeRack',
        ordered_items=create_ordered_items_2d(
            test_tube, 1,16,10,10,2,3,10
        ),
        model='Whoknows'
    )
def test_tube(name:str) -> Tube:
    diameter = 10
    return Tube(
    name=name,
    size_x=diameter,
    size_y=diameter,
    size_z=115,
    model="Falcon 50mL",
    max_volume=50_000,
    material_z_thickness=1.2,
  )