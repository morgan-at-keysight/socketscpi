=====
Usage
=====

To use socketscpi in a project::

    import socketscpi


====================
**SocketInstrument**
====================
::

    socketscpi.SocketInstrument(host, port=5025, timeout=10, noDelay=True)

Sets the basic configuration for the M8190A and populates class
attributes accordingly. It should be called any time these settings are
changed (ideally *once* directly after creating the M8190A object).

**Arguments**

* ``host``: Instrument host IP address. Argument is a string containing a valid IP address.
* ``port``: Port used by the instrument to facilitate socket communication. Argument is an int. Default is ``5025``, which is the default port used by Keysight instruments.
* ``timeout``: Timeout in seconds. This is how long the instrument will wait before sending a timeout error in response to a command or query. Argument is an int. Default is ``10``.
* ``noDelay``: Enables or disables the TCP_NODELAY flag when configuring the socket. Enabling TCP_NODELAY prevents the concatenation of multiple small data packets and sends them all in a larger message. Argument is a bool. Default is ``True``. Don't mess with this unless you have a specific need.

**Returns**

* SocketInstrument object



**disconnect**
--------------
::

    SocketInstrument.disconnect()

Gracefully closes socket connection.

**Arguments**

* None

**Returns**

* None


**query**
---------
::

    socketscpi.query(cmd)


Sends a query to the socket instrument and returns the response as a string.

**Arguments**

* ``cmd``: SCPI query sent to the instrument. Argument is a string, and should be a documented command that has a query form ending in ``?``.

**Returns**

* Response as a ``latin_1`` encoded string.


**write**
---------
::

    socketscpi.write(cmd)

Sends a command to the socket instrument.

**Arguments**

* ``cmd``: SCPI command sent to the instrument. Argument is a string.

**Returns**

* None


**err_check**
-------------
::

    socketscpi.err_check()

Checks for errors, clears error queue, and raises an exception if error has occurred.

**Arguments**

* None

**Returns**

* None


**binblockread**
----------------
::

    socketscpi.binblockread(cmd, datatype='b')

Sends a command and parses response in IEEE 488.2 binary block format.

**Arguments**

* ``cmd``: SCPI command sent to the instrument. Argument is a string, and should be a documented command that causes the instrument to return a binary block.
* ``datatype``: Data type used to interpret the returned binary data. Argument is a string that matches the `naming convention <https://docs.python.org/3/library/struct.html#format-characters>`_ used by Python's built-in ``struct`` module. Generally, test equipment includes a command to configure the data type of binary blocks, and the instrument's data type should match the data type used here. Default is ``'b'``, which specifies a signed 8 bit integer.

**Returns**

* Binblock data as a NumPy array.


**binblockwrite**
-----------------
::

    socketscpi.binblockwrite(cmd, data)

Sends a command and payload data in IEEE 488.2 binary block format.

**Arguments**

* ``cmd``: SCPI command sent to the instrument. Argument is a string, and should be a documented command with a binary block as its last argument.
* ``data``: Data to be sent to the instrument. Argument is a list or NumPy array. Refer to the documentation of the SCPI command being used for correct argument formatting.

**Returns**

* None
