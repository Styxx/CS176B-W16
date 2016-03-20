### Proxy Server - CS176B Lab 3
##### Vincent Chang (_Styxx_)
* HTTP Python proxy server
  1. Connects to client
  2. Gets server from client's request text
  3. Connects to server
  4. Sends data from server to client and vice versa

##### Usage:
```
mproxy.py [-h] [-v] [-p [PORT]] [-n [NUMWORKER]] [-t [TIMEOUT]] [-l LOG]

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program, version, author, and exit
  -p [PORT], --port [PORT]
                        port number client will connect to. Required.
  -n [NUMWORKER], --numworker [NUMWORKER]
                        number of workers used for handling concurent
                        requests. Default: 10
  -t [TIMEOUT], --timeout [TIMEOUT]
                        time to wait before giving up on a response from
                        server. Default: -1 (infinite)
  -l LOG, --log LOG     directory to place logs (directory must be
                        preexisting)
```

##### Notes:
* Developed using [Cloud 9 IDE](c9.io).
* Logs are created every runthrough the main loop. Loop only ends when client and server both send empty data X number of times or sockets have been closed.
* Pages only fully load on the device when the client has sent another request or if the proxy server has been turned off.
  * This seems to be due to the loop activating again the moment the proxy closes connections to sockets, which immediately activates another client connection and request, causing the page to not load until the 2nd client request is fulfilled.
  * Possibly can be remedied with usage of select.
  * `CONNECT` requests are often sent from the client from background applications (like e-mail), which can load the page, as `CONNECT` requests are not handled.
