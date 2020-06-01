import socket
import logging

from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)


print("default timeout: %s" % socket.getdefaulttimeout())  # initial value is None

HOST = "localhost"
PORT = 5454

s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
try:
    s.bind((HOST, PORT))
except socket.error as e:
    exit("unable to bind to: %s:%s" % (HOST, PORT))
print("socket: %s %s" % s.getsockname())

while True:
    data, address = s.recvfrom(4096)
    data = data.decode('utf-8')
    print("rx: %s [%s] from %s" % (data, len(data), address))
