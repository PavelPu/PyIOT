#!/usr/bin/env python

import gpiozero as IO

dining = IO.DigitalOutputDevice(17)

print(dining.value)

val = dining.value

print(val)

dining.off()


print(val)

print(dining.value)