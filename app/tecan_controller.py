import threading
import queue
from typing import Dict
import asyncio

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import LiquidHandlerChatterboxBackend
from pylabrobot.liquid_handling.backends import EVOBackend
from pylabrobot.machines import backend
from pylabrobot.resources import deck
from pylabrobot.resources.tecan.tecan_decks import EVO200Deck

class RobotController:
  def __init__(self, lh):
    self.queue: queue.Queue = queue.Queue()
    self.jobs: Dict = {}
    self.running: bool = False
    self.lh: LiquidHandler = lh
    self.status = None

  async def setup(self):
    if not self.running:
      print("Not running")
      pass
    await self.lh.setup()

  def start(self):
    if self.running:
      print("Instance already running")
    while self.running:
      job_id, cmd, payload = self.queue.get()
      try:
        pass
      except:
        print("theres a problem")


  async def run(self):
    print("Starting...\n")

    # Set up Liquid Handler
    self.lh = LiquidHandler(backend=LiquidHandlerChatterboxBackend(), deck=EVO200Deck())
    print(f"Machine Backend: {self.lh.backend}")
    # self.lh.deck.load_from_json_file("pylabrobot/Tecan_layout_test.json")

    await self.lh.setup()
    # self.lh.deck = deck.Deck.load_from_json_file("pylabrobot/Tecan_layout_test.json")

    # Display deck layout summary
    # self.lh.summary()
    print(self.lh.deck.summary())
    print("done\n")

if __name__ == '__main__':
  c = RobotController(lh=LiquidHandler)
  asyncio.run(c.run())
  # asyncio.run(c.lh.summary())
