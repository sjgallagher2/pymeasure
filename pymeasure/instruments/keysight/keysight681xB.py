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
from enum import Enum

import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, truncated_range

try:
    from enum import StrEnum
except ImportError:
    class StrEnum(str, Enum):
        """Until StrEnum is broadly available / pymeasure relies on python <=
        3.10.x."""

        def __str__(self):
            return self.value

class Functions(StrEnum):
    SINE="SIN"
    SQUARE="SQU"
    CLIPPED_SINE="CSIN"  # Clipped sinewave output. Both positive and negative peak amplitudes
                         # are clipped at a value determined by the FUNC:CSIN command.

class Modes(StrEnum):
    FIXED="FIX"   # unaffected by a triggered output transient.
    STEP="STEP"   # programmed to the value set by X:TRIG when a triggered transient occurs.
    PULSE="PULS"  # changed to the value set by X:TRIG for a duration determined by the pulse
                  # commands.
    LIST="LIST"   # controlled by the waveform shape list when a triggered transient occurs.

class Keysight681xB(SCPIMixin, Instrument):
    """Represents the Keysight 6811B, 6812B, and 6813B AC Power Source/Analyzers."""


    def __init__(self, adapter, name="Keysight 681xB AC Power Source/Analyzer",
                 **kwargs):
        super().__init__(adapter, name, **kwargs)

    voltage_setpoint = Instrument.control(
        "VOLT?", "VOLT %f",
        """Control the AC RMS voltage amplitude setpoint in volts.""",
        validator=truncated_range,
        values=[0,300],
    )
    current_setpoint = Instrument.control(
        "CURRENT?","CURRENT %f",
        """Control the AC RMS current limit setpoint in amperes.""",
        validator=truncated_range,
        values=[0,13.0],  # limit for 6813B only
    )
    frequency_setpoint = Instrument.control(
        "FREQ?","FREQ %f",
        """Control the frequency setpoint in hertz""",
        validator=truncated_range,
        values=[45,1000]
    )
    output_function = Instrument.control(
        "FUNC?","FUNC %s",
        """Control the output function of the ac source. Can be SIN, SQU, CSIN, or a user
        waveform.""",
    )

"""
=== LIMITS ===
300Vrms max
13Arms max (6813B)
1350W max (6813B
+/- 425VDC max
10ADC max (6813B)
45Hz-1kHz frequency
-----------------------

=== SET POINT ===
VOLT <V>
VOLT:TRIG <V>
VOLT:MODE FIX|STEP|PULS|LIST
VOLT:OFFSET <V>
VOLT:OFFSET:MODE FIX|STEP|PULS|LIST
VOLT:OFFSET:TRIG <V>
VOLT:OFFSET:SLEW <S>
VOLT:OFFSET:SLEW INFINITY
VOLT:OFFSET:SLEW:MODE FIX|STEP|PULSE|LIST
VOLT:OFFSET:SLEW:TRIG <S>
VOLT:OFFSET:SLEW:TRIG INFINITY
VOLT:PROT <V>
VOLT:PROT:STATE OFF|ON
VOLT:RANGE <V>
VOLT:SENSE:DETECTOR RTIME|RMS
VOLT:SENSE:SOURCE INTERNAL|EXTERNAL
VOLT:SLEW <S>
VOLT:SLEW INFINITY
VOLT:SLEW:MODE FIX|STEP|PULS|LIST
VOLT:SLEW:TRIG <S>
VOLT:SLEW:TRIG INFINITY
CURRENT <I>
CURR:PEAK <I>
CURR:PEAK:MODE FIX|STEP|PULS|LIST
CURR:TRIG <I>
CURR:PROT:STATE OFF|ON
FREQ <F>
FREQ:MODE FIX|STEP|PULS|LIST
FREQ:SLEW <S>
FREQ:SLEW INFINITY
FREQ:SLEW:MODE FIX|STEP|PULS|LIST
FREQ:SLEW:TRIG <S>
FREQ:TRIG <F>
FUNC SIN|SQU|CSIN|<user>
FUNC:MODE FIX|STEP|PULS|LIST
FUNC:TRIG SIN|SQU|CSIN|<table>
FUNC:CSIN <N>
PHASE <P>
PHASE:MODE FIX|STEP|PULS|LIST
PHASE:TRIG <P>

=== OUTPUT ===
OUTP:STATE OFF|ON
OUTPUT:COUPLING AC|DC
OUTPUT:DFI:STATE OFF|ON
OUTPUT:IMPEDANCE:STATE ON|OFF
OUTPUT:IMPEDANCE:REAL <R>
OUTPUT:IMPEDANCE:REACTIVE <X>
OUTPUT:PON:STATE RST|RCL0
OUTPUT:PROT:CLEAR
OUTPUT:PROT:DELAY <t>

=== MEASUREMENTS ===
MEAS:VOLT:DC?
MEAS:VOLT:AC?
MEAS:VOLT:ACDC?
MEAS:VOLT:HARMONIC:AMPL? <N>          for harmonic N
MEAS:VOLT:HARMONIC:PHASE? <N>         for harmonic N
MEAS:VOLT:HARMONIC:THD?
MEAS:VOLT:
MEAS:CURR:DC?
MEAS:CURR:AC?
MEAS:CURR:ACDC?
MEAS:CURR:AMPL:MAX?
MEAS:CURR:CRESTFACTOR?
MEAS:CURR:HARMONIC:AMPL? <N>          for harmonic N
MEAS:CURR:HARMONIC:PHASE? <N>         for harmonic N
MEAS:CURR:HARMONIC:THD?
MEAS:CURR:NEUTRAL:DC?
MEAS:CURR:NEUTRAL:
MEAS:CURR:NEUTRAL:
MEAS:CURR:NEUTRAL:
MEAS:CURR:NEUT:HARMONIC:AMPL? <N>     for harmonic N
MEAS:CURR:NEUT:HARMONIC:PHASE? <N>    for harmonic N
MEAS:POW:DC?
MEAS:POW:AC:REAL?
MEAS:POW:AC:APPARENT?
MEAS:POW:AC:REACTIVE?
MEAS:POW:AC:PFACTOR?
MEAS:POW:AC:TOTAL?             3-phase total power
MEAS:FREQUENCY?

=== SYSTEM ===
SYSTEM:CONF NORM|IEC
SYSTEM:ERROR?

=== USER-DEFINED WAVEFORMS ===
TRACE:CATALOG?
TRACE <WAVEFORM> <N> {, <N>}
TRACE:DEFINE <WAVEFORM>[, <WAVEFORM>|1024]
TRACE:DELETE <WAVEFORM>

=== TRIGGERING ===
ABORT
INIT
INIT:SEQ1|SEQ2|SEQ3
INIT:NAME TRAN|ACQ
INIT:CONTINUOUS:SEQ[1] OFF|ON
INIT:CONTINUOUS:NAME TRAN OFF|ON
TRIG
TRIG:SYNC:SOURCE PHASE|IMMEDIATE
TRIG:SYNC:PHASE <P>
TRIG:ACQ
TRIG:ACQ:SOURCE BUS|EXT|TTLT
TRIG:SEQ1:DEFINE TRANSIENT
TRIG:SEQ2:DEFINE SYNCHRONIZE
TRIG:SEQ3:DEFINE ACQUIRE
"""


