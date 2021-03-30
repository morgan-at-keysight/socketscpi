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
       self.awg = socketscpi.SocketInstrument('127.0.0.1', port=60003)

        #self.awg.write('*rst')
        #self.awg.query('*opc?')test_m8190.py
        #self.awg.write('abort')

    def tearDown(self) -> None:
       self.awg.disconnect()
        self.assertRaises(OSError,self.awg.query, '*idn?')

    def test_constructor(self):
        print('init')
        self.assertIsInstance(self.vsa, socketscpi.SocketInstrument)
        self.assertIsInstance(self.vsa.instId, str)
        # self.assertEqual(self.vsa.instId[:28], 'Agilent Technologies,89601B,')

    def test_write(self):
        print('write')
        self.assertRaises(socketscpi.SockInstError,self.awg.write, 19)
        self.assertRaises(socketscpi.SockInstError,self.awg.write, ['nineteen', 19])

    def test_query2(self):
        print('query')
        self.assertRaises(socketscpi.SockInstError,self.awg.query, 19)
        self.assertRaises(socketscpi.SockInstError,self.awg.query, ['nineteen', 19])
        self.assertRaises(socketscpi.SockInstError,self.awg.query, '*opc')
        result =self.awg.query('*opc?')
        self.assertEqual(result, '1')

    def test_read(self):
        print('read')
        self.awg.write('*idn?')
        self.assertEqual(self.vsa.read(),self.awg.instId)

    # def test_binblockread(self):
    #     print('binblockread')
    #    self.awg.write('initiate:continuous 0')
    #    self.awg.write('initiate:immediate')
    #    self.awg.query('*opc?')
    #    self.awg.write('format:trace:data real64')
    #     numPoints = int(self.vsa.query('rbw:points?'))
    #     data =self.awg.binblockread('trace1:data:y?', datatype='d').byteswap()
    #     self.assertEqual(len(data), numPoints)
    #     dataWrong =self.awg.binblockread('trace1:data:y?', datatype='f').byteswap()
    #     self.assertNotEqual(len(dataWrong), numPoints)
    #     self.assertRaises(socketscpi.SockInstError,self.awg.binblockread, 19, datatype='d')
    #     self.assertRaises(socketscpi.SockInstError,self.awg.binblockread, ['nineteen', 19], datatype='d')
    #     self.assertRaises(socketscpi.BinblockError,self.awg.binblockread, 'trace1:data:y?', datatype='r')
    #     self.assertRaises(socketscpi.BinblockError,self.awg.binblockread, '*idn?', datatype='d')

    def test_binblockwrite(self):
        pass

    def test_err_check(self):
        print('err_check')
       self.awg.write('gibberish')
        self.assertRaises(socketscpi.SockInstError,self.awg.err_check)
       self.awg.write('*opc?')
        self.assertRaises(socketscpi.SockInstError,self.awg.err_check)

if __name__ == '__main__':
    unittest.main()

