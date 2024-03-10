import network
import machine
from machine import TouchPad, Pin
import time
import esp32
import espnow
import utime
import aioespnow
import asyncio


# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

# Initialize ESP-NOW
esp = espnow.ESPNow()
esp.active(True)

# Define the MAC address of the receiving ESP32 (ESP32 B)
peer = b'L\x11\xaew\xc6L'
esp.add_peer(peer)

# Define pins
PIR_PIN1 = 23    # PIR sensor 1
PIR_PIN2 = 18    # PIR sensor 2
PIR_PIN3 = 4    # PIR sensor 3
LED_PIN1 = 26    # LED
LED_PIN2 = 27    # LED
LED_PIN3 = 25    # LED

ms_sleep_time = 60000

#for touch sensor
capacitiveValue = 300
threshold = 30 # Threshold to be adjusted
touch_pin_1 = TouchPad(Pin(2, mode=Pin.IN))
touch_pin_2 = TouchPad(Pin(15)) #, mode=Pin.IN))

# Initialize the PIR sensor pin as an input pin
pir_sensor1 = machine.Pin(PIR_PIN1, machine.Pin.IN, machine.Pin.PULL_DOWN)
pir_sensor2 = machine.Pin(PIR_PIN2, machine.Pin.IN, machine.Pin.PULL_DOWN)
pir_sensor3 = machine.Pin(PIR_PIN3, machine.Pin.IN, machine.Pin.PULL_DOWN)
# Initialize the LED pin as an output pin
led1 = machine.Pin(LED_PIN1, machine.Pin.OUT)
led2 = machine.Pin(LED_PIN2, machine.Pin.OUT)
led3 = machine.Pin(LED_PIN3, machine.Pin.OUT)

# Global flag to indicate motion detected
motion_detected_flag1 = False
motion_detected_flag2 = False
motion_detected_flag3 = False

# Function to handle the interrupt
def motion_detected1(pin):
    global motion_detected_flag1
    print("Motion detected on one!")
    motion_detected_flag1 = True
    print('function motion 1:', motion_detected_flag1)
    
def motion_detected2(pin):
    global motion_detected_flag2
    print("Motion detected on two!")
    motion_detected_flag2 = True
    print('function motion 2:', motion_detected_flag2)
    
def motion_detected3(pin):
    global motion_detected_flag3
    print("Motion detected on three!")
    motion_detected_flag3 = True
    print('function motion 3:', motion_detected_flag3)

# Attach the interrupt to the PIR sensor pin
pir_sensor1.irq(trigger=machine.Pin.IRQ_RISING, handler=motion_detected1)
pir_sensor2.irq(trigger=machine.Pin.IRQ_RISING, handler=motion_detected2)
pir_sensor3.irq(trigger=machine.Pin.IRQ_RISING, handler=motion_detected3)

# touch_pin_2.config(100)               # configure the threshold at which the pin is considered touched
# esp32.wake_on_touch(True)
# machine.lightsleep(60000)

# Main loop
# async def send_button_state(espnow):
while True:
    flag_list = [motion_detected_flag1, motion_detected_flag2, motion_detected_flag3]
#     message = str(motion_detected_flag1) + ',' + str(motion_detected_flag2) + ',' + str(motion_detected_flag3)
#     esp.send(peer, message)

    if flag_list.count(True) >= 2:
        print('alarm')
        message = 'alarm'
        esp.send(peer, message)
        led3.value(1)
        time.sleep(5)
        led3.value(0)
    #     time.sleep(1)
        motion_detected_flag1 = False
        motion_detected_flag2 = False
        motion_detected_flag3 = False
#     else:
#         message = str(motion_detected_flag1) + ',' + str(motion_detected_flag2) + ',' + str(motion_detected_flag3)
#         print(message)
#         esp.send(peer, message)
#         time.sleep(5)
#         motion_detected_flag1 = False
#         motion_detected_flag2 = False
#         motion_detected_flag3 = False
        
