import asyncio
from pylabrobot.liquid_handling.backends.tecan.EVO_backend import EVOBackend
############### VARIABLES ###############

"""RoMa Variables"""
z_travel = 2000
z_tray = 20
r_tray = 900
g_tray_open = 900
g_tray_closed = 400

"""Location Variables"""
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

plate_1 = Point(x=10, y=20)
plate_2 = Point(x=10, y=20)
plate_3 = Point(x=10, y=20)
plate_4 = Point(x=10, y=20)
plate_5 = Point(x=10, y=20)
plate_6 = Point(x=10, y=20)

############### BEGIN AND END FUNCTIONS ###############

"""begin will establish USB connection, initialize the FreedomEVO
  arms and move them to initial positions"""
#STILL REQUIRES PULNGER INITIALIZATION FOR LiHa
async def begin():
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

"""end will return arms to initial positions and terminate USB connection"""
async def end():
    await backend.send_command("C1", "PAA",[14628, 1999, 2000, 1800, 900])
    await backend.send_command("C5", "PAA", [9241, 793, 0, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500])
    await backend.send_command("W1", "PAA", [-100, -700, 2000, 0, 280])
    await backend.stop
############### ROMA FUNCTIONS ###############

async def tray_pick_up(plate):
  await backend.send_command("C1", "PAZ", [z_travel])
  await backend.send_command("C1", "PAA", [plate.x, plate.y, None, r_tray, g_tray_open])
  await backend.send_command("C1", "PAZ", [z_tray])
  await backend.send_command("C1", "PAG", [g_tray_closed])
  await backend.send_command("C1", "PAZ", [z_travel])

async def tray_put_down(plate):
  await backend.send_command("C1", "PAZ", [z_travel])
  await backend.send_command("C1", "PAA", [plate.x, plate.y, None, r_tray, None])
  await backend.send_command("C1", "PAZ", [z_tray])
  await backend.send_command("C1", "PAG", [g_tray_open])
  await backend.send_command("C1", "PAZ", [z_travel])
