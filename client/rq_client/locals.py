"""

rq_client/locals.py

written by: Oliver Cordes 2019-05-01
changed by: Oliver Cordes 2019-05-02


purpose:

compile all infos about the running computer to send
to the rq_server for statistics

"""


import socket
import psutil
from psutil._common import bytes2human
import platform


def get_ip1():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_ip2():
    try:
        IP =  socket.gethostbyname(socket.gethostname())
    except:
        IP = '127.0.0.1'
    return IP



def get_ip():
    # ask for an IP with routing
    IP = get_ip1()

    if IP == '127.0.0.1':
        IP = get_ip2()

    return IP


def get_host_info():
    data = {'ip': get_ip(),
            'hostname': socket.gethostname(),
            'cpus'    : psutil.cpu_count(logical=False),
            'mem'     : bytes2human(psutil.virtual_memory()[0]),
            'os'      : platform.platform(),
            'python'  : platform.python_version(),
            }

    return data


def submit_host_info(session):
    pass


if __name__ == '__main__':
    data = get_host_info()
    print(data)
