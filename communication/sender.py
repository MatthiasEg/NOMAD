import zmq
import configparser
import logging

class Sender:

  def __init__(self, nodeConfigSection):
    self._loadConfiguration(nodeConfigSection)
    self._openPushSocket()
    self.sendCounter = 0

  def _loadConfiguration(self, nodeConfigSection):
    config = configparser.ConfigParser()                                     
    config.read('config.ini')
    self.host = config.get(nodeConfigSection, 'HOST')
    self.port = config.get(nodeConfigSection, 'PORT')
    self.logger = logging.getLogger(nodeConfigSection + "_SENDER")

  def _openPushSocket(self):
    self.socket = zmq.Context().socket(zmq.PUB) # pylint: disable=no-member
    self.socket.bind("tcp://%s:%s" % (self.host, self.port))
    self.logger.info("bind to host: tcp://%s:%s" % (self.host, self.port))

  def send(self, message):
    self.socket.send_pyobj(message)
    self.sendCounter += 1
    self.logger.debug("send (%s): %s"  % (self.sendCounter, message))
  
  def close(self):
    self.socket.close()
    self.logger.info("unbind from host: tcp://%s:%s" % (self.host, self.port))