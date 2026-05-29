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
from pylabrobot.resources import Coordinate

from pylabrobot.resources import (
      MP_3Pos_Flat, #Tecan part no. 1061262
      Washstation_2Grid_Trough_DiTi, #Tecan part no. 10650037
      DiTi_3Pos, #Tecan part no. 10613022
      MP_4Pos_flat, #Tecan part no. 30013061
      MP_3Pos, #Tecan part no. 10612604
      DiTi_1000ul_CL_Filter_LiHa, #unsure if correct tip
      Microplate_96_Well #unsure if correct wellplate
      )

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

  def set_layout(self, layout=None):
    if layout != None:
      self.lh.deck = layout
    else:
      lh = self.lh
      print("Setting Layout")

      flat_carrier_1 = MP_3Pos_Flat(name="Flat Carrier 1")
      flat_carrier_2 = MP_3Pos_Flat(name="Flat Carrier 2")
      washstation = Washstation_2Grid_Trough_DiTi(name="Wash Station")
      washstation.off_x=10.0
      washstation.off_y=10.0
      tip_carrier = DiTi_3Pos(name="Disposable Tip Carrier")
      flat_carrier_1[0]= well_rack0 = Microplate_96_Well(name="well_0")
      flat_carrier_1[1]= well_rack1 = Microplate_96_Well(name="well_1")
      flat_carrier_1[2]= well_rack2 = Microplate_96_Well(name="well_2")
      flat_carrier_2[0]= well_rack3 = Microplate_96_Well(name="well_3")
      flat_carrier_2[1]= well_rack4 = Microplate_96_Well(name="well_4")
      flat_carrier_2[2]= well_rack5 = Microplate_96_Well(name="well_5")
      tip_carrier[0]= tip_rack0 = DiTi_1000ul_CL_Filter_LiHa(name="tips_0")
      tip_carrier[1]= tip_rack1 = DiTi_1000ul_CL_Filter_LiHa(name="tips_1")
      tip_carrier[2]= tip_rack2 = DiTi_1000ul_CL_Filter_LiHa(name="tips_2")
      centri_bucket_car = MP_4Pos_flat(name="Centrifuge Bucket Carrier")
      regrip = MP_3Pos(name="Regrip")

      lh.deck.assign_child_resource(washstation, location= Coordinate(915.000, 003.000, 000.000))
      lh.deck.assign_child_resource(tip_carrier, Coordinate(988.000, -04.300, 000.000))
      # lh.deck.assign_child_resource(centri_bucket_car, rails=48)
      # lh.deck.assign_child_resource(regrip, rails=61)



  async def run(self):
    print("Starting...\n")

    # Set up Liquid Handler
    self.lh = LiquidHandler(backend=LiquidHandlerChatterboxBackend(), deck=EVO200Deck())
    print(f"Machine Backend: {self.lh.backend}")
    # self.lh.deck.load_from_json_file("pylabrobot/Tecan_layout_test.json")

    await self.lh.setup()
    self.set_layout()
    # self.lh.deck = deck.Deck.load_from_json_file("pylabrobot/Tecan_layout_test.json")

    # Display deck layout summary
    # self.lh.summary()
    print(self.lh.deck.summary())
    # print("done\n")

if __name__ == '__main__':
  c = RobotController(lh=LiquidHandler)
  asyncio.run(c.run())
  # asyncio.run(c.lh.summary())
