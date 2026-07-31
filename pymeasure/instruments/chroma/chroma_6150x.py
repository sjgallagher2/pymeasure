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
from time import sleep

import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from pymeasure.instruments._strenum import StrEnum


class Chroma6150x(SCPIMixin, Instrument):
    """Represents the Chroma 6150x family of programmable AC sources.

    Do not use this class directly; use one of its subclasses.
    """

    _BOOLS = {True: 1, False: 0}
    FREQ_RANGE = [15, 1000]
    ROUT_RANGE = [0, 1]
    LOUT_RANGE = [200e-6, 1e-3]  # Henries
    WAVEFORMS = (
        ["SIN", "SQUA", "CSIN"]
        + [f"DST{x:02d}" for x in np.arange(1, 31)]
        + [f"USR{x:02d}" for x in np.arange(1, 7)]
    )

    def __init__(self, adapter, name="Chroma 6150x AC Power Source/Analyzer", **kwargs):
        super().__init__(adapter, name, **kwargs)

    voltage_setpoint_ac = Instrument.control(
        "VOLT:AC?",
        "VOLT:AC %f",
        """Control the AC RMS voltage amplitude setpoint in volts.

        Note that the max value dependends on the range, see control `output_range`.""",
        validator=strict_range,
        values=[0, 1],
        dynamic=True,
    )

    voltage_setpoint_dc = Instrument.control(
        "VOLT:DC?",
        "VOLT:DC %f",
        """Control the DC voltage amplitude setpoint in volts.

        Note that the max value dependends on the output range, see control `output_range`.""",
        validator=strict_range,
        values=[0, 1],
        dynamic=True,
    )

    clipped_sine_setpoint_pct = Instrument.control(
        "FUNC:CSIN?",
        "FUNC:CSIN %f",
        """Control clipped sine clipping point as a percent (0-100) of peak amplitude.""",
        validator=strict_range,
        values=[0.0, 100.0],
    )

    current_setpoint = Instrument.control(
        "CURRENT?",
        "CURRENT %f",
        """Control the AC RMS current limit setpoint in amperes.""",
        validator=strict_range,
        values=[0, 1],
        dynamic=True,
    )

    frequency_setpoint = Instrument.control(
        "FREQ?",
        "FREQ %f",
        """Control the frequency setpoint in hertz""",
        validator=strict_range,
        values=FREQ_RANGE,
    )

    voltage_dc = Instrument.measurement("FETCH:VOLT:DC?", """Measure DC voltage in volts.""")
    voltage_ac = Instrument.measurement("FETCH:VOLT:ACDC?", """Measure ACDC voltage in volts.""")
    current_dc = Instrument.measurement("FETCH:CURR:DC?", """Measure DC current in amperes.""")
    current_ac = Instrument.measurement("FETCH:CURR:AC?", """Measure AC RMS current in amperes.""")
    current_amplitude = Instrument.measurement(
        "FETCH:CURR:AMPL:MAX?", """Measure peak current amplitude in amperes."""
    )

    crest_factor = Instrument.measurement(
        "FETCH:CURR:CRESTFACTOR?", """Measure current crest factor."""
    )

    inrush = Instrument.measurement("FETCH:CURR:INRUSH?", """Measure the inrush current.""")
    power_real = Instrument.measurement("FETCH:POW:AC:REAL?", """Measure AC real power in watts.""")
    power_apparent = Instrument.measurement(
        "FETCH:POW:AC:APPARENT?", """Measure AC apparent power in VA."""
    )

    power_reactive = Instrument.measurement(
        "FETCH:POW:AC:REACTIVE?", """Measure AC reactive power in VAR."""
    )

    power_total = Instrument.measurement(
        "FETCH:POW:AC:TOTAL?", """Measure three-phase total AC power."""
    )

    frequency = Instrument.measurement("FETCH:FREQUENCY?", """Measure AC frequency in hertz.""")
    power_factor = Instrument.measurement(
        "FETCH:POW:AC:PFACTOR?", """Measure AC power factor in degrees."""
    )

    waveform_buffer = Instrument.control(
        "FUNC:SHAPE?",
        "FUNC:SHAPE %s",
        """Control the choice of waveform buffer. There are two buffers for the output of the AC
        source, so the user must specify the contents of waveform buffer A or B of the AC source.
        Can be 'A' or 'B'.""",
        validator=strict_discrete_set,
        values=["A", "B"],
        cast=str,
    )

    waveform_A = Instrument.control(
        "FUNC:SHAPE:A?",
        "FUNC:SHAPE:A %s",
        """Control the output function of buffer A of the ac source. Can be SIN, SQUA, CSIN,
        DST01,...,DST30, or USR01..06.""",
        validator=strict_discrete_set,
        values=WAVEFORMS,
        cast=str,
    )

    waveform_A_clip_mode = Instrument.control(
        "FUNC:SHAPE:A:MODE?",
        "FUNC:SHAPE:A:MODE %s",
        """Control the mode for the value of the clipped sine in waveform buffer A. Can be AMP
        or THD.""",
        validator=strict_discrete_set,
        values=["AMP", "THD"],
        cast=str,
    )

    waveform_A_clip_thd_pct = Instrument.control(
        "FUNC:SHAPE:A:THD?",
        "FUNC:SHAPE:A:THD %f",
        """Control the percentage of total harmonic distortion (THD) at which the clipped sine
        clips in waveform buffer A.""",
        validator=strict_range,
        values=[0, 100],
    )

    waveform_A_clip_peak_pct = Instrument.control(
        "FUNC:SHAPE:A:AMP?",
        "FUNC:SHAPE:A:AMP %f",
        """Control the percentage of peak at which the clipped sine clips in waveform buffer A.""",
        validator=strict_range,
        values=[0, 100],
    )

    waveform_B = Instrument.control(
        "FUNC:SHAPE:B?",
        "FUNC:SHAPE:B %s",
        """Control the output function of buffer B of the ac source. Can be SIN, SQUA, CSIN,
        DST01,...,DST30, or USR01..06.""",
        validator=strict_discrete_set,
        values=WAVEFORMS,
        cast=str,
    )

    waveform_B_clip_mode = Instrument.control(
        "FUNC:SHAPE:B:MODE?",
        "FUNC:SHAPE:B:MODE %s",
        """Control the mode for the value of the clipped sine in waveform buffer B. Can be AMP
        or THD.""",
        validator=strict_discrete_set,
        values=["AMP", "THD"],
        cast=str,
    )

    waveform_B_clip_thd_pct = Instrument.control(
        "FUNC:SHAPE:B:THD?",
        "FUNC:SHAPE:B:THD %f",
        """Control the percentage of total harmonic distortion (THD) at which the clipped sine
        clips in waveform buffer B.""",
        validator=strict_range,
        values=[0, 100],
    )

    waveform_B_clip_peak_pct = Instrument.control(
        "FUNC:SHAPE:B:AMP?",
        "FUNC:SHAPE:B:AMP %f",
        """Control the percentage of peak at which the clipped sine clips in waveform buffer B.""",
        validator=strict_range,
        values=[0, 100],
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
        cast=str,
    )

    output_mode = Instrument.control(
        "OUTPUT:MODE?",
        "OUTPUT_MODE %s",
        """Control the operation mode. Can be FIXED|LIST|PULSE|STEP|SYNTH|INTERHAR.""",
        validator=strict_discrete_set,
        values=["FIXED", "LIST", "PULSE", "STEP", "SYNTH", "INTERHAR"],
        cast=str,
    )

    output_range = Instrument.control(
        "VOLT:LIM:RANGE?",
        "VOLT:RANGE %s",
        """Control the output voltage range with three options of LOW (150V), HIGH (300V),
        or AUTO.""",
        validator=strict_discrete_set,
        values=["LOW", "HIGH", "AUTO"],
        cast=str,
    )

    # trigger_source = Instrument.control(
    #     "TRIG:SOUR?",
    #     "TRIG:SEQ1:SOUR %s",
    #     """Control the trigger source for first sequence. Can be BUS|EXTernal|IMMediate.

    #     When set to BUS, the trigger will activate after receiving a *TRG command over GPIB.
    #     When set to EXTernal, the AC source backplane BNC trigger input is used as the trigger.
    #     When set to IMMediate, the trigger is generated as soon as the trigger system is initiated.
    #     """,
    #     validator=strict_discrete_set,
    #     values=["BUS", "EXT", "EXTERNAL", "IMM", "IMMEDIATE"],
    #     cast=str,
    # )

    # trigger_sync_source = Instrument.control(
    #     "TRIG:SYNC:SOUR?",
    #     "TRIG:SYNC:SOUR %s",
    #     """Control the trigger system synchronization source.
    #     The trigger system can delay the trigger event until a certain synchronization event
    #     occurs. In particular, it can delay until the waveform phase reaches a particular value.

    #     Values can be IMMediate|PHASe.
    #     """,
    #     validator=strict_discrete_set,
    #     values=["IMM", "IMMEDIATE", "PHAS", "PHASE"],
    #     cast=str,
    # )

    # trigger_sync_phase = Instrument.control(
    #     "TRIG:SYNC:PHASE?",
    #     "TRIG:SYNC:PHASE %f",
    #     """Control the trigger synchronization phase value.

    #     When the trigger is phase synchronized, it waits until the waveform reaches this phase
    #     before the triggered event actually occurs.
    #     """,
    #     validator=strict_range,
    #     values=[0, 360],
    # )

    # voltage_trigger_level = Instrument.control(
    #     "VOLT:TRIG?",
    #     "VOLT:TRIG %f",
    #     """Control the AC RMS amplitude of the output waveform when triggered.""",
    #     validator=strict_range,
    #     values=[0, 1],
    #     dynamic=True,
    # )

    # voltage_trigger_mode = Instrument.control(
    #     "VOLT:MODE?",
    #     "VOLT:MODE %s",
    #     """Control the voltage trigger mode""",
    #     validator=strict_discrete_set,
    #     values=["FIX", "FIXED", "STEP", "PULS", "PULSE", "LIST"],
    #     cast=str,
    # )

    # pulse_count = Instrument.control(
    #     "PULSE:COUNT?",
    #     "PULSE:COUNT %f",
    #     """Control the number of pulses when trigger mode is set to PULSE.""",
    #     validator=strict_range,
    #     values=[1, 9.9e37],
    # )

    # pulse_period = Instrument.control(
    #     "PULSE:PER?",
    #     "PULSE:PER %f",
    #     """Control pulse period in seconds when trigger mode is set to PULSE.""",
    #     validator=strict_range,
    #     values=[0, 4.30133e5],
    # )

    # pulse_duty_cycle_pct = Instrument.control(
    #     "PULSE:DCYCLE?",
    #     "PULSE:DCYCLE %f",
    #     """Control pulse duty cycle as a percentage (0-100) when trigger mode is set to PULSE.""",
    #     validator=strict_range,
    #     values=[0, 100],
    # )

    # pulse_width = Instrument.control(
    #     "PULSE:WIDTH?",
    #     "PULSE:WIDTH %f",
    #     """Control the width in seconds of a transient output pulse when trigger mode is set to
    #     PULSE.""",
    #     validator=strict_range,
    #     values=[0, 4.30133e5],
    # )

    # voltage_sense_source = Instrument.control(
    #     "VOLTAGE:SENSE:SOURCE?", "VOLTAGE:SENSE:SOURCE %s",
    #     """Control the source from which the output voltage is sensed. Can be INTernal or
    #     EXTernal.""",
    #     validator=strict_discrete_set,
    #     values=['EXT', 'EXTERNAL', 'INT', 'INTERNAL'],
    #     cast=str,
    # )

    # def arm_immediate_trigger(self):
    #     """Arm the trigger system (SEQ1). Before a trigger can have effect, the trigger subsystem
    #     must be armed, or 'initialized'. This method arms the trigger for a single event."""
    #     self.write("INIT:SEQ1")

    # def arm_continuous_trigger(self, run=True):
    #     """Arm the trigger system (SEQ1). Before a trigger can have effect, the trigger subsystem
    #     must be armed, or 'initialized'. This method arms or disarms the trigger for a continuous
    #     run.

    #     :param run: if True, enable continuous triggering; if False, stop continuous triggering."""
    #     if run:
    #         self.write("INIT:CONT:SEQ1 ON")
    #     else:
    #         self.write("INIT:CONT:SEQ1 OFF")

    # def send_GPIB_trigger(self):
    #     """Send a GPIB trigger signal. The trigger source must be set to BUS for this to have
    #     any effect. This function forces the trigger source to be BUS before sending."""
    #     self.trigger_source = "BUS"
    #     self.write("*TRG")

    def output_enable(self, enable: bool = True):
        """Enable or disable the AC source."""
        self.output_state = enable

    # def output_enable_at_phase(self, trig_phase: float):
    #     """Enable the output at a given phase.

    #     This method uses the existing voltage setpoint to set a voltage step level on trigger.
    #     The voltage setpoint is set to 0V, the output is enabled, and the trigger system is used
    #     to step the voltage to the prior setpoint when we send *TRG and the waveform phase
    #     reaches `phase`. A GPIB trigger is sent.

    #     After this method, the voltage setpoint will be the same as before, the trigger SYNC
    #     source will be PHASE, and the voltage trigger mode will be STEP.

    #     Example:
    #     ```python
    #     # Reset and configure the output
    #     acsource.reset()
    #     acsource.voltage_setpoint = 50
    #     acsource.frequency_setpoint = 60
    #     acsource.output_enable_at_phase(90)  # start waveform at 90 degrees
    #     ```
    #     """
    #     vset = self.voltage_setpoint
    #     self.voltage_setpoint = 0
    #     self.output_enable(True)
    #     self.voltage_trigger_mode = "STEP"
    #     self.voltage_trigger_level = vset
    #     self.trigger_sync_source = "PHASE"
    #     self.trigger_sync_phase = trig_phase
    #     sleep(1)  # MUST dwell here for trigger to work.
    #     self.arm_immediate_trigger()
    #     self.send_GPIB_trigger()

    # def output_pulse(self, Vdefault, Vpulse, pulse_period, N_pulses=1, pulse_ON_time=-1):
    #     """Trigger one or more voltage pulses.

    #     :param N_pulses: number of pulses to output
    #     :param Vdefault: default voltage, or pulse OFF state voltage
    #     :param Vpulse: pulse ON state voltage
    #     :param pulse_period: Time duration of one full pulse (an ON and an OFF duration)
    #     :param pulse_ON_time: Time duration for pulse ON state, or -1 for a single pulse.
    #     """
    #     if pulse_ON_time == -1:
    #         pulse_ON_time = pulse_period
    #     self.voltage_setpoint = Vdefault
    #     self.output_enable(True)
    #     sleep(1)  # Dwell before trigger setup
    #     self.voltage_trigger_mode = "PULSE"
    #     self.voltage_trigger_level = Vpulse
    #     self.pulse_count = N_pulses
    #     self.pulse_period = pulse_period
    #     self.pulse_width = pulse_ON_time
    #     self.arm_immediate_trigger()
    #     self.send_GPIB_trigger()

    # def output_pulse_at_phase(
    #     self,
    #     Vdefault,
    #     Vpulse,
    #     pulse_period,
    #     trig_phase=0.0,
    #     N_pulses=1,
    #     pulse_ON_time=-1,
    #     trigger_source="GPIB",
    # ):
    #     """Trigger one or more voltage pulses, waiting for a particular phase angle before
    #     triggering.

    #     If trigger source is GPIB, trigger is sent immediately. if trigger source is
    #     external, this function returns with the system armed for an external trigger.

    #     :param Vdefault: default voltage, or pulse OFF state voltage
    #     :param Vpulse: pulse ON state voltage
    #     :param pulse_period: Time duration of one full pulse (an ON and an OFF duration)
    #     :param trig_phase: waveform phase angle at which to trigger
    #     :param N_pulses: number of pulses to output
    #     :param pulse_ON_time: Time duration for pulse ON state, or -1 for a single pulse.
    #     :param trigger_source: Trigger source, can be GPIB|BUS|EXTernal|IMMediate.
    #     """
    #     if pulse_ON_time == -1:
    #         pulse_ON_time = pulse_period
    #     self.voltage_setpoint = Vdefault
    #     self.output_enable(True)
    #     sleep(1)  # Dwell before trigger setup
    #     self.voltage_trigger_mode = "PULSE"
    #     self.voltage_trigger_level = Vpulse
    #     self.pulse_count = N_pulses
    #     self.pulse_period = pulse_period
    #     self.pulse_width = pulse_ON_time
    #     self.trigger_sync_source = "PHASE"
    #     self.trigger_sync_phase = trig_phase
    #     self.arm_immediate_trigger()
    #     if trigger_source == "GPIB" or trigger_source == "BUS":
    #         self.send_GPIB_trigger()
    #     else:
    #         self.trigger_source = trigger_source

    # WAVEFORMS #
    # user_wfm_catalog = Instrument.measurement(
    #     "TRACE:CATALOG?",
    #     """Get the user waveform catalog.""",
    #     get_process_list=lambda names: [str(name).replace('"', "") for name in names],
    # )

    # def get_user_wfm_data(self, name: str):
    #     """Get the data points for a particular user waveform.

    #     :param name: internal name of user waveform.
    #     :return: numpy array of y-data points with dtype float.
    #     """
    #     data_str = self.ask(f"TRACE:DATA? {name.upper()}")
    #     data = np.array(data_str.strip().split(","), dtype=float)
    #     return data

    # def get_user_waveform_catalog(self):
    #     """Query the list of user waveforms.."""
    #     print("Retrieving user waveform catalog. This might take a minute...")
    #     names = self.user_wfm_catalog
    #     cat = {}
    #     for name in names:
    #         if name not in ["SINUSOID", "SQUARE", "CSINUSOID"]:
    #             namedata = self.get_user_wfm_data(name)
    #             cat[name] = namedata
    #     return cat

    def add_user_waveform(self, data1024, user_slot=1, delete_existing=False):
        """Add user waveform"""
        pass


