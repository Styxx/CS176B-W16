#!/usr/bin/env python

# Proxy server with aid from: http://voorloopnul.com/blog/a-python-proxy-in-less-than-100-lines-of-code/

__version__ = '0.1'
__author__ = 'Vincent Chang'
CLIENTHOST = ''
CLIENTPORT = 57575
NUM_REQUESTS = -1
LOG_DIRECTORY = ""
KILL_FLAG = 0

import sys
import argparse
import logging
import multiprocessing
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
  def start(self, port):
    global KILL_FLAG
    KILL_FLAG = 0                           # Reset kill flag for next instance
    self.connect(port)
    logger.debug('Exited connect function')
    while True:
      if KILL_FLAG == 1:
        
        break
      """ After connected, anything received gets passed or closes """
      logger.debug('looking for data')
      self.server_data = self.server_socket.recv(1024)
      logger.debug('got data from server')
      
      if self.server_data == "":
        self.close(1)
        break
      else:
        self.pass_data(self.server_data, 1)
        
        
      self.client_data = self.client_socket.recv(1024)
      logger.debug('got data from client')
      
      if self.client_data == "":
        self.close(0)
        break
      else:
        self.pass_data(self.client_data, 0)



  """ Connects proxy to client. Gets server from client request. Connects to server"""
  def connect(self, server_port):
    global KILL_FLAG
    """ Connect to client """
    self.client_socket, self.client_address = self.client.accept()               # Establish connection with client
    logger.debug('Connected to client: %s', self.client_address)
    
    """ Get first HTTP request line from client """
    request_text = self.client_socket.recv(1024)                                 # First thing should be request line
    #logger.debug(request_text)
    
    """ Check client connection """
    if request_text == "":
      self.client_socket.close()
      logger.error("Can't establish connection with client. Closing connection.")
    else:
      """ Connect to server """
      self.server_hostname = self.get_host_from_header(request_text)
      self.create_log(self.client_address, self.server_hostname)
      self.server_socket = Server().start(self.server_hostname, server_port)
      
    """ Check server connection """
    if self.server_socket:
      logger.info('Connected to server: %s', self.server_hostname)
      """ Send client's inital request to server """
      self.server_socket.send(request_text) 
      logger.debug('Sent request text to server')
    else:
      logger.error("Can't establish connection with server: %s:%s", self.server_hostname, server_port)
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
  

  def pass_data(self, data, source):
    if source == 0:
      logger.info('Client -> Server: ' + data)
      self.server_socket.send(data)
    else:
      logger.info('Server -> Client: ' + data)
      self.client_socket.send(data)
    
  def close(self, source):
    if source == 1:
      logger.info('Server %s has disconnected', self.server_hostname)
      logger.info('Closing connection with client: %s', self.client_address)
      self.client_socket.close()
    else:
      logger.info('Client %s has disconnected', self.client_address)
      logger.info('Closing connection with server: %s', self.server_hostname)
      self.server_socket.close()
  
  def get_host_from_header(self, header):
    host = header.split("\r\n")[1].split(" ")[1]
    return host




def main():
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
    
  
 
  #TODO: figure out how to do log filenames - [index]_[sourceip]_[servername]
    #import os.path
    #os.path.isfile(fname) 
  #TODO: figure out how to do log directory (args.log)
  
  
  # Demarshall
  server_port = args.port                # try another port if occupied
  num_workers = args.numworker
  timeout = args.timeout
  
  if args.log is not None:
    global LOG_DIRECTORY
    LOG_DIRECTORY = args.log + '/'
  
  print LOG_DIRECTORY
   
    
  #logger = logging.getLogger('mproxy')

  proxy = Proxy(CLIENTHOST, CLIENTPORT)
  while True:
    try:
      proxy.start(server_port)
      pass
    except KeyboardInterrupt:
      print 'Ctrl C - Stopping server'
      break

  print "end of main"
  
  
if __name__ == '__main__':
  main()