"""
Simple VNA S Parameter Measurements
Author: Morgan Allison
Edited: 05/20
This script configures a VNA to make a single sweep, acquiring all four 2-port
S parameters in separate traces and plots each in a separate subplot.
Uses socket_instrument.py for instrument communication.
Windows 7 64-bit
Python 3.6.4
Matplotlib 2.2.2
Tested on N5242B PNA-X
"""

import socketscpi
import matplotlib.pyplot as plt
import time


def vna_setup(vna, start=10e6, stop=26.5e9, numPoints=401, ifBw=1e3, dwell=1e-3, measName=['meas1'], measParam=['S11']):
    """
    Sets up basic S parameter measurement(s). Configures measurements and traces in a single window, sets start/stop
    frequency, number of points, IF bandwidth, and dwell time from preset state.

    :param vna (socketscpi.SocketInstrument): SocketInstrument object used to send SCPI commands to VNA.
    :param start (float): Start frequency in Hz.
    :param stop (float): Stop frequency in Hz.
    :param numPoints (int): Number of points in measurement traces.
    :param ifBw (float): IF bandwidth in Hz.
    :param dwell (float): Dwell time per point in seconds.
    :param measName (list): A list of strings containing measurement names.
    :param measParam (list): A list of strings containing measurement parameter names.
    """

    if not isinstance(measName, list) and not isinstance(measParam, list):
        raise TypeError('measName and measParam must be lists of strings, even when defining only one measurement.')

    # Preset and activate window 1
    vna.write('system:fpreset')
    vna.query('*opc?')
    vna.write('display:window1:state on')

    # Order of operations: 1-Define a measurement. 2-Feed measurement to a trace on a window.
    t = 1
    for m, p in zip(measName, measParam):
        # Define measurement
        vna.write(f'calculate1:parameter:define "{m}","{p}"')
        # Feed measurement trace into specified window
        vna.write(f'display:window1:trace{t}:feed "{m}"')
        t += 1

    # Configure VNA stimulus
    vna.write(f'sense1:frequency:start {start}')
    vna.write(f'sense1:frequency:stop {stop}')
    vna.write(f'sense1:sweep:points {numPoints}')
    vna.write(f'sense1:sweep:dwell {dwell}')
    vna.write(f'sense1:bandwidth {ifBw}')


def vna_acquire(vna, measName):
    """
    Acquires frequency and measurement data from selected measurement on VNA for plotting.
    :param vna (socketscpi.SocketInstrument): SocketInstrument object used to send SCPI commands to VNA.
    :param measName (str): Name of measurement to be acquired.
    """

    if not isinstance(measName, str):
        raise TypeError('measName must be a string.')

    # Select measurement to be transferred.
    vna.write(f'calculate1:parameter:select "{measName}"')

    # Format data for transfer.
    vna.write('format:border swap')
    vna.write('format real,64')  # Data type is double/float64, not int64.

    # Acquire measurement data.
    meas = vna.binblockread('calculate:data? fdata', datatype='d')
    vna.query('*opc?')

    # Acquire frequency data.
    freq = vna.binblockread('calculate:x?', datatype='d')
    vna.query('*opc?')

    return freq, meas


def load_cal(vna, calSet='AD diff amp tms_STD_001'):

    # calSetList = vna.query('cset:cat?').replace('"', '').split(',')
    # print(calSetList)
    # if calSet in calSetList:
    #     print(calSetList.index(calSet))
    # else:
    #     raise ValueError(f'Cal set {calSet} not in list of cal sets.')

    # or just use the built-in command
    result = int(vna.query(f'cset:exists? "{calSet}"'))
    if result != 1:
        raise ValueError(f'Cal set {calSet} not in list of cal sets.')

    # Sense<channelNumber>
    vna.write(f'sense:correction:cset:activate "{calSet}", 1')

