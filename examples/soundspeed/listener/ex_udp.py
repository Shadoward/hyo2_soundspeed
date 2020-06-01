from subprocess import check_output
import socket
import logging

from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)


# *** WINDOWS SPECIFIC ***

# find machine IPs (0.0.0.0 means all IPv4 addresses on the local machine)
# subprocess.call("ipconfig", shell=True)

# list all the running processes and pid
tsk = check_output("tasklist", shell=True).split(b'\n')
prc = dict()
for r in tsk[3:]:
    if len(r) < 20:
        continue
    prc[int(r[26:].split()[0])] = r[:26].strip()
print(prc)

# list the UDP listening ports: a: all connections and listening ports, o: owning process id, n: numeric form
udp = check_output("netstat -aon | find \"UDP\"", shell=True).split(b'\n')


# order by port number
def get_key(item):
    fields = item.split()
    try:
        return int(fields[1].split(':')[1])
    except:
        return 0


udp = sorted(udp, key=get_key)

for row in udp:
    fields = row.split()
    if len(fields) == 0:
        continue
    if fields[1][0] == "[":
        continue

    print('%s %s %s %s' % (fields[1].split(b':')[0].ljust(20),
                           fields[1].split(b':')[1].ljust(10),
                           fields[3].ljust(10),
                           prc[int(fields[3])]
                           ))

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print("host: %s %s" % (host_name, host_ip))
