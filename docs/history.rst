=======
History
=======

0.0.1 (2019-01-24)
------------------

* First release on PyPI.

0.0.4 (2019-04-26)
------------------

* Updated syntax for binblockread to mimic that of PyVISA. Created documentation.

2020.04.0 (2020-04-15)
----------------------

* Added a ``.read()`` method. Wrote test scripts to verify performance. Overhauled documentation. Switched to calendar-style versioning.

2020.05.0 (2020-05-13)
----------------------

* Adjusted the error checking for the ``.query()`` method to account for SCPI queries that require additional arguments.

2022.08.0 (2022-08-11)
----------------------

* Renamed ``binblockwrite()``, ``binblockread()``, and ``disconnect()`` to ``write_binary_values()``, ``read_binary_values()``, and ``close()``, respectively, to match the function calls in PyVISA.

2023.04.0 (2023-04-17)
----------------------

* Added error checking syntax for UXR scopes. Added an argument in the ``SocketInstrument`` constructor to allow user to decide if verbose error checking will be attempted.

2023.06.0 (2023-06-13)
----------------------

* Relaxed error checking to account for different "No error" responses from different instrument vendors. Updated comments.


2023.10.0 (2023-10-16)
----------------------

* Fixed a bug where socketscpi.err_check() would get stuck in an endless loop when controlling Keysight oscilloscopes.

2024.12.0 (2024-12-04)
----------------------

* Added logging functionality.