def setup_bal(vna, topology='bb', portConfig='1,3,2,4', measParam='sdd21'):
    """
    Sets up a balanced topology and creates a new balanced measurement.

    Args:
        vna (socketscpi.SocketInstrument): SCPI object used to communicate with VNA
        topology (str): Device topology. B – 1 port balanced device, BB – Balanced - Balanced device, BS – Balanced - Single-ended device, SB – Single-ended - Balanced device, SSB – Single-ended - Single-ended - Balanced device
        portConfig (str): Physical-to-logical port mappings. Should be a string of integers separated by commas. For balanced logical ports, syntax is <nPos>, <nNeg>. For single ended logical ports, only one value is needed.
        measParam (str): Balanced s-parameter
    """

    # Clear all traces and measurements so there are no conflicts
    vna.write('calc:par:del:all')
    # Create an extended measurement type NOTE THIS COMMAND IS SUPERSEDED BY CALCULATE:MEASURE:DEFINE. FIX THIS IN THE FUTURE
    vna.write(f'calc:par:def:ext "{measParam}", "s21"')
    # Select the measurement we just created
    vna.write(f'calc:par:sel "{measParam}"')

    # Grab the measurement number of the measurement/trace we just created for use later
    mNum = int(vna.query(f'calc:par:mnum?'))

    # Set up balanced-balanced topology and assign ports (p+, p-) pairs
    vna.write(f'calc:dtop "{topology}",{portConfig}')

    # Turn balanced transform on
    vna.write(f'calc:fsim:bal:par:state on')
    # Select the parameter
    vna.write(f'calc:fsim:bal:par{mNum}:bbal:def {measParam}')
    # Feed selected trace
    vna.write(f'disp:window1:trace{mNum}:feed "{measParam}"')


def setup_power_sweep(vna, startPower=-25, stopPower=-5, cf=1e9, sAtten=0, rAtten=0):

    vna.write(f'sense:sweep:type power')
    vna.write(f'sense:freq {cf}')

    vna.write(f'source:power1:attenuation {sAtten}')
    vna.write(f'source:power2:attenuation {sAtten}')
    vna.write(f'source:power3:attenuation {sAtten}')
    vna.write(f'source:power4:attenuation {sAtten}')

    vna.write(f'sense:power:attenuator areceiver, {rAtten}')
    vna.write(f'sense:power:attenuator breceiver, {rAtten}')
    vna.write(f'sense:power:attenuator creceiver, {rAtten}')
    vna.write(f'sense:power:attenuator dreceiver, {rAtten}')

    for i in range(1,5):
        vna.write(f'source:power{i}:start {startPower}')
        vna.write(f'source:power{i}:stop {stopPower}')


def measure_compression(vna):
    vna.write('initiate:continuous off')
    vna.write('initiate:immediate')
    vna.query('*opc?')

    vna.write(f'calculate:measure:marker:aoff')
    vna.write(f'calculate:measure:marker1:state on')

    vna.write(f'calculate:measure:marker1:function:compression:level 1')
    vna.write(f'calculate:measure:marker1:function:compression:state 1')
    vna.write(f'calculate:measure:marker1:function:execute compression')
    ip1db = float(vna.query(f'calculate:measure:marker1:x?'))
    result = vna.query(f'calculate:measure:marker1:y?')
    op1db = float(result.split(',')[0])
    print(f'Input @ compression: {ip1db} dBm')
    print(f'Output @ compression: {op1db} dBm')


def setup_specan_mode(vna, measName='harmonics', srcAtten=0, recAtten=0, rbw=1e3, power=-20):
    """sets up specan mode for differential measurements"""

    vna.write('calc:par:del:all')

    ports = [2, 4]

    for p in ports:
        # Create a spectrum analyzer measurement
        vna.write(f'calculate:custom:define "{measName}{p}","Spectrum Analyzer", "b{p}"')
        # Select spectrum analyzer measurement
        vna.write(f'calc:par:select "{measName}{p}"')
        # Get the measurement/trace identifier for the FEED command
        mNum = int(vna.query(f'calc:par:mnum?'))
        # Feed the measurement to window 1
        vna.write(f'disp:meas{mNum}:feed 1')
        # Set source attenuation
        vna.write(f'source:power{p - 1}:attenuation {srcAtten}')

        # Set RBW
        vna.write(f'sense:sa:bandwidth {rbw}')

        # Set source power
        vna.write(f'sense:sa:source{p - 1}:power {power}')

        # Set receiver attenuators
        if p == 1:
            atten = 'areceiver'
        elif p == 2:
            atten = 'breceiver'
        elif p == 3:
            atten = 'creceiver'
        elif p == 4:
            atten = 'dreceiver'
        else:
            raise ValueError('invalid port selected. ')
        vna.write(f'sense:power:attenuator {atten}, {recAtten}')