class Chroma61501(Chroma6150x):
    VRMS_MAX = 300
    IRMS_MAX = 4
    VPEAK_MAX = 424
    IPEAK_MAX = 24

    def __init__(self, adapter, name="Chroma 61501 Programmable AC Power Source", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.voltage_setpoint_ac_values = [0, self.VRMS_MAX]
        self.voltage_setpoint_dc_values = [0, self.VPEAK_MAX]
        self.current_setpoint_ac_values = [0, self.IRMS_MAX]
        self.current_setpoint_dc_values = [0, self.IPEAK_MAX]
        self.voltage_trigger_level_values = [0, self.VRMS_MAX]


class Chroma61502(Chroma6150x):
    VRMS_MAX = 300
    IRMS_MAX = 8
    VPEAK_MAX = 424
    IPEAK_MAX = 48

    def __init__(self, adapter, name="Chroma 61502 Programmable AC Source", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.voltage_setpoint_ac_values = [0, self.VRMS_MAX]
        self.voltage_setpoint_dc_values = [0, self.VPEAK_MAX]
        self.current_setpoint_ac_values = [0, self.IRMS_MAX]
        self.current_setpoint_dc_values = [0, self.IPEAK_MAX]
        self.voltage_trigger_level_values = [0, self.VRMS_MAX]


class Chroma61503(Chroma6150x):
    VRMS_MAX = 300
    IRMS_MAX = 12
    VPEAK_MAX = 424
    IPEAK_MAX = 72

    def __init__(self, adapter, name="Chroma 61503 Programmable AC Source", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.voltage_setpoint_ac_values = [0, self.VRMS_MAX]
        self.voltage_setpoint_dc_values = [0, self.VPEAK_MAX]
        self.current_setpoint_ac_values = [0, self.IRMS_MAX]
        self.current_setpoint_dc_values = [0, self.IPEAK_MAX]
        self.voltage_trigger_level_values = [0, self.VRMS_MAX]


class Chroma61504(Chroma6150x):
    VRMS_MAX = 300
    IRMS_MAX = 16
    VPEAK_MAX = 424
    IPEAK_MAX = 96

    def __init__(self, adapter, name="Chroma 61504 Programmable AC Source", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.voltage_setpoint_ac_values = [0, self.VRMS_MAX]
        self.voltage_setpoint_dc_values = [0, self.VPEAK_MAX]
        self.current_setpoint_ac_values = [0, self.IRMS_MAX]
        self.current_setpoint_dc_values = [0, self.IPEAK_MAX]
        self.voltage_trigger_level_values = [0, self.VRMS_MAX]


class Chroma61505(Chroma6150x):
    VRMS_MAX = 300
    IRMS_MAX = 32
    IPEAK_MAX = 192

    def __init__(self, adapter, name="Chroma 61505 Programmable AC Source", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.voltage_setpoint_ac_values = [0, self.VRMS_MAX]
        self.voltage_setpoint_dc_values = [0, self.VPEAK_MAX]
        self.current_setpoint_ac_values = [0, self.IRMS_MAX]
        self.current_setpoint_dc_values = [0, self.IPEAK_MAX]
        self.voltage_trigger_level_values = [0, self.VRMS_MAX]
