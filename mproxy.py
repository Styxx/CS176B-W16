#!/usr/bin/env python

__version__ = '0.1'
__author__ = 'Vincent Chang'
CLIENTHOST = ''
CLIENTPORT = 57575
TIMEOUT = 0
NUM_REQUESTS = -1
LOG_DIRECTORY = ""
KILL_FLAG = 0
S_EMPTY = 0
C_EMPTY = 0

import sys
import argparse
import logging
from multiprocessing import Pool
import threading
import ssl
import socket

logger = logging.getLogger(__name__)

class Server:
  def __init__(self):
    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.debug('Socket to server created')
  def start(self, host, port):
    try:
      self.server.connect((host, port))
      return self.server
    except Exception, e:
      print e
      return False


#class Proxy(multiprocessing.Process):
class Proxy():
  
  
  """ Initialize socket connection to client """
  def __init__(self, host, port):
    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.client.bind((host, port))
    logger.debug('Socket to client created - Hostname: ' + socket.gethostname())
    logger.info('Listening for client')
    self.client.listen(5)               
    pass

  """ Adds new client to list, then starts connection """
  def start(self):
    global KILL_FLAG, S_EMPTY, C_EMPTY
    
    if KILL_FLAG == 1:
      KILL_FLAG = 0
      return None
      
    #KILL_FLAG = 0                           # Reset kill flag for next instance
    self.connect()
    logger.debug('Exited connect function')
    logger.debug('Kill is: ' + str(KILL_FLAG))
    while KILL_FLAG == 0:
      """ After connected, anything received gets passed or closes """
      self.server_data = "d"
      
      while self.server_data != "":
        logger.debug('Looking for server data')
        self.server_data = self.server_socket.recv(1024)
        
        if self.server_data == "":
          logger.debug('Empty data from server')
          #self.close(1)
          #KILL_FLAG = 1;
          S_EMPTY = S_EMPTY + 1
          break
        elif len(self.server_data) < 1024:
          logger.debug('Last client packet')
          self.pass_data(self.server_data, 1)
          break
        else:
          S_EMPTY = 0
          logger.debug('Got data from server')
          self.pass_data(self.server_data, 1)
        
        

      self.client_data = "d"
      while self.client_data != "":
        logger.debug('Looking for client data')
        self.client_data = self.client_socket.recv(1024)
        
        if self.client_data == "":
          logger.debug('Empty data from client')
          #self.close(0)
          C_EMPTY = C_EMPTY + 1
          break
        elif len(self.client_data) < 1024:
          logger.debug('Last client packet')
          self.pass_data(self.client_data, 1)
          break  
        else:
          C_EMPTY = 0
          logger.debug('Got data from client')
          self.pass_data(self.client_data, 0)
        
        
      if S_EMPTY > 5:
        if C_EMPTY > 5:
          self.close()
      


  """ Connects proxy to client. Gets server from client request. Connects to server"""
  def connect(self):
    global KILL_FLAG
    
    """ Connect to client """
    self.client_socket, self.client_address = self.client.accept()               # Establish connection with client
    self.client_socket.setblocking(0)
    self.client_socket.settimeout(10)
    logger.debug('Connected to client: %s', self.client_address)
    
    """ Get first HTTP request line from client """
    request_text = self.client_socket.recv(1024)                                 # First thing should be request line
    print request_text
    #logger.debug(request_text)
    
    """ Check client connection """
    if request_text == "":
      self.client_socket.close()
      logger.error("Can't establish connection with client. Closing connection.")
      KILL_FLAG = 1
      return None

    """ Connect to server """
    self.method, self.server_hostname, self.server_port = self.get_host_from_header(request_text)
    if self.method == 'CONNECT':
      KILL_FLAG = 1
      return None
      
    self.create_log(self.client_address, self.server_hostname)
    logger.debug("Attempting to connect to server [%s] with port [%s]", self.server_hostname, self.server_port)
    self.server_socket = Server().start(self.server_hostname, self.server_port)
    self.server_socket.setblocking(0)
    self.server_socket.settimeout(10)     #TODO: Set to global timeout later
      
    """ Check server connection """
    if self.server_socket:
      logger.info('Connected to server: %s', self.server_hostname)
      """ Send client's inital request to server """
      logger.info('Client -> Server: ' + request_text)
      self.server_socket.send(request_text) 
      logger.debug('Sent request text to server')
      
    else:
      logger.error("Can't establish connection with server: %s:%s", self.server_hostname, self.server_port)
      logger.error("Closing connection with client side: %s", self.client_address)
      self.client_socket.close()
      KILL_FLAG = 1

  def create_log(self, client_address, server_address):
    global NUM_REQUESTS
    NUM_REQUESTS = NUM_REQUESTS + 1
    
    new_log_file = logging.FileHandler(LOG_DIRECTORY + str(NUM_REQUESTS) + '_' + client_address[0] + '_' + str(server_address) + '.log')
    formatter = logging.Formatter('(%(asctime)s)(pid:%(process)d) %(levelname)s: %(message)s')
    new_log_file.setFormatter(formatter)
    logger.addHandler(new_log_file)
    logger.setLevel(logging.DEBUG)
    logger.debug('Log created with client [%s] and server [%s]', client_address[0], str(server_address))
  

  def pass_data(self, data, source):
    if source == 0:
      logger.info('Client -> Server: ' + data)
      self.server_socket.send(data)
    else:
      logger.info('Server -> Client: ' + data)
      self.client_socket.send(data)
  
  def close(self):
    global KILL_FLAG
    logger.info("Empty data from client [%s] and server [%s]", self.client_address, self.server_hostname)
    logger.info("Closing sockets")
    self.client_socket.close()
    self.server_socket.close()
    KILL_FLAG = 1
  
  """
  def close(self, source):
    if source == 1:
      logger.info('Server %s has disconnected', self.server_hostname)
      logger.info('Closing connection with client: %s', self.client_address)
      self.client_socket.close()
    else:
      logger.info('Client %s has disconnected', self.client_address)
      logger.info('Closing connection with server: %s', self.server_hostname)
      self.server_socket.close()
  """
  def get_host_from_header(self, header):

    method = header.split("\r\n")[0].split(" ")[0]
    """
    if method == 'CONNECT':
      pass
    else:
    """
    #host = header.split("\r\n")[0].split(" ")[1]#.split(":")[0]
    host = header.split("\r\n")[1].split(" ")[1]
    #port = header.split(" ")[1].split(":")[1]
    port = 80
    
    return method, host, port




