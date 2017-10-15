
import gpiozero as IO

class Room:
    dev_file = ''
    pin = 17
    tempSetpoint = 5
    roomName = ''

    def _read_temp_raw(self):
        f = open(self.dev_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    
    def temperature(self):
        
        lines = self._read_temp_raw()
        # Analyze if the last 3 characters are 'YES'.
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self._read_temp_raw(dev_file)
        # Find the index of 't=' in a string.
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            # Read the temperature .
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c


    def __init__(self, roomName, dev_file, pin):
        self.tempSetpoint = 18
        self.dev_file = dev_file
        self.roomName = roomName
        self.relay