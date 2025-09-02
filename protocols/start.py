import asyncio
from pylabrobot.liquid_handling.backends.tecan.EVO_backend import EVOBackend

async def main():
    backend = EVOBackend()
    await backend.io.setup()
    resp1 = await backend.send_command("W1", "PIA")
    print(resp1)
    resp2 = await backend.send_command("C5", "PIA")
    print(resp2)
    resp3 = await backend.send_command("C1", "PIA")
    print(resp3)
    await backend.send_command("C1", "PAA",[14628, 1999, 2000, 1800, 900])
    await backend.send_command("C5", "PAA", [9241, 793, 0, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500])
    await backend.send_command("W1", "PAA", [-100, -700, 2000, 0, 280])
    # Optionally stop/close USB cleanly:
    await backend.stop()

if __name__ == "__main__":
    asyncio.run(main())