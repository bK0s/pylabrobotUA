import time


class MockCentrifuge:
    def __init__(self):
        self.hatch_open = False
        self.position = None
        self.running = False

    def open_hatch(self):
        print("[CENTRIFUGE] Opening hatch...")
        time.sleep(1)
        self.hatch_open = True
        print("[CENTRIFUGE] Hatch is now open.")

    def close_hatch(self):
        print("[CENTRIFUGE] Closing hatch...")
        time.sleep(1)
        self.hatch_open = False
        print("[CENTRIFUGE] Hatch is now closed.")

    def move_to_position(self, position: int):
        if not self.hatch_open:
            raise RuntimeError("Cannot move to loading position unless hatch is open.")

        print(f"[CENTRIFUGE] Moving rotor to bucket position {position}...")
        time.sleep(1)
        self.position = position
        print(f"[CENTRIFUGE] Reached bucket position {position}.")

    def start(self):
        if self.hatch_open:
            raise RuntimeError("Cannot start centrifuge while hatch is open.")

        print("[CENTRIFUGE] Starting centrifugation...")
        self.running = True

    def stop(self):
        print("[CENTRIFUGE] Stopping centrifugation...")
        self.running = False
        print("[CENTRIFUGE] Centrifuge stopped.")