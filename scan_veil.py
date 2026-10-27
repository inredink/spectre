
import time
import board

def main():
    print("=" * 44)
    print(" SPECTRE | VEIL Hardware Diagnostic")
    print("=" * 44)
    print("Initializing MCP2221A I2C interface...")

    try:
        i2c = board.I2C()
        print("I2C interface initialized.")
    except Exception as exc:
        print(f"Could not initialize I2C: {exc}")
        return

    while not i2c.try_lock():
        time.sleep(0.01)

    try:
        addresses = i2c.scan()
        print("\nI2C devices detected:")

        if not addresses:
            print("No devices found.")
            print("If VEIL is not connected, this is expected.")
        else:
            for address in addresses:
                print(f"  Device at 0x{address:02X}")

        print("\nDiagnostic complete.")
    except Exception as exc:
        print(f"I2C scan failed: {exc}")
    finally:
        i2c.unlock()

if __name__ == "__main__":
    main()
