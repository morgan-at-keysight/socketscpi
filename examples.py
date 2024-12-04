import socketscpi
import numpy as np


def awg_example(ipAddress, port=5025):
    """Tests generic waveform transfer to M8190. Length and granularity checks not performed."""
    awg = socketscpi.SocketInstrument(ipAddress=ipAddress, port=port, timeout=10)
    print(awg.instId)
    awg.write('*rst')
    awg.query('*opc?')

    fs = 10e9
    freq = 100e6
    res = 'wsp'

    awg.write('func:mode arb')
    awg.write(f'trace1:dwidth {res}')
    awg.write(f'frequency:raster {fs}')

    awg.write('output1:route dac')
    awg.write('output1:norm on')

    rl = int(fs / freq * 64)
    t = np.linspace(0, rl / fs, rl, endpoint=False)
    wfm = np.array(2047 * np.sin(2 * np.pi * freq * t), dtype=np.int16) << 4

    awg.write(f'trace:def 1, {rl}')
    awg.write_binary_values('trace:data 1, 0, ', wfm)

    awg.write('trace:select 1')
    awg.write('init:cont on')
    awg.write('init:imm')
    awg.query('*opc?')

    awg.err_check()
    awg.close()


def vna_example(ipAddress, port=5025):
    """Test generic VNA connection, sweep control, and data transfer."""
    vna = socketscpi.SocketInstrument(ipAddress=ipAddress, port=port, timeout=10, log=False)
    print(vna.instId)

    vna.write('system:fpreset')
    vna.query('*opc?')

    measName = 'meas1'
    vna.write('display:window1:state on')
    vna.write(f'calc1:parameter:define "{measName}", "S11"')
    vna.write(f'display:window1:trace1:feed "{measName}"')
    vna.write(f'calc1:parameter:select "{measName}"')

    vna.write('initiate:continuous off')
    vna.write('initiate:immediate')
    vna.query('*opc?')
    vna.write('display:window1:y:auto')

    vna.write('format:border swap')
    vna.write('format real,64')

    meas = vna.query_binary_values('calculate1:data? fdata', datatype='d')
    vna.query('*opc?')

    freq = vna.query_binary_values('calculate1:x?', datatype='d')
    vna.query('*opc?')

    vna.err_check()
    vna.close()

    return freq, meas


def scope_example(ipAddress):
    # Make connection to instrument
    scope = socketscpi.SocketInstrument(ipAddress)

    # Measurement setup variables
    vRange = 2
    tRange = 500e-9
    trigLevel = 0
    ch = 1

    # Preset and wait for operation to complete
    scope.write('*rst')
    scope.query('*opc?')

    # Setup up vertical and horizontal ranges
    scope.write(f'channel{ch}:range {vRange}')
    scope.write(f'timebase:range {tRange}')

    # Set up trigger mode and level
    scope.write('trigger:mode edge')
    scope.write(f'trigger:level channel{ch}, {trigLevel}')

    # Set waveform source
    scope.write(f'waveform:source channel{ch}')

    # Specify waveform format
    scope.write('waveform:format byte')

    # Capture data
    scope.write('digitize')

    # Transfer binary waveform data from scope
    data = scope.query_binary_values('waveform:data?', datatype='b')

    # Query x and y values to scale the data appropriately for plotting
    xIncrement = float(scope.query('waveform:xincrement?'))
    xOrigin = float(scope.query('waveform:xorigin?'))
    yIncrement = float(scope.query('waveform:yincrement?'))
    yOrigin = float(scope.query('waveform:yorigin?'))
    length = len(data)

    # Apply scaling factors
    time = [(t * xIncrement) + xOrigin for t in range(length)]
    wfm = [(d * yIncrement) + yOrigin for d in data]

    # Check for errors
    scope.close()

    return time, wfm


def main():
    # awg_example('127.0.0.1', port=5025)
    vna_example('127.0.0.1', port=5025)
    # scope_example('141.121.210.161')

if __name__ == '__main__':
    main()
