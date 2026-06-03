import RPi.GPIO as GPIO
import socket
import time

# UDP network configuration
serverAddressPort = ("192.168.0.67", 20002)
bufferSize = 1024

# GPIO configuration
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_UP)

gear = "N"
last_gear = ""

print("=== Speed detection started ===")
print("Pin 11 = R (Reverse)")
print("Pin 13 = H (High)")
print("Pin 37 = L (Low)")
print("None   = N (Neutral)")
print("================================")
print()
print("=== DIAGNOSTIC - Raw pin states ===")

try:
    while True:
        time.sleep(0.05)

        # Raw pin reading for diagnostic
        p11 = GPIO.input(11)
        p13 = GPIO.input(13)
        p37 = GPIO.input(37)
        print(f"Pin 11 (R): {p11} | Pin 13 (H): {p13} | Pin 37 (L): {p37}")

        # Gear detection
        if p13 == False:
            gear = "H"
        elif p37 == False:
            gear = "L"
        elif p11 == False:
            gear = "R"
        else:
            gear = "N"

        # Send only on change
        if gear != last_gear:
            print(f">>> Gear changed : {gear}")
            UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPClientSocket.sendto(str.encode(gear), serverAddressPort)
            last_gear = gear

except KeyboardInterrupt:
    print("\nProgram stopped.")
    GPIO.cleanup()