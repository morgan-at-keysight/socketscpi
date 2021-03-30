import unittest
import socketscpi

class vsa_test(unittest.TestCase):

    def setUp(self) -> None:
        self.assertRaises(ValueError, socketscpi.SocketInstrument, 'five')
        self.assertRaises(ValueError, socketscpi.SocketInstrument, '127.0.0.0.0.0.1')
        self.assertRaises(ValueError, socketscpi.SocketInstrument, '127.0.0.257')
        self.assertRaises(ValueError, socketscpi.SocketInstrument, '127.0.0.1 ')
        self.assertRaises(ValueError, socketscpi.SocketInstrument, '127.0 .0.1')
        # self.assertRaises(TypeError, socketscpi.SocketInstrument, 127001)
        self.vsa = socketscpi.SocketInstrument('127.0.0.1')

        hw = '"Analyzer1"'
        hwList = self.vsa.query('system:vsa:hardware:configuration:catalog?').split(',')
        if hw not in hwList:
            raise ValueError('Selected hardware not present in VSA hardware list.')
        self.vsa.write(f'system:vsa:hardware:configuration:select {hw}')
        self.vsa.query('*opc?')

        # self.vsa.write('*rst')
        # self.vsa.query('*opc?')
        # self.vsa.write('abort')

    def tearDown(self) -> None:
        self.vsa.disconnect()
        self.assertRaises(OSError, self.vsa.query, '*idn?')

    def test_constructor(self):
        print('init')
        self.assertIsInstance(self.vsa, socketscpi.SocketInstrument)
        self.assertIsInstance(self.vsa.instId, str)
        self.assertEqual(self.vsa.instId[:28], 'Agilent Technologies,89601B,')

    def test_write(self):
        print('write')
        self.assertRaises(socketscpi.SockInstError, self.vsa.write, 19)
        self.assertRaises(socketscpi.SockInstError, self.vsa.write, ['nineteen', 19])

    def test_query2(self):
        print('query')
        self.assertRaises(socketscpi.SockInstError, self.vsa.query, 19)
        self.assertRaises(socketscpi.SockInstError, self.vsa.query, ['nineteen', 19])
        self.assertRaises(socketscpi.SockInstError, self.vsa.query, '*opc')
        result = self.vsa.query('*opc?')
        self.assertEqual(result, '1')

    def test_read(self):
        print('read')
        self.vsa.write('*idn?')
        self.assertEqual(self.vsa.read(), self.vsa.instId)

    def test_binblockread(self):
        print('binblockread')
        self.vsa.write('initiate:continuous 0')
        self.vsa.write('initiate:immediate')
        self.vsa.query('*opc?')
        self.vsa.write('format:trace:data real64')
        numPoints = int(self.vsa.query('rbw:points?'))
        data = self.vsa.binblockread('trace1:data:y?', datatype='d').byteswap()
        self.assertEqual(len(data), numPoints)
        dataWrong = self.vsa.binblockread('trace1:data:y?', datatype='f').byteswap()
        self.assertNotEqual(len(dataWrong), numPoints)
        self.assertRaises(socketscpi.SockInstError, self.vsa.binblockread, 19, datatype='d')
        self.assertRaises(socketscpi.SockInstError, self.vsa.binblockread, ['nineteen', 19], datatype='d')
        self.assertRaises(socketscpi.BinblockError, self.vsa.binblockread, 'trace1:data:y?', datatype='r')
        self.assertRaises(socketscpi.BinblockError, self.vsa.binblockread, '*idn?', datatype='d')

    def test_err_check(self):
        print('err_check')
        self.vsa.write('gibberish')
        self.assertRaises(socketscpi.SockInstError, self.vsa.err_check)
        self.vsa.write('*opc?')
        self.assertRaises(socketscpi.SockInstError, self.vsa.err_check)

if __name__ == '__main__':
    unittest.main()

