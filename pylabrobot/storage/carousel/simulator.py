"""Simulator backend for the LiCONiC LPT 220.

Useful for developing and testing protocols without a physical carousel.
Mirrors the interface of :class:`~liconic_lpt220.LiCoNiCLPT220Backend` but
operates entirely in memory.

Usage::

  from liconic_lpt220 import Carousel
  from liconic_lpt220.simulator import LiCoNiCLPT220SimulatorBackend

  carousel = Carousel(
      name="sim_carousel",
      backend=LiCoNiCLPT220SimulatorBackend(),
  )
  await carousel.setup()
  await carousel.fetch_plate(stack=2, level=4)
  await carousel.return_plate(stack=2, level=4)
  await carousel.stop()
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from .carousel_backend import CarouselBackend

logger = logging.getLogger(__name__)


class LiCoNiCLPT220SimulatorBackend(CarouselBackend):
  """In-memory simulator for the LPT 220 carousel.

  All operations log what they would do and simulate the expected timing
  with small configurable delays.

  Args:
    num_stacks: Number of stacks to simulate (default 9).
    levels_per_stack: Plate slots per stack (default 21).
    op_delay: Simulated operation delay in seconds (default 0.05).
    has_barcode_reader: Whether to simulate the barcode reader option.
  """

  def __init__(
    self,
    num_stacks: int = 9,
    levels_per_stack: int = 21,
    op_delay: float = 0.05,
    has_barcode_reader: bool = False,
  ) -> None:
    self._num_stacks = num_stacks
    self._levels_per_stack = levels_per_stack
    self._op_delay = op_delay
    self._has_barcode_reader = has_barcode_reader

    self._position: int = 1
    self._initialised: bool = False

    # Simulate plate occupancy: True = plate present
    self._plates: dict[tuple[int, int], bool] = {
      (s, l): True
      for s in range(1, num_stacks + 1)
      for l in range(1, levels_per_stack + 1)
    }
    # Track which plate is currently at the transfer position
    self._plate_at_transfer: Optional[tuple[int, int]] = None

  # ------------------------------------------------------------------
  # Lifecycle
  # ------------------------------------------------------------------

  async def setup(self) -> None:
    await asyncio.sleep(self._op_delay)
    self._initialised = True
    logger.info("[SIM] LPT 220 initialised. Position: %d", self._position)

  async def stop(self) -> None:
    await asyncio.sleep(self._op_delay)
    self._initialised = False
    logger.info("[SIM] LPT 220 stopped.")

  # ------------------------------------------------------------------
  # Rotation
  # ------------------------------------------------------------------

  async def rotate_to_position(self, position: int) -> None:
    await asyncio.sleep(self._op_delay)
    self._position = position
    logger.info("[SIM] Carousel rotated to position %d.", position)

  async def get_current_position(self) -> int:
    return self._position

  # ------------------------------------------------------------------
  # Plate transfer
  # ------------------------------------------------------------------

  async def move_plate_to_transfer(self, stack: int, level: int) -> None:
    await asyncio.sleep(self._op_delay)
    key = (stack, level)
    if not self._plates.get(key, False):
      logger.warning("[SIM] No plate at stack %d level %d.", stack, level)
    self._plates[key] = False
    self._plate_at_transfer = key
    logger.info("[SIM] Plate from stack %d level %d moved to transfer position.", stack, level)

  async def move_plate_from_transfer(self, stack: int, level: int) -> None:
    await asyncio.sleep(self._op_delay)
    key = (stack, level)
    self._plates[key] = True
    self._plate_at_transfer = None
    logger.info("[SIM] Plate returned to stack %d level %d.", stack, level)

  # ------------------------------------------------------------------
  # Optional barcode inventory
  # ------------------------------------------------------------------

  async def start_barcode_inventory(self) -> None:
    if not self._has_barcode_reader:
      raise RuntimeError("[SIM] Barcode reader not installed on this unit.")
    await asyncio.sleep(self._op_delay * 10)  # inventory takes a bit longer
    logger.info("[SIM] Barcode inventory complete.")

  # ------------------------------------------------------------------
  # Extra helpers for testing
  # ------------------------------------------------------------------

  def get_plate_map(self) -> dict[tuple[int, int], bool]:
    """Return the current simulated plate occupancy map."""
    return dict(self._plates)

  def __repr__(self) -> str:
    return (
      f"LiCoNiCLPT220SimulatorBackend("
      f"stacks={self._num_stacks}, "
      f"levels={self._levels_per_stack}, "
      f"position={self._position})"
    )
