#!/usr/bin/env python

# Proxy server with aid from: http://voorloopnul.com/blog/a-python-proxy-in-less-than-100-lines-of-code/

__version__ = '0.1'
__author__ = 'Vincent Chang'
CLIENTHOST = ''
CLIENTPORT = 57575
__numrequests__ = -1


import sys
import argparse
import logging
import select
import ssl
import socket

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


class Proxy:
  input_list = []
  channel = {}
  
  """ Initialize socket connection to client """
  def __init__(self, host, port):
    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.client.bind((host, port))
    logging.debug('Socket to client created - Hostname: ' + socket.gethostname())
    logging.info('Listening for client')
    self.client.listen(5)               
    pass

  """ Adds new client to list, then starts connection """
  def start(self, port):
    self.input_list.append(self.client)
    # TODO: Create new log here
    self.connect(port)
    logging.debug('Exited connect function')
    while True:
      """
      ss = select.select
      inputready, outputready, errorready = ss(self.input_list, [], [])
      for self.s in inputready:
        if self.s == self.client:
          self.connect(port)
          logging.debug('Exited connect function')
          break
        
    """    
      """ After connected, anything received gets passed or closes """
      logging.debug('looking for data')
      #self.data = self.s.recv(1024)
      self.server_data = self.server_socket.recv(1024)
      logging.debug('got data from server')
      
      if self.server_data == "":
        self.close(1)
        break
      else:
        self.pass_data(self.server_data, 1)
        
        
      self.client_data = self.client_socket.recv(1024)
      logging.debug('got data from client')
      
      if self.client_data == "":
        self.close(0)
        break
      else:
        self.pass_data(self.client_data, 0)
          
        
        
        """
        if self.data == "":
          self.close()
          break
        else:
          self.pass_data()
        """
    
  """ Connects proxy to client. Gets server from client request. Connects to server"""
  def connect(self, server_port):
    """ Connect to client """
    self.client_socket, self.client_address = self.client.accept()               # Establish connection with client
    logging.debug('Connected to client: %s', self.client_address)
    
    """ Get first HTTP request line from client """
    request_text = self.client_socket.recv(1024)                                 # First thing should be request line
    logging.info(request_text)
    
    """ Check client connection """
    if request_text == "":
      self.client_socket.close()
      logging.error("Can't establish connection with client. Closing connection.")
    else:
      """ Connect to server """
      self.server_hostname = self.get_host_from_header(request_text)
      self.server_socket = Server().start(self.server_hostname, server_port)
    
    """ Check server connection """
    if self.server_socket:
      logging.debug('Connected to server: %s', self.server_hostname)
      self.channel[self.client_socket] = self.server_socket
      self.channel[self.server_socket] = self.client_socket
    else:
      logging.error("Can't establish connection with server: %s:%s", self.server_hostname, server_port)
      logging.error("Closing connection with client side: %s", self.client_address)
      self.client_socket.close()
    
    """ Send client's inital request to server """
    self.server_socket.send(request_text) 
    logging.debug('Sent request text to server')

  def pass_data(self, data, source):
    if source == 0:
      logging.info('Client -> Server: ' + data)
      self.server_socket.send(data)
    else:
      logging.info('Server -> Client: ' + data)
      self.client_socket.send(data)
    
    
    """
    data = self.data
    logging.info(data)
    self.channel[self.s].send(data)
    """
    
    
  def close(self, source):
    if source == 1:
      logging.info('Server %s has disconnected', self.server_hostname)
      logging.info('Closing connection with client: %s', self.client_address)
      self.client_socket.close()
    else:
      logging.info('Client %s has disconnected', self.client_address)
      logging.info('Closing connection with server: %s', self.server_hostname)
      self.server_socket.close()
  
  def get_host_from_header(self, header):
    host = header.split("\r\n")[1].split(" ")[1]
    return host
    
    
"""
  def close(self):
    logging.info('%s has disconnected', self.getpeername())
    #Delete from list
    self.input_list.remove(self.s)
    self.input_list.remove(self.channel[self.s])
    
    other = self.channel[self.s]
    
    #Close connections
    self.channel[other].close()
    self.channel[self.s].close()
    
    #Delete from channel
    del self.channel[other]
    del self.channel[self.s]

"""


  
  
      


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

  #print args
  
  if args.port is None:
    print "Port is required."
    sys.exit(1)
    
  
 
  #TODO: figure out how to do log filenames - [index]_[sourceip]_[servername]
    #import os.path
    #os.path.isfile(fname) 
  #TODO: figure out how to do log directory (args.log)
  logging.basicConfig(filename='EXP.log',level=logging.DEBUG, format='(%(asctime)s)(pid:%(process)d) %(levelname)s: %(message)s')
  
  
  # Demarshall
  server_port = args.port                # try another port if occupied
  num_workers = args.numworker
  timeout = args.timeout
  logging.debug('Inputs: Port - %i || Timeout - %i || NumWorkers - %i || Log - %s', server_port, num_workers, timeout, args.log)

  proxy = Proxy(CLIENTHOST, CLIENTPORT)
  try:
    proxy.start(server_port)
    pass
  except KeyboardInterrupt:
    print 'Ctrl C - Stopping server'
    sys.exit(1)

  print "End of main"
  
  
if __name__ == '__main__':
  main()