def main():
  global KILL_FLAG
  parser = argparse.ArgumentParser (
    prog='mproxy.py'
  )
  parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1 - Vincent Chang', help='show program, version, author, and exit')
  parser.add_argument('-p', '--port', nargs='?', type=int, help='port number. if occupied, tries another')
  parser.add_argument('-n', '--numworker', nargs='?', type=int, default='10', help='number of workers used for handling concurent requests. Default: 10')
  parser.add_argument('-t', '--timeout', nargs='?', type=int, default='-1', help='time to wait before giving up on a response from server. Default: -1 (infinite)')
  parser.add_argument('-l', '--log', nargs=1, help='directory to place logs')
  args = parser.parse_args()

  print args
  
  if args.port is None:
    print "Port is required."
    sys.exit(1)
  
  
  # Demarshall
  CLIENTPORT = args.port                # try another port if occupied
  num_workers = args.numworker
  TIMEOUT = args.timeout
  
  if args.log is not None:
    #global LOG_DIRECTORY
    #TODO if args.log = ""
    LOG_DIRECTORY = args.log + '/'
  
  #print LOG_DIRECTORY
  
  """ Spawn thread pool """
  #pool = Pool(processes=num_workers)
  proxy = Proxy(CLIENTHOST, CLIENTPORT)
  print socket.gethostname()
  while True:
  #while (threading.active_count() < num_workers):
  #for i in range(1, num_workers):
    try:
      #thread = threading.Thread(target=proxy.start, args=(server_port,))
      #thread.daemon = True
      #thread.start()
      #print 'started thread'
      KILL_FLAG = 0
      proxy.start()
      #multiple_results = [pool.apply_async(proxy.start, (server_port,)) for i in range(num_workers)]
      pass
    except KeyboardInterrupt:
      print 'Ctrl C - Stopping server'
      self.client_socket.close()
      break
  #thread.join()
  print "end of main"
  
  
if __name__ == '__main__':
  main()