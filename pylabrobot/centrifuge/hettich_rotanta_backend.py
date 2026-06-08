import logging

from .backend import CentrifugeBackend

logger = logging.getLogger(__name__)


class HettichRotantaBackend(CentrifugeBackend):
    """
    Backend skeleton for the Hettich ROTANTA 460 Robotic centrifuge.

    This backend adapts PyLabRobot's existing CentrifugeBackend interface
    to the Hettich ROTANTA 460 Robotic used in the biobank.

    This first version does not communicate with real hardware yet.
    It documents the method structure and preliminary Hettich serial command mappings.
    """

    def __init__(self, address: str = "]"):
        """
        Args:
            address: Hettich centrifuge address. The factory default address is usually ']',
            corresponding to address 29 in the Hettich communication manual.
        """
        self.address = address

    async def setup(self):
        """
        Future implementation:
        - Open serial connection.
        - Configure serial settings: 9600 baud, 7 data bits, even parity, 1 stop bit.
        - Check that the centrifuge is reachable.
        - Check that it is in LOCK 2 software-control mode.
        """
        logger.info("Setting up Hettich ROTANTA backend.")
        raise NotImplementedError("Real serial setup is not implemented yet.")

    async def stop(self):
        """
        Future implementation:
        - Stop/close the serial connection safely.
        """
        logger.info("Stopping Hettich ROTANTA backend.")
        raise NotImplementedError("Real serial shutdown is not implemented yet.")

    async def open_door(self) -> None:
        """
        Open the loading hatch.

        Hettich command mapping:
        - Send parameter 00526 = 0060.
        - Poll parameter 00528 until hatch-open status is true.
        """
        logger.info("Open Hettich ROTANTA hatch.")
        raise NotImplementedError("Open hatch command is not implemented yet.")

    async def close_door(self) -> None:
        """
        Close the loading hatch.

        Hettich command mapping:
        - Send parameter 00526 = 0070.
        - Poll parameter 00528 until hatch-closed status is true.
        """
        logger.info("Close Hettich ROTANTA hatch.")
        raise NotImplementedError("Close hatch command is not implemented yet.")

    async def lock_door(self) -> None:
        """
        Lock the door/hatch.

        Need to confirm:
        - Whether Hettich exposes this as a separate command.
        - Or whether closing the hatch automatically locks it.
        """
        logger.info("Lock Hettich ROTANTA door/hatch.")
        raise NotImplementedError("Door lock behavior needs to be confirmed.")

    async def unlock_door(self) -> None:
        """
        Unlock the door/hatch.

        Need to confirm:
        - Whether Hettich exposes this as a separate command.
        - Or whether opening the hatch automatically unlocks it.
        """
        logger.info("Unlock Hettich ROTANTA door/hatch.")
        raise NotImplementedError("Door unlock behavior needs to be confirmed.")

    async def go_to_bucket1(self) -> None:
        """
        Move rotor to bucket position 1.

        Hettich command mapping:
        - Set target position using parameter 00524.
        - Send positioning command using parameter 00526.
        - Poll parameter 00528 until position reached.
        """
        logger.info("Move Hettich ROTANTA rotor to bucket 1.")
        raise NotImplementedError("Bucket 1 positioning is not implemented yet.")

    async def go_to_bucket2(self) -> None:
        """
        Move rotor to bucket position 2.

        Hettich command mapping:
        - Set target position using parameter 00524.
        - Send positioning command using parameter 00526.
        - Poll parameter 00528 until position reached.
        """
        logger.info("Move Hettich ROTANTA rotor to bucket 2.")
        raise NotImplementedError("Bucket 2 positioning is not implemented yet.")

    async def rotate_distance(self, distance) -> None:
        """
        Rotate rotor by a specified distance.

        Need to confirm:
        - PyLabRobot docs define rotate_distance where 8000 = 360 degrees.
        - Hettich docs seem to focus more on target rotor positions.
        - This may need a conversion layer or may not map directly.
        """
        logger.info("Rotate Hettich ROTANTA rotor by distance: %s", distance)
        raise NotImplementedError("rotate_distance mapping needs to be confirmed.")

    async def lock_bucket(self) -> None:
        """
        Lock bucket position.

        Need to confirm:
        - Whether Hettich has a separate bucket lock command.
        - Or whether bucket holding is handled by positioning mode / electromagnetic brake.
        """
        logger.info("Lock Hettich ROTANTA bucket position.")
        raise NotImplementedError("Bucket lock behavior needs to be confirmed.")

    async def unlock_bucket(self) -> None:
        """
        Unlock bucket position.

        Possible Hettich command mapping:
        - Parameter 00526 = 0080 may terminate positioning mode.
        - Need to confirm if this should map to unlock_bucket.
        """
        logger.info("Unlock Hettich ROTANTA bucket position.")
        raise NotImplementedError("Bucket unlock behavior needs to be confirmed.")

    async def start_spin_cycle(self, g: float, duration: float, acceleration: float) -> None:
        """
        Start a centrifugation cycle.

        Hettich command mapping:
        - Set RCF/RPM/runtime/acceleration as needed.
        - Start centrifugation using parameter 00521 = 0002.
        - Poll status while running.
        - Stop using parameter 00521 = 0001 if needed.

        Args:
            g: Target relative centrifugal force.
            duration: Spin duration.
            acceleration: Acceleration setting.
        """
        logger.info(
            "Start Hettich ROTANTA spin cycle: g=%s, duration=%s, acceleration=%s",
            g,
            duration,
            acceleration,
        )
        raise NotImplementedError("Spin cycle command is not implemented yet.")