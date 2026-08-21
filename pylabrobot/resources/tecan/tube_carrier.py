from typing import Dict, Optional

from pylabrobot.resources.carrier import (
  Coordinate,
  ResourceHolder,
  TubeCarrier,
  create_homogeneous_resources,
)
from pylabrobot.resources.tecan.tecan_resource import TecanResource
from pylabrobot.resources.tube import Tube


class TecanTubeCarrier(TubeCarrier, TecanResource):
  """Base class for Tecan tube carriers."""

  def __init__(
    self,
    name: str,
    size_x: float,
    size_y: float,
    size_z: float,
    off_x: float = 0,
    off_y: float = 0,
    sites: Optional[Dict[int, ResourceHolder]] = None,
    category="tecan_tube_carrier",
    model: Optional[str] = None,
  ):
    super().__init__(
      name,
      size_x,
      size_y,
      size_z,
      sites,
      category=category,
      model=model,
    )
    self.off_x = off_x
    self.off_y = off_y


def tecan_tube_carrier_16(name: str) -> TecanTubeCarrier:
  """Single-track, 16-position tube carrier.

  No corresponding Tecan part number is known for this carrier; the
  dimensions and spacing are placeholder estimates sized to fit one rail
  slot on an EVO deck, not measurements of real hardware.
  """
  return TecanTubeCarrier(
    name=name,
    size_x=23.0,
    size_y=307.0,
    size_z=50.0,
    sites=create_homogeneous_resources(
      klass=ResourceHolder,
      locations=[Coordinate(3.25, 1.375 + i * 18.75, 50.0) for i in range(16)],
      resource_size_x=16.5,
      resource_size_y=16.5,
      name_prefix=name,
    ),
    model="tecan_tube_carrier_16 (placeholder)",
  )


def test_tube(name: str) -> Tube:
  """Placeholder 10 mL test tube.

  Dimensions are estimates, not sourced from a specific manufacturer part.
  """
  diameter = 16.5
  return Tube(
    name=name,
    size_x=diameter,
    size_y=diameter,
    size_z=115.0,
    model="test_tube (placeholder)",
    max_volume=10_000,
    material_z_thickness=1.2,
  )
