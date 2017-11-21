#!/usr/bin/env python3

import daemon
from app import iothub_client_sample_run


with daemon.DaemonContext():
    iothub_client_sample_run

