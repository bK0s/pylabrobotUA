import asyncio
import logging

import serial

from .backend import CentrifugeBackend

logger = logging.getLogger(__name__)

# RS-232 control characters
EOT = 0x04
ENQ = 0x05
STX = 0x02
ETX = 0x03
ACK = 0x06
NAK = 0x15

# Parameters (Hettich communication manual §2.10)
P_CONTROL_CMD = "00521"  # W:  0001=stop, 0002=start centrifugation
P_TARGET_POS  = "00524"  # RW: highbyte=rotor position count, lowbyte=target position
P_POS_CMD     = "00526"  # W:  positioning and hatch commands
P_POS_STATE   = "00528"  # R:  positioning and hatch state
P_RUNTIME     = "00601"  # RW: run time in seconds (0=continuous, 1–59999)
P_SET_SPEED   = "00603"  # RW: set speed in RPM (50–20000)
P_STATE_1     = "00634"  # R:  centrifuge state 1
P_STATE_2     = "00635"  # R:  centrifuge state 2 / key-lock
P_SIOF        = "00685"  # R:  must be read after power-on to unlock SELECT telegrams

# Values for P_POS_CMD (00526)
CMD_MOVE_SLOW     = "0001"
CMD_MOVE_FAST     = "0002"
CMD_OPEN_HATCH    = "0060"
CMD_CLOSE_HATCH   = "0070"
CMD_TERMINATE_POS = "0080"

# Values for P_CONTROL_CMD (00521)
CMD_STOP  = "0001"
CMD_START = "0002"

# P_POS_STATE (00528) highbyte bit masks
HATCH_OPEN_BIT   = 0x20  # bit 5: hatch is fully open
HATCH_CLOSED_BIT = 0x10  # bit 4: hatch is fully closed

# P_POS_STATE (00528) lowbyte bit masks
POS_REACHED = 0x04  # bit 2: rotor reached target position
POS_ERROR   = 0x10  # bit 4: positioning error

# LOCK 2 key-lock state (P_STATE_2 / 00635 lowbyte bits 2:0)
LOCK_2_VALUE = 2

# 4-position rotor on ROTANTA 460 Robotic
ROTOR_POSITIONS = 4

# Timing
POLL_INTERVAL_S    = 0.5
HATCH_TIMEOUT_S    = 30.0
POSITION_TIMEOUT_S = 60.0
SERIAL_TIMEOUT_S   = 0.5  # manual guarantees response within 150 ms


