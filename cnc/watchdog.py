import threading
import time

from cnc import hal


class HardwareWatchdog(threading.Thread):
    def __init__(self):
        """ Run feed loop for hardware watchdog.
        """
        super(HardwareWatchdog, self).__init__()
        self.setDaemon(True)
        self.start()

    def run(self):
        while True:
            hal.watchdog_feed()
            time.sleep(3)

# for test purpose
if __name__ == "__main__":
    hal.init()
    hal.fan_control(True)
    print("Fan is on, it should turn off automatically in ~15 seconds."
          "\nExiting...")
