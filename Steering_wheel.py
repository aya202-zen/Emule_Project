import RPi.GPIO as GPIO
import socket
import time

# UDP network configuration
serverAddressPort = ("192.168.10.27", 20003)

# GPIO configuration
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # North
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # East
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # South
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # West

# Sensor order clockwise: N -> E -> S -> W -> N
SENSORS = ["N", "E", "S", "W"]
PINS    = {"N": 18, "E": 15, "S": 16, "W": 22}

direction   = 0
last_active = None

print("=== Steering wheel detection started ===")
print("Pin 18 = North | Pin 15 = East")
print("Pin 16 = South | Pin 22 = West")
print("========================================")

def get_active_sensor():
    """Return the currently triggered sensor, or None if none/multiple."""
    active = [s for s in SENSORS if GPIO.input(PINS[s]) == False]
    if len(active) == 1:
        return active[0]
    return None

def get_rotation(prev, curr):
    """
    Returns +90 (clockwise) or -90 (counter-clockwise)
    based on the transition between two adjacent sensors.
    """
    idx_prev = SENSORS.index(prev)
    idx_curr = SENSORS.index(curr)
    diff = (idx_curr - idx_prev) % 4

    if diff == 1:
        return +90    # clockwise
    elif diff == 3:
        return -90    # counter-clockwise
    else:
        return None   # skipped a sensor, ignore

try:
    while True:
        time.sleep(0.02)  # 20ms debounce

        active = get_active_sensor()

        if active is None:
            continue

        if active == last_active:
            continue

        # New sensor detected
        if last_active is not None:
            rotation = get_rotation(last_active, active)
            if rotation is not None:
                direction += rotation
                print(f"Rotation: {'+' if rotation > 0 else ''}{rotation}° | "
                      f"Total direction: {direction}° | "
                      f"{last_active} ? {active}")

                # Send via UDP
                UDPClientSocket = socket.socket(
                    family=socket.AF_INET,
                    type=socket.SOCK_DGRAM
                )
                UDPClientSocket.sendto(
                    str.encode(str(direction)),
                    serverAddressPort
                )
                UDPClientSocket.close()
        else:
            print(f"First sensor detected: {active}")

        last_active = active

except KeyboardInterrupt:
    print("\nProgram stopped.")
    GPIO.cleanup()