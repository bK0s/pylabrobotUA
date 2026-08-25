"""High-level Carousel machine that wraps any :class:`CarouselBackend`."""

from __future__ import annotations

from typing import Optional

from .carousel_backend import CarouselBackend


class Carousel:
  """A rotating plate hotel / carousel instrument.

  The Carousel manages a rotating plate that holds up to 9 stacks, each
  stack containing up to 21 (or 22) microplate slots.  A vertical lift /
  handler moves individual plates to a transfer position where a liquid
  handler's RoMa arm can pick them up.

  Example usage::

    from pylabrobot.carousel import Carousel
    from pylabrobot.carousel.liconic_lpt220 import LiCoNiCLPT220Backend

    carousel = Carousel(
        name="my_carousel",
        backend=LiCoNiCLPT220Backend(port="COM8"),
    )
    await carousel.setup()

    # Bring stack 3, slot 5 to the transfer position
    await carousel.fetch_plate(stack=3, level=5)

    # After the liquid handler has finished with the plate, return it
    await carousel.return_plate(stack=3, level=5)

    await carousel.stop()
  """

  def __init__(
    self,
    name: str,
    backend: CarouselBackend,
    num_stacks: int = 9,
    levels_per_stack: int = 21,
  ) -> None:
    """Create a Carousel instance.

    Args:
      name: Arbitrary human-readable label for this instrument.
      backend: Hardware-specific communication backend.
      num_stacks: Number of stacks on the rotating plate (default 9).
      levels_per_stack: Usable plate slots per stack (default 21 –
        position 22 is unusable with the barcode reader installed).
    """
    self.name = name
    self._backend = backend
    self.num_stacks = num_stacks
    self.levels_per_stack = levels_per_stack
    self._current_position: Optional[int] = None

  # ------------------------------------------------------------------
  # Properties
  # ------------------------------------------------------------------

  @property
  def backend(self) -> CarouselBackend:
    return self._backend

  # ------------------------------------------------------------------
  # Lifecycle
  # ------------------------------------------------------------------

  async def setup(self) -> None:
    """Initialise the backend (open serial port, send init commands …)."""
    await self._backend.setup()
    self._current_position = await self._backend.get_current_position()

  async def stop(self) -> None:
    """Cleanly shut down the backend."""
    await self._backend.stop()

  # ------------------------------------------------------------------
  # Rotation helpers
  # ------------------------------------------------------------------

  def _validate_stack(self, stack: int) -> None:
    if not (1 <= stack <= self.num_stacks):
      raise ValueError(
        f"Stack must be between 1 and {self.num_stacks}, got {stack}."
      )

  def _validate_level(self, level: int) -> None:
    if not (1 <= level <= self.levels_per_stack):
      raise ValueError(
        f"Level must be between 1 and {self.levels_per_stack}, got {level}."
      )

  async def rotate_to(self, stack: int) -> None:
    """Rotate the carousel so that *stack* faces the handler.

    Args:
      stack: Target stack position (1–9).
    """
    self._validate_stack(stack)
    await self._backend.rotate_to_position(stack)
    self._current_position = stack

  async def get_position(self) -> int:
    """Query the carousel for its current rotational position."""
    pos = await self._backend.get_current_position()
    self._current_position = pos
    return pos

  # ------------------------------------------------------------------
  # Plate transfer
  # ------------------------------------------------------------------

  async def fetch_plate(self, stack: int, level: int) -> None:
    """Rotate to *stack* and move the plate at *level* to the transfer position.

    After this call the plate sits at the transfer / RoMa pick-up position
    and the liquid handler can act on it.

    Args:
      stack: Carousel stack number (1–9).
      level: Plate slot within the stack (1–21).
    """
    self._validate_stack(stack)
    self._validate_level(level)
    await self.rotate_to(stack)
    await self._backend.move_plate_to_transfer(stack, level)

  async def return_plate(self, stack: int, level: int) -> None:
    """Move the plate at the transfer position back into *stack* / *level*.

    The carousel must already be at the correct *stack* position (i.e. you
    must have called :meth:`fetch_plate` or :meth:`rotate_to` previously).

    Args:
      stack: Carousel stack number (1–9).
      level: Plate slot within the stack (1–21).
    """
    self._validate_stack(stack)
    self._validate_level(level)
    await self._backend.move_plate_from_transfer(stack, level)

  # ------------------------------------------------------------------
  # Optional barcode inventory
  # ------------------------------------------------------------------

  async def run_barcode_inventory(self) -> None:
    """Trigger a full barcode inventory scan (requires the barcode reader option)."""
    await self._backend.start_barcode_inventory()

  # ------------------------------------------------------------------
  # Repr
  # ------------------------------------------------------------------

  def __repr__(self) -> str:
    return (
      f"Carousel(name={self.name!r}, "
      f"stacks={self.num_stacks}, "
      f"levels={self.levels_per_stack}, "
      f"backend={self._backend.__class__.__name__})"
    )
