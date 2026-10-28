"""Support for Chroma 6150x programmable AC sources.

The command set is based on the Chroma 61505 User's Manual, version 1.8.
"""
import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class Chroma6150x(SCPIMixin, Instrument):
    """Base class for the Chroma 6150x programmable AC-source family.

    Use a model-specific subclass rather than this class directly.
    """

    FREQ_RANGE = (15.0, 1000.0)
    ROUT_RANGE = (0.0, 1.0)
    LOUT_RANGE = (0.0, 1e-3)
    PHASE_RANGE = (0.0, 359.9)
    WAVEFORMS = (
        ["SINE", "SQUA", "CSIN"]
        + [f"DST{x:02d}" for x in range(1, 31)]
        + [f"USR{x:02d}" for x in range(1, 7)]
    )

    # ON|OFF
    output_enabled = Instrument.control(
        "OUTP?", "OUTP %d",
        "Control whether source output is enabled.",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    # ON|OFF
    output_relay_enabled = Instrument.control(
        "OUTP:REL?", "OUTP:REL %d",
        "Control whether the output relay is closed.",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    output_mode = Instrument.control(
        "OUTP:MODE?", "OUTP:MODE %s",
        "Control the operating mode.",
        validator=strict_discrete_set,
        values=("FIXED", "LIST", "PULSE", "STEP", "SYNTH", "INTERHAR"),
    )

    output_coupling = Instrument.control(
        "OUTP:COUP?", "OUTP:COUP %s",
        "Control output coupling.",
        validator=strict_discrete_set,
        values=("AC", "DC", "ACDC"),
    )

    frequency_setpoint = Instrument.control(
        "FREQ?", "FREQ %g",
        "Control output frequency in hertz.",
        validator=strict_range,
        values=FREQ_RANGE,
    )

    voltage_setpoint_ac = Instrument.control(
        "VOLT:AC?", "VOLT:AC %g",
        "Control AC RMS output voltage in volts.",
        validator=strict_range,
        values=(0.0, 300.0),
    )

    voltage_setpoint_dc = Instrument.control(
        "VOLT:DC?", "VOLT:DC %g",
        "Control DC output voltage in volts.",
        validator=strict_range,
        values=(-424.2, 424.2),
    )

    voltage_range = Instrument.control(
        "VOLT:RANG?", "VOLT:RANG %s",
        "Control output voltage range.",
        validator=strict_discrete_set,
        values=("LOW", "HIGH", "AUTO"),
    )

    voltage_limit_ac = Instrument.control(
        "VOLT:LIM:AC?", "VOLT:LIM:AC %g",
        "Control the software AC voltage limit in volts.",
        validator=strict_range,
        values=(0.0, 300.0),
    )

    voltage_limit_dc_positive = Instrument.control(
        "VOLT:LIM:DC:PLUS?", "VOLT:LIM:DC:PLUS %g",
        "Control the positive software DC voltage limit in volts.",
        validator=strict_range,
        values=(0.0, 424.2),
    )

    voltage_limit_dc_negative = Instrument.control(
        "VOLT:LIM:DC:MIN?", "VOLT:LIM:DC:MIN %g",
        "Control the negative software DC voltage limit in volts.",
        validator=strict_range,
        values=(-424.2, 0.0),
    )

    current_limit = Instrument.control(
        "CURR:LIM?", "CURR:LIM %g",
        "Control the RMS current limit in amperes.",
        validator=strict_range,
        values=(0.0, 32.0),
    )

    current_limit_delay = Instrument.control(
        "CURR:DEL?", "CURR:DEL %g",
        "Control over-current protection delay in half-seconds.",
        validator=strict_range,
        values=(0.0, 5.0),
    )

    inrush_start = Instrument.control(
        "CURR:INR:STAR?", "CURR:INR:STAR %g",
        "Control inrush measurement start time in milliseconds.",
        validator=strict_range,
        values=(0.0, 999.9),
    )

    inrush_interval = Instrument.control(
        "CURR:INR:INT?", "CURR:INR:INT %g",
        "Control inrush measurement interval in milliseconds.",
        validator=strict_range,
        values=(0.0, 999.9),
    )

    phase_on = Instrument.control(
        "PHAS:ON?", "PHAS:ON %g",
        "Control output turn-on phase in degrees.",
        validator=strict_range,
        values=PHASE_RANGE,
    )

    phase_off = Instrument.control(
        "PHAS:OFF?", "PHAS:OFF %g",
        "Control output turn-off phase in degrees; 360 means immediate.",
        validator=strict_range,
        values=(0.0, 360.0),
    )

    # ON|OFF
    impedance_enabled = Instrument.control(
        "OUTP:IMP:STAT?", "OUTP:IMP:STAT %d",
        "Control programmable output impedance.",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    impedance_resistance = Instrument.control(
        "OUTP:IMP:RES?", "OUTP:IMP:RES %g",
        "Control output resistance in ohms.",
        validator=strict_range,
        values=ROUT_RANGE,
    )

    # The instrument command uses mH even though this Python API uses henries.
    impedance_inductance = Instrument.control(
        "OUTP:IMP:IND?", "OUTP:IMP:IND %g",
        "Control output inductance in henries.",
        validator=strict_range,
        values=LOUT_RANGE,
        get_process=lambda value: float(value) / 1000.0,
        set_process=lambda value: value * 1000.0,
    )

    slew_voltage_ac = Instrument.control(
        "OUTP:SLEW:VOLT:AC?", "OUTP:SLEW:VOLT:AC %g",
        "Control AC-voltage slew rate in V/ms; zero selects fastest.",
        validator=strict_range,
        values=(0.0, 1200.0),
    )

    slew_voltage_dc = Instrument.control(
        "OUTP:SLEW:VOLT:DC?", "OUTP:SLEW:VOLT:DC %g",
        "Control DC-voltage slew rate in V/ms; zero selects fastest.",
        validator=strict_range,
        values=(0.0, 1000.0),
    )

    slew_frequency = Instrument.control(
        "OUTP:SLEW:FREQ?", "OUTP:SLEW:FREQ %g",
        "Control frequency slew rate in Hz/ms; zero selects fastest.",
        validator=strict_range,
        values=(0.0, 1600.0),
    )

    waveform_buffer = Instrument.control(
        "FUNC:SHAP?", "FUNC:SHAP %s",
        "Control the selected waveform buffer.",
        validator=strict_discrete_set,
        values=("A", "B"),
        cast=str,
    )

    waveform_a = Instrument.control(
        "FUNC:SHAP:A?", "FUNC:SHAP:A %s",
        "Control waveform buffer A.",
        validator=strict_discrete_set,
        values=WAVEFORMS,
        cast=str,
    )

    waveform_b = Instrument.control(
        "FUNC:SHAP:B?", "FUNC:SHAP:B %s",
        "Control waveform buffer B.",
        validator=strict_discrete_set,
        values=WAVEFORMS,
        cast=str,
    )

    # OFF|ON, returns OFF|RUNNING
    # To change parameters, set TRIG OFF then OUTP:MODE FIXED, then set OUTP:MODE LIST again
    # and re-set TRIG ON
    trigger_state = Instrument.control(
        "TRIG:STATE?", "TRIG %s",
        "Control transient execution state after setting output mode to LIST.",
        validator=strict_discrete_set,
        values=("OFF", "ON", "PAUSE", "CONTINUE"),
        cast=str,
    )

    list_count = Instrument.control(
        "LIST:COUN?", "LIST:COUN %d",
        "Control LIST repetitions; zero means infinite.",
        validator=strict_range,
        values=(0, 65535),
    )

    list_base = Instrument.control(
        "LIST:BASE?", "LIST:BASE %s",
        "Control LIST dwell base.",
        validator=strict_discrete_set,
        values=("TIME", "CYCLE"),
        cast=str,
    )

    pulse_voltage_ac = Instrument.control(
        "PULS:VOLT:AC?", "PULS:VOLT:AC %g",
        "Control AC voltage during PULSE duty cycle, in volts.",
        validator=strict_range,
        values=(0.0, 300.0),
    )

    pulse_voltage_dc = Instrument.control(
        "PULS:VOLT:DC?", "PULS:VOLT:DC %g",
        "Control DC voltage during PULSE duty cycle, in volts.",
        validator=strict_range,
        values=(-424.2, 424.2),
    )

    pulse_frequency = Instrument.control(
        "PULS:FREQ?", "PULS:FREQ %g",
        "Control frequency during PULSE duty cycle, in hertz.",
        validator=strict_range,
        values=FREQ_RANGE,
    )

    pulse_shape = Instrument.control(
        "PULS:SHAP?", "PULS:SHAP %s",
        "Control waveform buffer during PULSE duty cycle.",
        validator=strict_discrete_set,
        values=("A", "B"),
    )

    pulse_phase = Instrument.control(
        "PULS:SPH?", "PULS:SPH %g",
        "Control starting phase for PULSE duty cycle, in degrees.",
        validator=strict_range,
        values=PHASE_RANGE,
    )

    pulse_count = Instrument.control(
        "PULS:COUN?", "PULS:COUN %d",
        "Control pulse count; zero means infinite.",
        validator=strict_range,
        values=(0, 65535),
    )

    pulse_duty_cycle = Instrument.control(
        "PULS:DCYC?", "PULS:DCYC %g",
        "Control PULSE duty cycle in percent.",
        validator=strict_range,
        values=(0.0, 100.0),
    )

    pulse_period = Instrument.control(
        "PULS:PER?", "PULS:PER %g",
        "Control PULSE period in milliseconds.",
        validator=strict_range,
        values=(0.0, 99999999.9),
    )

    step_voltage_ac = Instrument.control(
        "STEP:VOLT:AC?", "STEP:VOLT:AC %g",
        "Control STEP initial AC voltage in volts.",
        validator=strict_range,
        values=(0.0, 300.0),
    )

    step_voltage_dc = Instrument.control(
        "STEP:VOLT:DC?", "STEP:VOLT:DC %g",
        "Control STEP initial DC voltage in volts.",
        validator=strict_range,
        values=(-424.2, 424.2),
    )

    step_frequency = Instrument.control(
        "STEP:FREQ?", "STEP:FREQ %g",
        "Control STEP initial frequency in hertz.",
        validator=strict_range,
        values=FREQ_RANGE,
    )

    step_dwell = Instrument.control(
        "STEP:DWEL?", "STEP:DWEL %g",
        "Control STEP dwell time in milliseconds.",
        validator=strict_range,
        values=(0.0, 99999999.9),
    )

    step_count = Instrument.control(
        "STEP:COUN?", "STEP:COUN %d",
        "Control STEP count.",
        validator=strict_range,
        values=(0, 65535),
    )

    # NOTE: Missing DVOL:AC, DVOL:DC, DFR, SHAP

    interharmonic_start_frequency = Instrument.control(
        "INT:FREQ:STAR?", "INT:FREQ:STAR %g",
        "Control interharmonic sweep start frequency in hertz.",
        validator=strict_range,
        values=(0.01, 2400.0),
    )

    interharmonic_end_frequency = Instrument.control(
        "INT:FREQ:END?", "INT:FREQ:END %g",
        "Control interharmonic sweep end frequency in hertz.",
        validator=strict_range,
        values=(0.01, 2400.0),
    )

    interharmonic_level = Instrument.control(
        "INT:LEV?", "INT:LEV %g",
        "Control interharmonic level in percent.",
        validator=strict_range,
        values=(0.0, 30.0),
    )

    interharmonic_dwell = Instrument.control(
        "INT:DWEL?", "INT:DWEL %g",
        "Control interharmonic sweep time in seconds.",
        validator=strict_range,
        values=(0.01, 9999.99),
    )

    def __init__(self, adapter, name="Chroma 6150x AC Power Source/Analyzer", **kwargs):
        super().__init__(adapter, name, **kwargs)

    @property
    def voltage_ac_measured(self):
        """Return newly acquired RMS output voltage in volts."""
        return float(self.ask("MEAS:VOLT:ACDC?"))

    @property
    def voltage_dc_measured(self):
        """Return newly acquired DC output voltage in volts."""
        return float(self.ask("MEAS:VOLT:DC?"))

    @property
    def current_ac_measured(self):
        """Return newly acquired RMS output current in amperes."""
        return float(self.ask("MEAS:CURR:AC?"))

    @property
    def current_dc_measured(self):
        """Return newly acquired DC output current in amperes."""
        return float(self.ask("MEAS:CURR:DC?"))

    @property
    def current_peak_measured(self):
        """Return newly acquired absolute peak output current in amperes."""
        return float(self.ask("MEAS:CURR:AMPL:MAX?"))

    @property
    def current_inrush_measured(self):
        """Return newly acquired inrush current in amperes."""
        return float(self.ask("MEAS:CURR:INR?"))

    @property
    def power_measured(self):
        """Return newly acquired real power in watts."""
        return float(self.ask("MEAS:POW:AC?"))

    @property
    def apparent_power_measured(self):
        """Return newly acquired apparent power in volt-amperes."""
        return float(self.ask("MEAS:POW:AC:APP?"))

    @property
    def reactive_power_measured(self):
        """Return newly acquired reactive power in vars."""
        return float(self.ask("MEAS:POW:AC:REAC?"))

    @property
    def power_factor_measured(self):
        """Return newly acquired power factor."""
        return float(self.ask("MEAS:POW:AC:PFAC?"))

    @property
    def crest_factor_measured(self):
        """Return newly acquired current crest factor."""
        return float(self.ask("MEAS:CURR:CRES?"))

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

    def clear_protection(self):
        """Clear a latched protection condition after its cause is removed."""
        self.write("OUTP:PROT:CLE")

    def set_list(self, dwell, shape, voltage_ac_start, voltage_ac_end,
                 voltage_dc_start, voltage_dc_end, frequency_start,
                 frequency_end, phase):
        """Program all LIST vectors.

        Every argument is an iterable and all vectors must have equal length.
        """
        vectors = [dwell, shape, voltage_ac_start, voltage_ac_end,
                   voltage_dc_start, voltage_dc_end, frequency_start,
                   frequency_end, phase]
        vectors = [list(v) for v in vectors]
        lengths = {len(v) for v in vectors}
        if len(lengths) != 1 or not vectors[0]:
            raise ValueError("LIST vectors must be non-empty and equal in length")
        if len(vectors[0]) > 100:
            raise ValueError("The instrument supports at most 100 LIST points")
        if any(value not in ("A", "B") for value in vectors[1]):
            raise ValueError("LIST shape entries must be 'A' or 'B'")
        commands = (
            ("LIST:DWEL", vectors[0]), ("LIST:SHAP", vectors[1]),
            ("LIST:VOLT:AC:STAR", vectors[2]), ("LIST:VOLT:AC:END", vectors[3]),
            ("LIST:VOLT:DC:STAR", vectors[4]), ("LIST:VOLT:DC:END", vectors[5]),
            ("LIST:FREQ:STAR", vectors[6]), ("LIST:FREQ:END", vectors[7]),
            ("LIST:DEGR", vectors[8]),
        )
        for command, values in commands:
            self.write(f"{command} " + ",".join(str(value) for value in values))

    def start_transient(self, mode):
        """Select a transient mode and trigger it."""
        self.output_mode = mode
        self.trigger_state = "ON"

    def stop_transient(self):
        """Stop transient execution and return to fixed mode."""
        self.trigger_state = "OFF"
        self.output_mode = "FIXED"

    def define_user_waveform(self, number, waveform):
        """Download one period into a user-defined waveform slot.

        Adapting from the manual:
            A user waveform needs 1024 data points to construct a period. Users have
            to normalize the data to either a maximum value of 32767 or a minimum
            value of -32767. The RMS value of the user waveform can be set from 0 to
            32767.

        :param number: User waveform number, 1 through 6.
        :param waveform: Iterable containing exactly 1024 samples.
            Arbitrary input scaling is accepted; samples are normalized
            to the instrument's signed 32767 full-scale range.
        """
        if number not in range(1, 7):
            raise ValueError("User waveform number must be 1 through 6")

        waveform = np.asarray(waveform, dtype=float)

        if waveform.size != 1024:
            raise ValueError("User waveform must contain exactly 1024 samples")

        peak = np.max(np.abs(waveform))
        if peak == 0:
            raise ValueError("User waveform cannot be all zero")

        samples = np.rint(32767 * waveform / peak).astype(int)
        rms = int(round(np.sqrt(np.mean(samples.astype(float) ** 2))))

        data = ",".join(map(str, samples))

        self.write(f"TRAC US{number},{data}")
        self.write(f"TRAC:RMS US{number},{rms}")


class Chroma61501(Chroma6150x):
    VRMS_MAX, IRMS_MAX, VPEAK_MAX, IPEAK_MAX = 300.0, 4.0, 424.2, 24.0

    def __init__(self, adapter, name="Chroma 61501 Programmable AC Source", **kwargs):
        super().__init__(adapter, name, **kwargs)


class Chroma61502(Chroma6150x):
    VRMS_MAX, IRMS_MAX, VPEAK_MAX, IPEAK_MAX = 300.0, 8.0, 424.2, 48.0

    def __init__(self, adapter, name="Chroma 61502 Programmable AC Source", **kwargs):
        super().__init__(adapter, name, **kwargs)


class Chroma61503(Chroma6150x):
    VRMS_MAX, IRMS_MAX, VPEAK_MAX, IPEAK_MAX = 300.0, 12.0, 424.2, 72.0

    def __init__(self, adapter, name="Chroma 61503 Programmable AC Source", **kwargs):
        super().__init__(adapter, name, **kwargs)


class Chroma61504(Chroma6150x):
    VRMS_MAX, IRMS_MAX, VPEAK_MAX, IPEAK_MAX = 300.0, 16.0, 424.2, 96.0

    def __init__(self, adapter, name="Chroma 61504 Programmable AC Source", **kwargs):
        super().__init__(adapter, name, **kwargs)


class Chroma61505(Chroma6150x):
    VRMS_MAX, IRMS_MAX, VPEAK_MAX, IPEAK_MAX = 300.0, 32.0, 424.2, 192.0

    def __init__(self, adapter, name="Chroma 61505 Programmable AC Source", **kwargs):
        super().__init__(adapter, name, **kwargs)