def measure_harmonics(vna, fundamental=1e9, harmonics=3):


    vna.write(f'sense:sa:source1:sweep:type cw')
    vna.write(f'sense:sa:source1:frequency:cw {fundamental}')
    vna.write(f'source:power1:mode on')

    vna.write(f'sense:sa:source3:sweep:type cw')
    vna.write(f'sense:sa:source3:frequency:cw {fundamental}')
    vna.write(f'source:phase3 180')
    vna.write(f'source:power3:mode on')

    # Delete all segments
    vna.write(f'sense:segment:delete:all')

    for s in range(1, harmonics + 1):
        vna.write(f'sense:segment{s}:add')
        vna.write(f'sense:segment{s}:frequency:center {fundamental * s}')
        vna.write(f'sense:segment{s}:frequency:span 20e6')
        vna.write(f'sense:segment{s}:state 1')

    # Set segmented sweep type
    vna.write(f'sense:sweep:type segment')

    vna.write('initiate:continuous off')
    vna.write('initiate:immediate')
    vna.query('*opc?')

    vna.err_check()

    vna.write(f'calculate:measure:marker:aoff')
    for m in range(1,3):
        vna.write(f'calculate:measure{m}:marker1:reference:state on')
        vna.write(f'calculate:measure{m}:marker2:state on')
        vna.write(f'calculate:measure{m}:marker3:state on')

        vna.write(f'calculate:measure{m}:marker1:coupling:state on')
        vna.write(f'calculate:measure{m}:marker2:coupling:state on')
        vna.write(f'calculate:measure{m}:marker3:coupling:state on')

        vna.write(f'calculate:measure{m}:marker2:delta on')
        vna.write(f'calculate:measure{m}:marker3:delta on')

        # Set marker frequencies
        vna.write(f'calculate:measure{m}:marker1:reference:x {fundamental}')
        vna.write(f'calculate:measure{m}:marker2:x {fundamental}')
        vna.write(f'calculate:measure{m}:marker3:x {fundamental * 2}')

        # vna.write('initiate:continuous off')
        # vna.write('initiate:immediate')
        # vna.query('*opc?')

        # For specan traces, marker y values return the trace value and zero. We only care about the first value.
        hd2 = float(vna.query(f'calculate:measure{m}:marker2:y?').split(',')[0])
        hd3 = float(vna.query(f'calculate:measure{m}:marker3:y?').split(',')[0])
        print(f'HD2: {hd2} dBc\nHD3: {hd3} dBc')

def main():
    vna = socketscpi.SocketInstrument('192.168.50.37', port=5025, timeout=30)
    # vna = socketscpi.SocketInstrument('127.0.0.1', port=5025)
    # vna.write('system:preset')
    # vna.query('*opc?')
    print('Connected to:', vna.instId)

    # load_cal(vna, 'AD diff amp tms_STD_001')
    # setup_bal(vna)
    #
    # freqs = [500e6, 1e9, 2e9, 3e9, 4e9]
    #
    # for f in freqs:
    #     setup_power_sweep(vna, stopPower=4, cf=f, rAtten=30)
    #     measure_compression(vna)
    #     time.sleep(1)

    setup_specan_mode(vna, srcAtten=20, recAtten=10, rbw=10, power=-30)

    load_cal(vna, calSet='Diff 4 port SpecAn_SA_001')
    measure_harmonics(vna, fundamental=1e9)

    vna.err_check()
    vna.disconnect()

if __name__ == '__main__':
    main()
