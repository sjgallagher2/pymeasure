#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from enum import Enum,IntFlag
from time import sleep


from pymeasure.adapters.adapter import Adapter
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set

try:
    from enum import StrEnum
except ImportError:
    class StrEnum(str, Enum):
        """Until StrEnum is broadly available / pymeasure relies on python <=
        3.10.x."""

        def __str__(self):
            return self.value


class Modes(IntFlag):
    RUN=1
    HOLD=2
    CONFIGURATION=4
    CALIBRATION=8
    ALARM_SILENC_ACTIVE=16
    OFF=32

def wait(v=None):
    sleep(0.1)
    return v

class InterfaceType(Enum):
    NONE = "None"
    SYNERGY488 = "Synergy 488"
    ICS4814 = "ICS Model 4814"

class Watlow942(Instrument):
    """Represents a Watlow 942 process controller using ANSI X3.28 protocol."""
    def __init__(self, adapter: Adapter | int | str,
                 name: str = "Watlow 942 Process Controller",
                 **kwargs):
        super().__init__(adapter, name, read_termination='\r\n',write_termination='\n',
                              **kwargs)
        self.interface = InterfaceType.ICS4814  # Purely for informational purposes
        self.query_delay = 0.1
        self.write('0')  # address 0
        self.wait_for(self.query_delay)
        ack = self.read()
        # Don't need to check the ACK for now, but in case it's needed later:
        # if ack == '0ACK':
        #     # X3.28 communication successfully started
        # else:
        #     # X3.28 communication was already started
        self.wait_for(self.query_delay)

    def wait_for(self, query_delay=None):
        """Wait for some time. Used by 'ask' to wait before reading.

        :param query_delay: Delay between writing and reading in seconds.
            None means :attr:`query_delay`.
        """
        super().wait_for(self.query_delay if query_delay is None else query_delay)

    def check_set_errors(self):
        """Check for errors after having set a property.

        Called if :code:`check_set_errors=True` is set for that property.
        """
        wait()
        ack = self.read()
        if ack != 'ACK':
            print(f"Warning: expected ACK but received {ack}")
        # else:
            # print("ACK received")
        return []

    temperature_setpoint = Instrument.control(
        "? SP1","= SP1 %d",
        """Control chamber setpoint 1. Units, decimal format, and limits must be queried.""",
        get_process=wait,  # impose delay
        check_set_errors=True,
    )
    temperature = Instrument.measurement(
        "? C1",
        """Measure chamber process variable 1. Units and decimal format must be queried.""",
        get_process=wait,  # impose delay
    )
    decimal_format = Instrument.control(
        "? DEC","= DEC %d",
        """Control fixed-point decimal format. Can be 0, 1, or 2 decimals (000, 00.0, 0.00).""",
        validator=strict_discrete_set,
        values=[0,1,2],
        get_process=wait,  # impose delay
        check_set_errors=True,
    )
    temperature_unit = Instrument.control(
        "? CF","= CF %d",
        """Control temperature units. Can be 'C' or 'F'.""",
        validator=strict_discrete_set,
        values={'C':0,'F':1},
        map_values=True,
        get_process=wait,  # impose delay
        check_set_errors=True,
    )
    range_high = Instrument.measurement(
        "? RH",
        """Get upper temperature range.""",
        get_process=wait,  # impose delay
    )
    range_low = Instrument.measurement(
        "? RL",
        """Get lower temperature range.""",
        get_process=wait,  # impose delay
    )
    run_mode = Instrument.measurement(
        "? MODE",
        """Get run mode of the chamber. The mode will be one of:
            RUN|HOLD|CONFIGURATION|CALIBRATION|ALARM_SILENCE_ACTIVE|OFF.""",
        get_process=lambda md: Modes(int(md))
    )