#         message = str(motion_detected_flag1) + ',' + str(motion_detected_flag2) + ',' + str(motion_detected_flag3)
#         print(message)
#         time.sleep(10)
# #         print(f"Sending command : {message}")
#         esp.send(peer, message)
#         motion_detected_flag1 = False
#         motion_detected_flag2 = False
#         motion_detected_flag3 = False
        

#     if motion_detected_flag1 and motion_detected_flag2:
#         message = "motion_1_2_On"
#         print(f"Sending command : {message}")
#         esp.send(peer, message)
#         led3.value(1)
#         time.sleep(5)
#         led3.value(0)
#         motion_detected_flag1 = False
#         motion_detected_flag2 = False
# #     else:
# #         message = "motionOneOff"
# #         print(f"Sending command : {message}")
# #         esp.send(peer, message)
# #         motion_detected_flag1 = False
# # #             print("first sensor motion detected.")
# # #             led1.value(1)  # Turn on the LED
# # #             time.sleep(2)  # Keep the LED on for 5 seconds
# # #             led1.value(0)  # Turn off the LED
# # #             motion_detected_flag1 = False
# # #             print(motion_detected_flag1)
#     elif motion_detected_flag2 and motion_detected_flag3 :
#             message = "motion_2_3_On"
#             print(f"Sending command : {message}")
#             esp.send(peer, message)
#             led3.value(1)
#             time.sleep(5)
#             led3.value(0)
#             motion_detected_flag2 = False
#             motion_detected_flag3 = False
# #         else:
# #             message = "motionTwoOff"
# #             print(f"Sending command : {message}")
# #             esp.send(peer, message)
# #             motion_detected_flag2 = False
# # #             print("second sensor motion detected.")
# # #             led2.value(1)  # Turn on the LED
# # #             time.sleep(2)  # Keep the LED on for 5 seconds
# # #             led2.value(0)  # Turn off the 
# # #             motion_detected_flag2 = False
# # #             print(motion_detected_flag2)
#     elif motion_detected_flag3 and motion_detected_flag1:
#                 message = "motion_3_1_On"
#                 print(f"Sending command : {message}")
#                 esp.send(peer, message)
#                 led3.value(1)
#                 time.sleep(5)
#                 led3.value(0)
#                 motion_detected_flag3 = False
#                 motion_detected_flag1 = False
#             else:
#                 message = "motionThreeOff"
#                 print(f"Sending command : {message}")
#                 esp.send(peer, message)
#                 motion_detected_flag3 = False
#     time.sleep(5)
#             print("third sensor motion detected.")
#             led3.value(1)  # Turn on the LED
#             time.sleep(2)  # Keep the LED on for 5 seconds
#             led3.value(0)  # Turn off the 
#             motion_detected_flag3 = False
#             print(motion_detected_flag3)
#     await asyncio.sleep_ms(10)  # Adjust the polling interval as needed
        
        
# asyncio.run(send_button_state(esp))
        
#     print('Im awake. Going to sleep in 10 seconds')
#     time.sleep(10)
#     print('Going to sleep now')
#     deepsleep()
        
#     touch_pin_2.config(30)               # configure the threshold at which the pin is considered touched
#     esp32.wake_on_touch(True)
#     machine.lightsleep(ms_sleep_time)
#     if motion_detected_flag:
#         led.value(1)  # Turn on the LED
#         time.sleep(5)  # Keep the LED on for 5 seconds
#         led.value(0)  # Turn off the LED
#         motion_detected_flag = False
#         print(motion_detected_flag)
#     capacitiveValue_1 = touch_pin_1.read()
#     capacitiveValue_2 = touch_pin_2.read()
#     time.sleep(5)
#     print('Touch value 1:', capacitiveValue_1)
#     print('Touch value 2:', capacitiveValue_2)
#     touch_pin_2.config(30)               # configure the threshold at which the pin is considered touched
#     esp32.wake_on_touch(True)
#     machine.lightsleep()
    
#     time

