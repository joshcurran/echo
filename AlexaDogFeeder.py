import RPi.GPIO as GPIO
import time
import wiringpi
import fauxmo
import logging

from debounce_handler import debounce_handler

logging.basicConfig(level=logging.DEBUG)

class device_handler(debounce_handler):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """
    TRIGGERS = {"Dog Feeder": 52000}

    def act(self, client_address, state):
        rotate_once();
        print "Fed by Alexa"
        print "State", state, "from client @", client_address
        return True

buttonpin = 23
servopin = 18
delay_after = 1.5
servo_duration = 3.0
speed = 500
off = 0

#Setup the servo in wiringpi
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(servopin, wiringpi.GPIO.PWM_OUTPUT)
wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)

#Setup the button in GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(buttonpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Rotate the servo
def rotate_once():
    wiringpi.pwmWrite(servopin, speed)
    time.sleep(servo_duration)
    wiringpi.pwmWrite(servopin, off)

if __name__ == "__main__":
    # Startup the fauxmo server
    fauxmo.DEBUG = True
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)

    # Register the device callback as a fauxmo handler
    d = device_handler()
    for trig, port in d.TRIGGERS.items():
        fauxmo.fauxmo(trig, u, p, None, port, d)

    # Loop and poll for incoming Echo requests
    logging.debug("Entering fauxmo polling loop")
    while True:
        try:
            # Allow time for a ctrl-c to stop the process
            p.poll(100)
            input_state = GPIO.input(buttonpin)
            if input_state == False:
              print('Dog was fed')
              rotate_once()
              time.sleep(delay_after)
            time.sleep(0.1)
        except Exception, e:
            logging.critical("Critical exception: " + str(e))
            break