class HettichRotantaBackend(CentrifugeBackend):
    """
    RS-232 driver for the Hettich ROTANTA 460 Robotic centrifuge, Generation 2 (type 5680).

    Serial settings: 9600 baud, 7 data bits, even parity, 1 stop bit.

    Telegram formats (verified against manual §2.4 examples):
      ENQUIRY  PC→centrifuge:  EOT ADDR CODE(5) ENQ                       no BCC
      ENQUIRY  centrifuge→PC:  ADDR STX CODE(5) = VALUE(4) ETX BCC
      SELECT   PC→centrifuge:  EOT ADDR STX CODE(5) = VALUE(4) ETX BCC
      SELECT   centrifuge→PC:  ADDR ACK  or  ADDR NAK

    BCC = XOR of: CODE(5 bytes) + '='(1) + VALUE(4 bytes) + ETX(1) = 11 bytes total.
    """

    def __init__(
        self,
        port: str,
        address: str = "]",
        rpm: int = 1000,
        runtime: int = 60,
        positioning_speed: str = "fast",
    ):
        """
        Args:
            port: Serial port, e.g. '/dev/ttyUSB0' or 'COM3'.
            address: Centrifuge address character. Factory default is ']' (ASCII 0x5D).
            rpm: Centrifuge speed in RPM (50–20000).
            runtime: Run time in seconds (1–59999).
            positioning_speed: 'slow' or 'fast' rotor positioning.
        """
        self.port = port
        self._adr = ord(address)
        self.rpm = rpm
        self.runtime = runtime
        self.positioning_speed = positioning_speed
        self._serial: serial.Serial | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def setup(self) -> None:
        """Open serial port and read SIOF register to unlock SELECT telegrams."""
        self._serial = serial.Serial(
            port=self.port,
            baudrate=9600,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=SERIAL_TIMEOUT_S,
        )
        siof = await self._enquire(P_SIOF)
        logger.info("Connected to Hettich ROTANTA 460 on %s (SIOF=%s).", self.port, siof)

    async def stop(self) -> None:
        """Close the serial connection."""
        if self._serial and self._serial.is_open:
            self._serial.close()
        logger.info("Disconnected from Hettich ROTANTA 460.")

    # ------------------------------------------------------------------
    # CentrifugeBackend interface
    # ------------------------------------------------------------------

    async def open_door(self) -> None:
        await self._verify_lock_2()
        await self._select(P_POS_CMD, CMD_OPEN_HATCH)
        await self._poll_until(
            self._hatch_is_open,
            timeout=HATCH_TIMEOUT_S,
            error_msg="Hatch did not open within timeout.",
        )
        logger.info("Hatch open.")

    async def close_door(self) -> None:
        await self._verify_lock_2()
        await self._select(P_POS_CMD, CMD_CLOSE_HATCH)
        await self._poll_until(
            self._hatch_is_closed,
            timeout=HATCH_TIMEOUT_S,
            error_msg="Hatch did not close within timeout.",
        )
        logger.info("Hatch closed.")

    async def lock_door(self) -> None:
        # The hatch locks mechanically when fully closed — no separate serial command.
        await self.close_door()

    async def unlock_door(self) -> None:
        await self.open_door()

    async def go_to_bucket1(self) -> None:
        await self._move_to_position(1)

    async def go_to_bucket2(self) -> None:
        await self._move_to_position(2)

    async def rotate_distance(self, distance) -> None:
        # PyLabRobot defines distance where 8000 = 360°.
        # The Hettich protocol uses discrete bucket positions, not continuous angles.
        raise NotImplementedError(
            "rotate_distance is not supported by the Hettich protocol. "
            "Use go_to_bucket1(), go_to_bucket2(), or go_to_position(n) instead."
        )

    async def lock_bucket(self) -> None:
        # The electromagnetic brake engages automatically when position is reached.
        logger.debug("lock_bucket: electromagnetic brake is already active after positioning.")

    async def unlock_bucket(self) -> None:
        """Terminate positioning mode, releasing the electromagnetic brake."""
        await self._select(P_POS_CMD, CMD_TERMINATE_POS)
        logger.info("Positioning mode terminated — brake released.")

    async def start_spin_cycle(self, g: float, duration: float, acceleration: float) -> None:
        """
        Start centrifugation using the RPM and runtime from the constructor.

        The Hettich protocol takes RPM directly; g-force conversion would require
        knowing the rotor radius and is left to a higher-level layer.
        Positioning mode is terminated first as required by the Hettich protocol.
        """
        await self._verify_lock_2()
        await self._select(P_POS_CMD, CMD_TERMINATE_POS)
        await self._select(P_SET_SPEED, format(self.rpm, "04X"))
        await self._select(P_RUNTIME, format(self.runtime, "04X"))
        await self._select(P_CONTROL_CMD, CMD_START)
        logger.info("Centrifugation started: %d RPM for %d s.", self.rpm, self.runtime)

    # ------------------------------------------------------------------
    # Extended helpers (used by automated load/unload protocols)
    # ------------------------------------------------------------------

    async def go_to_position(self, position: int) -> None:
        """
        Move the rotor to one of the 4 bucket positions.

        The standard load/unload order is [1, 3, 2, 4].
        PyLabRobot's go_to_bucket1/2 only cover positions 1 and 2;
        use this method directly for the full 4-position sequence.
        """
        await self._move_to_position(position)

    async def stop_spin(self) -> None:
        """Send a stop command during an in-progress centrifugation cycle."""
        await self._select(P_CONTROL_CMD, CMD_STOP)
        logger.info("Centrifugation stop command sent.")

    # ------------------------------------------------------------------
    # Manual hatch test methods (for hardware verification without a full protocol run)
    # ------------------------------------------------------------------

    async def open_hatch_test(self) -> None:
        """Open the hatch for manual testing."""
        await self.open_door()

    async def close_hatch_test(self) -> None:
        """Close the hatch for manual testing."""
        await self.close_door()

    # ------------------------------------------------------------------
    # Serial protocol internals
    # ------------------------------------------------------------------

    def _bcc(self, code: str, value: str) -> int:
        """BCC = XOR of CODE(5) + '='(1) + VALUE(4) + ETX(1)."""
        payload = code.encode("ascii") + b"=" + value.encode("ascii") + bytes([ETX])
        result = 0
        for b in payload:
            result ^= b
        return result

    def _build_enquiry(self, code: str) -> bytes:
        """Build ENQUIRY telegram: EOT ADDR CODE(5) ENQ — no STX, no ETX, no BCC."""
        return bytes([EOT, self._adr]) + code.encode("ascii") + bytes([ENQ])

    def _build_select(self, code: str, value: str) -> bytes:
        """Build SELECT telegram: EOT ADDR STX CODE(5) = VALUE(4) ETX BCC."""
        bcc = self._bcc(code, value)
        return (
            bytes([EOT, self._adr, STX])
            + code.encode("ascii")
            + b"="
            + value.encode("ascii")
            + bytes([ETX, bcc])
        )

    def _read_enquiry_response(self) -> bytes:
        """Read bytes until ETX (inclusive), then read the trailing BCC byte."""
        buf = bytearray()
        while True:
            b = self._serial.read(1)
            if not b:
                raise TimeoutError(
                    f"No ENQUIRY response from centrifuge "
                    f"(timeout={SERIAL_TIMEOUT_S}s)."
                )
            buf.extend(b)
            if b[0] == ETX:
                break
        bcc_byte = self._serial.read(1)
        if bcc_byte:
            buf.extend(bcc_byte)
        return bytes(buf)

    async def _enquire(self, code: str) -> str:
        """
        Send ENQUIRY telegram and return the 4-char hex VALUE string.

        Response layout: ADDR(1) STX(1) CODE(5) =(1) VALUE(4) ETX(1) BCC(1) = 14 bytes.
        VALUE starts at index 8.
        """
        self._serial.reset_input_buffer()
        self._serial.write(self._build_enquiry(code))
        resp = self._read_enquiry_response()
        if len(resp) < 12:
            raise RuntimeError(
                f"Short ENQUIRY response for param {code}: {resp.hex()}"
            )
        return resp[8:12].decode("ascii")

    async def _select(self, code: str, value: str) -> None:
        """
        Send SELECT telegram and verify ACK response.
        On NAK, reads SIOF (clears centrifuge error bits) then raises.
        """
        self._serial.reset_input_buffer()
        self._serial.write(self._build_select(code, value))
        resp = self._serial.read(2)  # ADDR ACK  or  ADDR NAK
        if len(resp) < 2:
            raise TimeoutError(
                f"No SELECT response for {code}={value} "
                f"(timeout={SERIAL_TIMEOUT_S}s)."
            )
        if resp[1] == NAK:
            await self._enquire(P_SIOF)  # reset centrifuge error bits before retry
            raise RuntimeError(
                f"NAK received for SELECT {code}={value}. "
                "Check LOCK 2 state and parameter range."
            )
        if resp[1] != ACK:
            raise RuntimeError(
                f"Unexpected SELECT response for {code}={value}: {resp.hex()}"
            )

    async def _get_pos_state(self) -> tuple[int, int]:
        """Return (highbyte, lowbyte) of param 00528 (positioning/hatch state)."""
        raw = await self._enquire(P_POS_STATE)
        val = int(raw, 16)
        return (val >> 8) & 0xFF, val & 0xFF

    async def _hatch_is_open(self) -> bool:
        highbyte, _ = await self._get_pos_state()
        return bool(highbyte & HATCH_OPEN_BIT)

    async def _hatch_is_closed(self) -> bool:
        highbyte, _ = await self._get_pos_state()
        return bool(highbyte & HATCH_CLOSED_BIT)

    async def _verify_lock_2(self) -> None:
        """Raise RuntimeError if centrifuge is not in LOCK 2 (PC control) mode."""
        raw = await self._enquire(P_STATE_2)
        key_lock = int(raw, 16) & 0x07  # lowbyte bits 2:0
        if key_lock != LOCK_2_VALUE:
            raise RuntimeError(
                f"Centrifuge is not in LOCK 2 mode (key-lock state={key_lock}). "
                "Turn the key switch to the right position."
            )

    async def _poll_until(
        self,
        condition,
        timeout: float,
        error_msg: str,
    ) -> None:
        """Poll an async condition every POLL_INTERVAL_S until True or timeout."""
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while loop.time() < deadline:
            if await condition():
                return
            await asyncio.sleep(POLL_INTERVAL_S)
        raise TimeoutError(error_msg)

    async def _move_to_position(self, position: int) -> None:
        """Set target position, issue move command, poll 00528 until reached or error."""
        if not (1 <= position <= ROTOR_POSITIONS):
            raise ValueError(
                f"Position must be 1–{ROTOR_POSITIONS}, got {position}."
            )
        # Highbyte = total number of rotor positions, lowbyte = target position number
        target = format((ROTOR_POSITIONS << 8) | position, "04X")
        await self._select(P_TARGET_POS, target)

        move_cmd = CMD_MOVE_FAST if self.positioning_speed == "fast" else CMD_MOVE_SLOW
        await self._select(P_POS_CMD, move_cmd)

        loop = asyncio.get_running_loop()
        deadline = loop.time() + POSITION_TIMEOUT_S
        while loop.time() < deadline:
            _, lowbyte = await self._get_pos_state()
            if lowbyte & POS_ERROR:
                raise RuntimeError(
                    f"Positioning error while moving to position {position}."
                )
            if lowbyte & POS_REACHED:
                logger.info("Rotor at position %d.", position)
                return
            await asyncio.sleep(POLL_INTERVAL_S)
        raise TimeoutError(
            f"Did not reach position {position} within {POSITION_TIMEOUT_S}s."
        )
