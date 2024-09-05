import time

# Set LED to blink at 1-second intervals (connected to VPN)
def set_led_blink_1s():
    with open('/sys/class/leds/led0/trigger', 'w') as f:
        f.write('timer')  # Set LED trigger to timer
    with open('/sys/class/leds/led0/delay_on', 'w') as f:
        f.write('1000')  # 1 second on
    with open('/sys/class/leds/led0/delay_off', 'w') as f:
        f.write('1000')  # 1 second off

# Set LED to blink at 5-second intervals (disconnected from VPN but connected to internet)
def set_led_blink_5s():
    with open('/sys/class/leds/led0/trigger', 'w') as f:
        f.write('timer')
    with open('/sys/class/leds/led0/delay_on', 'w') as f:
        f.write('1000')  # 1 second on
    with open('/sys/class/leds/led0/delay_off', 'w') as f:
        f.write('5000')  # 5 seconds off

# Turn LED off
def set_led_off():
    with open('/sys/class/leds/led0/trigger', 'w') as f:
        f.write('none')  # Disable trigger
    with open('/sys/class/leds/led0/brightness', 'w') as f:
        f.write('0')  # Turn LED off