from transitions import Machine
import numpy as np
import socketserver

class Proto(socketserver.StreamRequestHandler):
  
  states = [ 'connection', 'version_sent', 'version_received', 'send_security_list', 'security_list_sent', 'security_type_received', 'client_init_reived', 'server_init_sent' ]
  secTypes = [ 'invalid', 'none', 'vncauth' ]
  pixelFormatType = [
    ('bpp', np.uint8),
    ('depth', np.uint8),
    ('bigendianflag', np.uint8),
    ('truecolourflag', np.uint8),
    ('redmax', np.uint16),
    ('greenmax', np.uint16),
    ('bluemax', np.uint16),
    ('redshift', np.uint8),
    ('greenshift', np.uint8),
    ('blueshift', np.uint8),
    ('padding0', np.uint8),
    ('padding1', np.uint8),
    ('padding2', np.uint8)
  ]

  def __init__(self, version):
    self.secType = 0
    self.version = version
    self.enabled_states = dict.fromkeys(Proto.states, True)

    self.machine = Machine(model=self, states=Proto.states, initial='connection', send_event=True)
    self.machine.add_transition('start_handshake', 'connection', 'version_sent', before='send_version', conditions=['enabled'])
    self.machine.add_transition('finish_handshake', 'version_sent', 'version_received', before='get_version', after='start_security', conditions=['enabled'])
    self.machine.add_transition('start_security', 'version_received', 'security_list_sent', before='send_security_list', conditions=['enabled'])
    self.machine.add_transition('finish_security', 'security_list_sent', 'security_type_received', before='get_security_type', after='wait_init', conditions=['enabled'])
    self.machine.add_transition('wait_init', 'security_type_received', 'client_init_received', before='get_client_init', conditions=['enabled'])

    # bits per pixel, depth, big-endian-flag, true-colour-flag, red-max, green-max, blue-max, red-shift, green-shift, blue-shift, padding, padding padding
    pixelFormat = np.array([32,32,0,0,0,0,0,0,0,0,0,0,0], dtype=Proto.pixelFormatType)

  def serverInitType(self, name):
    serverInitType = [
      ('fbwidth', np.uint16),
      ('fbheight', np.uint16),
      ('pixelformat', Proto.pixelFormatType),
      ('namelength', np.uint32),
      ('name', 'U%s' % (len(name)))]

  def disable_state(self, state):
    self.enabled_states[state] = False

  def enabled(self, event):
    return self.enabled_states[event.transition.dest]

  def send_version(self, event):
    self.wfile.write("RFB %.3d.%.3d\n" % self.version)

  def get_version(self, event):
    (major, minor) = self.rfile.readline().strip().split(' ')[1].split('.')

  def send_security_list(self, event):
    self.wfile.write(np.array([2,1,2], dtype=np.uint8))

  def get_security_type(self, event):
    secType = np.uint8(self.request.recv(1))
    if secType > 0 and secType < len(Proto.secTypes):
      self.secType = secType
    else:
      self.secType = 0 # error

  def get_client_init(self, event):
    self.sharedFlag = np.uint8(self.rfile.request.recv(1))
    
  def send_server_init(self, event):
    # U16 fb-width, U16 fb-height, [16] PIXEL_FORMAT, U32 name-length, [name-length]U8array name string
    self.wfile.write()
    
  def handle(self):
    if self.state == 'connection':
      self.start_handshake()
    elif self.state == 'version_sent':
      self.finish_handshake()
    elif self.state == 'version_received':
      self.start_security()
    elif self.state == 'security_list_sent':
      self.finish_security()

