import mock
import unittest
import numpy as np
import rfb


class TestRFB(unittest.TestCase):

  def setUp(self):
    self.rfb = rfb.Proto((3,8))
    self.rfb.wfile = mock.Mock()
    self.rfb.rfile = mock.Mock()
    self.rfb.request = mock.Mock()

  def test_version(self):
    self.assertEqual(self.rfb.state, 'connection')
    self.rfb.rfile.readline.return_value = "RFB 003.008\n"
    self.rfb.handle()

    self.rfb.wfile.write.assert_called_with("RFB 003.008\n")
    self.assertEqual(self.rfb.version, (3,8))

  def test_security(self):
    #self.rfb.machine.remove_transition(trigger='wait_init', source='security_type_received', dest='client_init_received')
    self.rfb.disable_state('client_init_received')

    self.rfb.state = 'version_received'
    self.assertEqual(self.rfb.state, 'version_received')
    self.rfb.start_security()
    self.rfb.request.recv.return_value = np.uint8(2)
    self.rfb.handle()

    np.testing.assert_array_equal(np.array([2,1,2], dtype=np.uint8), self.rfb.wfile.write.call_args[0][0])
    self.assertEqual(self.rfb.secType, np.uint8(2))

  def test_initialization(self):
    pass

if __name__ == '__main__':
  unittest.main()
