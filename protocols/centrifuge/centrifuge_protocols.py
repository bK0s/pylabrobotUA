from centrifuge_mock import MockCentrifuge


def load_centrifuge(centrifuge: MockCentrifuge):
    print("\n=== Starting centrifuge load protocol ===")

    centrifuge.open_hatch()

    # Based on old Tecan load order: positions 1, 3, 2, 4
    for bucket_position in [1, 3, 2, 4]:
        centrifuge.move_to_position(bucket_position)
        print(f"[ROBOT ARM] Pretend loading bucket into position {bucket_position}")

    centrifuge.close_hatch()

    print("=== Centrifuge load protocol complete ===\n")


def run_spin_protocol(centrifuge: MockCentrifuge):
    print("\n=== Starting centrifuge spin protocol ===")

    centrifuge.start()
    print("[CENTRIFUGE] Pretend spinning for 5 seconds...")
    
    import time
    time.sleep(5)

    centrifuge.stop()

    print("=== Centrifuge spin protocol complete ===\n")


if __name__ == "__main__":
    centrifuge = MockCentrifuge()

    load_centrifuge(centrifuge)
    run_spin_protocol(centrifuge)