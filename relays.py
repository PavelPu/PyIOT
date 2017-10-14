#!/usr/bin/env python3

import gpiozero as IO


class Relays:

    def __init__(self):
        self.dining = IO.DigitalOutputDevice(17)
        self.bath = IO.DigitalOutputDevice(27)
        self.waterHeater = IO.DigitalOutputDevice(22)
        self.diningState = self.dining.value
