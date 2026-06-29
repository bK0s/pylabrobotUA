import asyncio

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import LiquidHandlerChatterboxBackend
from pylabrobot.visualizer.visualizer import Visualizer
from pylabrobot.resources.tecan import EVO200Deck
from pylabrobot.resources.tube_rack import TubeRack
from pylabrobot.resources.coordinate import Coordinate
from pylabrobot.resources import (
    MP_3Pos_Flat,                   # Tecan part no. 10612624
    Washstation_2Grid_Trough_DiTi,  # Tecan part no. 10650037
    DiTi_3Pos,                      # Tecan part no. 10613022
    MP_4Pos_flat,                   # Tecan part no. 30013061
    MP_3Pos,                        # Tecan part no. 10612604
    DiTi_1000ul_CL_Filter_LiHa,
    Microplate_96_Well,
)
from pylabrobot.resources.tecan.tube_carrier import tecan_tube_carrier_16, test_tube


async def main():
    lh = LiquidHandler(
        backend=LiquidHandlerChatterboxBackend(),
        deck=EVO200Deck(origin=Coordinate(0, 0, 0)),
    )
    await lh.setup()
    vis = Visualizer(resource=lh)
    await vis.setup()

    flat_carrier_1 = MP_3Pos_Flat(name="Flat Carrier 1")
    flat_carrier_2 = MP_3Pos_Flat(name="Flat Carrier 2")
    washstation = Washstation_2Grid_Trough_DiTi(name="Wash Station")
    tip_carrier = DiTi_3Pos(name="Disposable Tip Carrier")

    flat_carrier_1[0] = well_rack0 = Microplate_96_Well(name="well_0")
    flat_carrier_1[1] = well_rack1 = Microplate_96_Well(name="well_1")
    flat_carrier_1[2] = well_rack2 = Microplate_96_Well(name="well_2")
    flat_carrier_2[0] = well_rack3 = Microplate_96_Well(name="well_3")
    flat_carrier_2[1] = well_rack4 = Microplate_96_Well(name="well_4")
    flat_carrier_2[2] = well_rack5 = Microplate_96_Well(name="well_5")

    tip_carrier[0] = tip_rack0 = DiTi_1000ul_CL_Filter_LiHa(name="tips_0")
    tip_carrier[1] = tip_rack1 = DiTi_1000ul_CL_Filter_LiHa(name="tips_1")
    tip_carrier[2] = tip_rack2 = DiTi_1000ul_CL_Filter_LiHa(name="tips_2")

    centri_bucket_car = MP_4Pos_flat(name="Centrifuge Bucket Carrier")
    regrip = MP_3Pos(name="Regrip")

    lh.get_resource("wash_station").unassign()

    lh.deck.assign_child_resource(flat_carrier_1, rails=22)
    lh.deck.assign_child_resource(flat_carrier_2, rails=28)
    lh.deck.assign_child_resource(washstation, rails=38)
    lh.deck.assign_child_resource(tip_carrier, rails=41)
    lh.deck.assign_child_resource(centri_bucket_car, rails=48)
    lh.deck.assign_child_resource(regrip, rails=61)

    for i in range(9):
        lh.deck.assign_child_resource(tecan_tube_carrier_16(f"tube_carrier_{i}"), rails=i + 12)
        carrier = lh.get_resource(f"tube_carrier_{i}")
        for j in range(16):
            carrier[j] = test_tube(f"test_tube_{i}_{j}")

    lh.summary()

    await asyncio.Event().wait()  # keep servers alive until Ctrl+C


if __name__ == "__main__":
    asyncio.run(main())
