from logger_configuration import logger
import math

def get_current_ip():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("10.255.255.255", 1))
        ip_address = sock.getsockname()[0]
        #logger.Debug(f'Address : {ip_address}')
    except:
        ip_address = "127.0.0.1"
    finally:
        sock.close()
    return ip_address
    #hostname = socket.gethostname()


def am_I_this_computer(ip):
    if ip == get_current_ip():
        return True
    else:
        return False


# Message of the day for a client
def message_of_the_day(computers):
    for computer_key in computers.keys():
        ip = get_current_ip()
        if ip == computers[computer_key].ip:
            logger.info(f"Client Running - Agent {computers[computer_key].agent_name} running on  : {computer_key}({ip})")

def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper
