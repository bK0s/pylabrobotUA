"""Abstract base class for plate carousel / hotel backends."""

from abc import ABCMeta, abstractmethod


class CarouselBackend(metaclass=ABCMeta):
  """Abstract backend for a rotating plate carousel / hotel instrument.

  Subclasses implement the hardware-specific communication layer while the
  :class:`Carousel` front-end provides the unified user-facing API.
  """

  # ------------------------------------------------------------------
  # Lifecycle
  # ------------------------------------------------------------------

  @abstractmethod
  async def setup(self) -> None:
    """Open the connection to the instrument and initialise it."""

  @abstractmethod
  async def stop(self) -> None:
    """Gracefully close the connection."""

  # ------------------------------------------------------------------
  # Carousel rotation
  # ------------------------------------------------------------------

  @abstractmethod
  async def rotate_to_position(self, position: int) -> None:
    """Rotate the carousel so that the given stack position faces the handler.

    Args:
      position: Stack position (1-9 for LPT 220).
    """

  @abstractmethod
  async def get_current_position(self) -> int:
    """Return the carousel's current rotational position (1-9)."""

  # ------------------------------------------------------------------
  # Lift / handler
  # ------------------------------------------------------------------

  @abstractmethod
  async def move_plate_to_transfer(self, stack: int, level: int) -> None:
    """Move a plate from *stack* / *level* to the transfer (RoMa pick-up) position.

    Args:
      stack: Carousel stack number (1-9).
      level: Slot within the stack (1-21 for standard microplates).
    """

  @abstractmethod
  async def move_plate_from_transfer(self, stack: int, level: int) -> None:
    """Move a plate from the transfer position back into *stack* / *level*.

    Args:
      stack: Carousel stack number (1-9).
      level: Slot within the stack (1-21).
    """

  # ------------------------------------------------------------------
  # Optional barcode inventory
  # ------------------------------------------------------------------

  async def start_barcode_inventory(self) -> None:
    """Trigger a full barcode inventory scan (optional – not all units have a reader)."""
    raise NotImplementedError(f"{self.__class__.__name__} does not support barcode inventory.")
