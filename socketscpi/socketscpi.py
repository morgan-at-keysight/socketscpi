"""
socketscpi
Author: Morgan Allison, Keysight RF/uW Application Engineer
This program provides a socket interface to Keysight test equipment.
It handles sending commands, receiving query results,
reading/writing binary block data, and checking for errors.
"""

import socket
import numpy as np
import ipaddress


class SocketInstrument:
    def __init__(self, ipAddress, port=5025, timeout=10, noDelay=True):
        """
        Open socket connection with settings for instrument control.

        Args:
            ipAddress (string): Instrument host IP address. Argument is a string containing a valid IP address.
            port (int): Port used by the instrument to facilitate socket communication (Keysight equipment uses port 5025 by default).
            timeout (int): Timeout in seconds.
            noDelay (bool): True sends data immediately without concatenating multiple packets together. Just leave this alone.
        """
        # Validate IP address (will raise an error if given an invalid address).
        ipaddress.ip_address(ipAddress)

        # Create socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Handle
        if noDelay:
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        # Turn blocking behavior off so we can control the socket while it processes commands
        self.socket.setblocking(False)
        # Set timeout
        self.socket.settimeout(timeout)
        # Connect to socket
        self.socket.connect((ipAddress, port))

        # Get the instrument ID
        self.instId = self.query('*idn?')

        # Enable verbose error checking of instrument supports this
        try:
            self.write('syst:err:verbose 1')
            self.err_check()
        except SockInstError:
            pass

    def disconnect(self):
        """Gracefully close socket connection."""
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()


    def write(self, cmd):
        """
        Writes a command to the instrument.

        Args:
            cmd (string): Documented SCPI command to be sent to the instrument.
        """

        if not isinstance(cmd, str):
            raise SockInstError('Argument must be a string.')

        msg = '{}\n'.format(cmd)
        self.socket.send(msg.encode('latin_1'))
        # msg = '{}\n*esr?'.format(cmd)
        # ret = self.query(msg)
        # if (int(ret) != 0):
        #     raise SockInstError('esr non-zero: {}'.format(ret))

    def read(self):
        """
        Reads the output buffer of the instrument.

        Returns (string): Contents of the instrument's output buffer.
        """

        response = b''
        while response[-1:] != b'\n':
            response += self.socket.recv(1024)

        # Strip out whitespace and return.
        return response.decode('latin_1').strip()

    def query(self, cmd):
        """
        Sends query to instrument and reads the output buffer immediately afterward.

        Args:
            cmd (string): Documented SCPI query to be sent to instrument (should end in a "?" character).

        Returns (string): Response from instrument's output buffer as a latin_1-encoded string.
        """

        if not isinstance(cmd, str):
            raise SockInstError('Argument must be a string.')
        if '?' not in cmd:
            raise SockInstError('Query must include "?"')

        self.write(cmd)
        return self.read()

    def err_check(self):
        """Prints out all errors and clears error queue. Raises SockInstError with the info of the error encountered."""

        err = []

        # syst:err? response format varies between instruments, so remove whitespace and extra characters before checking
        if 'mso' in self.instId.lower() or 'dso' in self.instId.lower():
            cmd = 'SYST:ERR? string'
        else:
            cmd = 'SYST:ERR?'

        # Strip out extra characters
        temp = self.query(cmd).strip().replace('+', '').replace('-', '')
        # Read all errors until none are left
        while temp != '0,"No error"':
            # Build list of errors
            err.append(temp)
            temp = self.query('syst:err?').strip().replace('+', '').replace('-', '')
        if err:
            raise SockInstError(err)

    def binblockread(self, cmd, datatype='b', debug=False):
        """
        Send a command and parses response in IEEE 488.2 binary block format.

        cmd: string containing SCPI command
        datatype:

        The waveform is formatted as:
        #<x><yyy><data><newline>, where:
        <x> is the number of y bytes. For example, if <yyy>=500, then <x>=3.
        NOTE: <x> is a hexadecimal number.
        <yyy> is the number of bytes to transfer. Care must be taken
        when selecting the data type used to interpret the data.
        The dtype argument used to read the data must match the data
        type used by the instrument that sends the data.
        <data> is the data payload in binary format.
        <newline> is a single byte new line character at the end of the data.

        Args:
            cmd (string): Documented SCPI query that causes the instrument to return a binary block.
            datatype (string): Data type for the returned data. Uses the same naming convention as Python's struct module
                https://docs.python.org/3/library/struct.html#format-characters
            debug (bool): Turns debug mode on or off.

        Returns (NumPy ndarray): Array containing the data from the instrument buffer.

        """

        # Decode data type
        if datatype == 'b':
            dtype = np.int8
        elif datatype == 'B':
            dtype = np.uint8
        elif datatype == 'h':
            dtype = np.int16
        elif datatype == 'H':
            dtype = np.uint16
        elif datatype == 'i' or datatype == 'l':
            dtype = np.int32
        elif datatype == 'I' or datatype == 'L':
            dtype = np.uint32
        elif datatype == 'q':
            dtype = np.int64
        elif datatype == 'Q':
            dtype = np.uint64
        elif datatype == 'f':
            dtype = np.float32
        elif datatype == 'd':
            dtype = np.float64
        else:
            raise BinblockError('Invalid data type selected.')

        # Send command/query
        self.write(cmd)

        # Read # character, raise exception if not present.
        if self.socket.recv(1) != b'#':
            raise BinblockError('Data in buffer is not in binblock format.')

        # Extract header length and number of bytes in binblock.
        headerLength = int(self.socket.recv(1).decode('latin_1'), 16)
        numBytes = int(self.socket.recv(headerLength).decode('latin_1'))

        if debug:
            print('Header: #{}{}'.format(headerLength, numBytes))

        # Create a buffer object of the correct size and expose a memoryview for efficient socket reading
        rawData = bytearray(numBytes)
        buf = memoryview(rawData)

        # While there is data left to read...
        while numBytes:
            # Read data from instrument into buffer.
            bytesRecv = self.socket.recv_into(buf, numBytes)
            # Slice buffer to preserve data already written to it. This syntax seems odd, but it works correctly.
            buf = buf[bytesRecv:]
            # Subtract bytes received from total bytes.
            numBytes -= bytesRecv
            if debug:
                print('numBytes: {}, bytesRecv: {}'.format(
                    numBytes, bytesRecv))

        # Receive termination character.
        term = self.socket.recv(1)
        if debug:
            print('Term char: ', term)
        # If term char is incorrect or not present, raise exception.
        if term != b'\n':
            print('Term char: {}, rawData Length: {}'.format(
                term, len(rawData)))
            raise BinblockError('Data not terminated correctly.')

        # Convert binary data to NumPy array of specified data type and return.
        return np.frombuffer(rawData, dtype=dtype)

    # noinspection PyUnresolvedReferences
    @staticmethod
    def binblock_header(data):
        """Returns a IEEE 488.2 binary block header

        #<x><yyy>..., where:
        <x> is the number of y bytes. For example, if <yyy>=500, then <x>=3.
        NOTE: <x> is a hexadecimal number.
        <yyy> is the number of bytes to transfer. """

        numBytes = memoryview(data).nbytes
        return f'#{len(str(numBytes))}{numBytes}'

    def binblockwrite(self, cmd, data, debug=False, esr=True):
        """
        Sends a command and payload data with IEEE 488.2 binary block format

        The data is formatted as:
        #<x><yyy><data><newline>, where:
        <x> is the number of y bytes. For example, if <yyy>=500, then <x>=3.
        NOTE: <x> is a hexadecimal number.
        <yyy> is the number of bytes to transfer.
        <data> is the data payload in binary format.
        <newline> is a single byte new line character at the end of the data.

        Args:
            cmd (string): SCPI command used to send data to instrument as a binary block.
            data (NumPy ndarray): NumPy array containing data to load into the instrument.
            debug (bool): Turns debug mode on or off.
            esr (bool): Determines whether to append an ESR query to the end of the binblockwrite for error checking purposes.
        """

        # Generate binary block header from data
        header = self.binblock_header(data)

        # Send message, header, data, and termination
        self.socket.send(cmd.encode('latin_1'))
        self.socket.send(header.encode('latin_1'))
        self.socket.send(data)
        self.socket.send(b'\n')

        if debug:
            print(f'binblockwrite --')
            print(f'msg: {cmd}')
            print(f'header: {header}')

        # Check error status register and notify of problems
        if esr:
            r = self.query('*esr?')
            if int(r) is not 0:
                self.err_check()


class SockInstError(Exception):
    pass


class BinblockError(Exception):
    pass
