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
from pymeasure.instruments._strenum import StrEnum


class Functions(StrEnum):
    SINE = "SIN"
    SQUARE = "SQU"
    CLIPPED_SINE = "CSIN"  # Clipped sinewave output. Both positive and negative peak amplitudes
    # are clipped at a value determined by the FUNC:CSIN command.


class Modes(StrEnum):
    FIXED = "FIX"  # unaffected by a triggered output transient.
    STEP = "STEP"  # programmed to the value set by X:TRIG when a triggered transient occurs.
    PULSE = "PULS"  # changed to the value set by X:TRIG for a duration determined by the pulse
    # commands.
    LIST = "LIST"  # controlled by the waveform shape list when a triggered transient occurs.


class Keysight681xB(SCPIMixin, Instrument):
    """Represents the Keysight 6811B, 6812B, and 6813B AC Power Source/Analyzers."""

    _BOOLS = {True: 1, False: 0}

    def __init__(self, adapter, name="Keysight 681xB AC Power Source/Analyzer", **kwargs):
        super().__init__(adapter, name, **kwargs)

    voltage_setpoint = Instrument.control(
        "VOLT?",
        "VOLT %f",
        """Control the AC RMS voltage amplitude setpoint in volts.""",
        validator=truncated_range,
        values=[0, 300],
    )
    clipped_sine_setpoint_pct = Instrument.control(
        "FUNC:CSIN?",
        "FUNC:CSIN %f",
        """Control clipped sine clipping point as a percent (0-100) of peak amplitude.""",
        validator=truncated_range,
        values=[0.0, 100.0],
    )
    current_setpoint = Instrument.control(
        "CURRENT?",
        "CURRENT %f",
        """Control the AC RMS current limit setpoint in amperes.""",
        validator=truncated_range,
        values=[0, 13.0],  # default limit, for 6813B
    )
    frequency_setpoint = Instrument.control(
        "FREQ?",
        "FREQ %f",
        """Control the frequency setpoint in hertz""",
        validator=truncated_range,
        values=[45, 1000],
    )
    voltage_dc = Instrument.measurement("MEAS:VOLT:DC?", """Measure DC voltage in volts.""")
    voltage_ac = Instrument.measurement("MEAS:VOLT:AC?", """Measure AC RMS voltage in volts.""")
    voltage_acdc = Instrument.measurement("MEAS:VOLT:ACDC?", """Measure ACDC voltage in volts.""")
    current_dc = Instrument.measurement("MEAS:CURR:DC?", """Measure DC current in amperes.""")
    current_ac = Instrument.measurement("MEAS:CURR:AC?", """Measure AC RMS current in amperes.""")
    current_acdc = Instrument.measurement("MEAS:CURR:ACDC?", """Measure ACDC current in amperes.""")
    current_amplitude = Instrument.measurement(
        "MEAS:CURR:AMPL:MAX?", """Measure peak current amplitude in amperes."""
    )
    crest_factor = Instrument.measurement(
        "MEAS:CURR:CRESTFACTOR?", """Measure current crest factor."""
    )
    power_dc = Instrument.measurement("MEAS:POW:DC?", """Measure DC power.""")
    power_real = Instrument.measurement("MEAS:POW:AC:REAL?", """Measure AC real power in watts.""")
    power_apparent = Instrument.measurement(
        "MEAS:POW:AC:APPARENT?", """Measure AC apparent power in VA."""
    )
    power_reactive = Instrument.measurement(
        "MEAS:POW:AC:REACTIVE?", """Measure AC reactive power in VAR."""
    )
    power_total = Instrument.measurement(
        "MEAS:POW:AC:TOTAL?", """Measure three-phase total AC power."""
    )
    frequency = Instrument.measurement("MEAS:FREQUENCY?", """Measure AC frequency in hertz.""")
    power_factor = Instrument.measurement(
        "MEAS:POW:AC:PFACTOR?", """Measure AC power factor in degrees."""
    )
    output_function = Instrument.control(
        "FUNC?",
        "FUNC %s",
        """Control the output function of the ac source. Can be SIN, SQU, CSIN, or a user
        waveform.""",
    )
    output_state = Instrument.control(
        "OUTPUT:STATE?",
        "OUTPUT:STATE %s",
        """Control the enable/disable state of the AC source (bool).

        See also :py:method:`output_enable()`.
        """,
        validator=strict_discrete_set,
        values=_BOOLS,
        map_values=True,
    )

    def output_enable(self, enable: bool = True):
        """Enable or disable the AC source."""
        self.output_state = enable

    user_wfm_catalog = Instrument.measurement(
        "TRACE:CATALOG?",
        """Get the user waveform catalog.""",
        get_process_list=lambda names: [name.replace('"', "") for name in names],
    )

    def get_user_wfm_data(self, name: str):
        """Get the data points for a particular user waveform.

        :param name: internal name of user waveform.
        :return: numpy array of y-data points with dtype float.
        """
        data_str = self.ask(f"TRACE:DATA? {name.upper()}")
        data = np.array(data_str.strip().split(","), dtype=float)
        return data

    def get_user_waveform_catalog(self):
        """Query the list of user waveforms.."""
        print("Retrieving user waveform catalog. This might take a minute...")
        names = self.user_wfm_catalog
        cat = {}
        for name in names:
            if name not in ["SINUSOID", "SQUARE", "CSINUSOID"]:
                namedata = self.get_user_wfm_data(name)
                cat[name] = namedata
        return cat

    def delete_user_waveform(self, name: str):
        """Delete a user waveform by name."""
        self.write(f"TRACE:DEL {name}")

    def define_user_waveform_name(self, name: str):
        """Define a user waveform name without data."""
        self.write(f"TRACE:DEF {name}")

    def add_user_waveform(self, name, data1024, delete_existing=False):
        """Add a waveform called `name` with 1024 float data points in [0.0, 1.0] to the user
        waveform catalog.

        From the programming guide:
        "data points define the relative amplitudes of exactly one cycle of the waveform. The first
        data point defines the amplitude that will be output at 0 degrees phase reference."

        "Data points can be in any arbitrary units. The ac source scales the data to an
        internal format that removes the dc component and ensures that the correct ac rms
        voltage is output when the waveform is selected. When queried, trace data is returned
        as normalized values in the range of 1. Waveform data is stored in nonvolatile memory
        and is retained when input power is removed. Up to 12 user defined waveforms may be
        created and stored."

        :param name: str, name of waveform, will be converted to ALL CAPS.
        :param data1024: numpy array of length 1024, dtype float, all values in [0.0, 1.0].
                         Points will be rounded to 5 digits of precision.
        :param delete_existing: if True, any waveform with the same name will be deleted before
                                adding the new data. If False, raises an exception if name exists.
        """
        if len(data1024) != 1024:
            raise ValueError(
                f"Length error, received array of length {len(data1024)}; length must be 1024."
            )
        data1024f = data1024.astype(float)

        # Preprocess name, delete existing trace if present
        name = name.upper()
        if name in self.user_wfm_catalog:
            if delete_existing:
                print(f"NOTE: Deleting existing waveform '{name}'")
                self.delete_user_waveform(name)
            else:
                raise ValueError(
                    "Waveform with this name already exists. To override, "
                    "use `delete_existing=True`."
                )

        # Convert to 5 digits of precision
        wave = [f"{x:.5f}" for x in data1024f]

        # Add name if needed, then write data
        self.define_user_waveform_name(name)
        self.write(f"TRACE:DATA {name}, " + ", ".join(wave))


