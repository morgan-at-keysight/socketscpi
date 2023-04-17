=====
Usage
=====

To use socketscpi in a project::

    import socketscpi


To create an instrument object, do something like this::

    ipAddress = '192.168.1.123'
    instrument = socketscpi.SocketInstrument(ipAddress)

To send SCPI commands and queries to the instrument, do something like this::

    instrument.write('*rst')
    instrument.query('*opc?')

To check for and print out errors, do something like this::

    try:
        instrument.err_check()
    except socketscpi.SockInstError as e:
        print(str(e))

When you're finished communicating with your instrument, close it gracefully like this::

    instrument.close()

====================
**SocketInstrument**
====================
::

    socketscpi.SocketInstrument(host, port=5025, timeout=10, noDelay=True, globalErrCheck=False, verboseErrCheck=True)

Class constructor that connects to the test equipment and returns a SocketInstrument object that can be used to communicate with the equipment.

**Arguments**

* ``host`` ``(string)``: Instrument host IP address. Argument is a string containing a valid IP address.
* ``port`` ``(int)``:  Port used by the instrument to facilitate socket communication (Keysight equipment uses port 5025 by default).
* ``timeout`` ``(int)``: Timeout in seconds. This is how long the instrument will wait before sending a timeout error in response to a command or query. Argument is an int. Default is ``10``.
* ``noDelay`` ``(bool)``: True turns on the TCP_NODELAY flag, which sends data immediately without concatenating multiple packets together. Just leave this alone.
* ``globalErrCheck`` ``(bool)``: Determines if error checking will be done automatically after calling class methods.
* ``verboseErrCheck`` ``(bool)``: Determines if verbose error checking will be attempted.

**Returns**

* ``socketscpi.SocketInstrument``: Instrument object to be used for communication and control.


**close**
--------------
::

    SocketInstrument.close()

Gracefully closes socket connection.

**Arguments**

* None

**Returns**

* None


**write**
---------
::

    SocketInstrument.write(cmd)

Writes a command to the instrument.

**Arguments**

* ``cmd`` ``(string)``: Documented SCPI command to be sent to the instrument.

**Returns**

* None


**read**
--------
::

    SocketInstrument.read()

Reads the output buffer of the instrument.

**Arguments**

* None

**Returns**

* ``(string)``: Contents of the instrument's output buffer.


**query**
---------
::

    SocketInstrument.query(cmd)


Sends query to instrument and reads the output buffer immediately afterward.

**Arguments**

* ``cmd`` ``(string)``: Documented SCPI query to be sent to instrument (should end in a "?" character).

**Returns**

* ``(string)`` Response from instrument's output buffer as a latin_1-encoded string.


**err_check**
-------------
::

    SocketInstrument.err_check()

Prints out all errors and clears error queue. Raises SockInstError with the info of the error encountered.

**Arguments**

* None

**Returns**

* None


**query_binary_values**
-----------------------
::

    SocketInstrument.query_binary_values(cmd, datatype='b')

Sends a query and parses response in IEEE 488.2 binary block format.

**Arguments**

* ``cmd`` ``(string)``: Documented SCPI query that causes the instrument to return a binary block.
* ``datatype`` ``(string)``: Data type for the returned data. Uses the same `naming convention <https://docs.python.org/3/library/struct.html#format-characters>`_ used by Python's built-in ``struct`` module. Generally, test equipment includes a command to configure the data type of binary blocks, and the instrument's data type should match the data type used here. Default is ``'b'``, which specifies a signed 8 bit integer.

**Returns**

* ``(NumPy ndarray)`` Array containing the data from the instrument buffer.


**write_binary_values**
-----------------------
::

    SocketInstrument.write_binary_values(cmd, data)

Sends a command and payload data in IEEE 488.2 binary block format.

**Arguments**

* ``cmd`` ``(string)``: SCPI command used to send data to instrument as a binary block.
* ``data`` ``(NumPy ndarray)``: Data to be sent to the instrument. Refer to the documentation of the SCPI command being used for correct argument formatting.
* ``esr`` ``(bool)``: Determines whether to append an ESR query to the end of the binary block write for error checking purposes.

**Returns**

* None
