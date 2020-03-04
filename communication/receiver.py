import zmq
import configparser
import logging

class Receiver:
  
  def __init__(self, nodeConfigSection):
    self._loadConfiguration(nodeConfigSection)
    self._openPullSocket()
    self.receivedCounter = 0

  def _loadConfiguration(self, nodeConfigSection):
    config = configparser.ConfigParser()                                     
    config.read('config.ini')
    self.host = config.get(nodeConfigSection, 'HOST')
    self.port = config.get(nodeConfigSection, 'PORT')
    self.logger = logging.getLogger(nodeConfigSection + "_RECEIVER")

  def _openPullSocket(self):    
    self.socket = zmq.Context().socket(zmq.SUB) # pylint: disable=no-member
    self.socket .setsockopt_string(zmq.SUBSCRIBE, "") # pylint: disable=no-member
    self.socket.connect("tcp://%s:%s" % (self.host, self.port))
    self.logger.info("connect to host: tcp://%s:%s" % (self.host, self.port))

  def receive(self):
    message = self.socket.recv_pyobj()
    self.receivedCounter += 1
    self.logger.debug("received (%s): %s"  % (self.receivedCounter, message))
    return message

  def close(self):
    self.socket.close()
    self.logger.info("disconnect from host: tcp://%s:%s" % (self.host, self.port))