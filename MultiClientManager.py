import socket
import Tools
import traceback
import time
from logger_configuration import logger
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
import queue


class ClientThreadObject(QObject):
    def __init__(self, ip, computers_dict, sending_queue, parent=None):
        super(ClientThreadObject, self).__init__(parent)
        self.ip = ip
        self.sending_queue = sending_queue
        self.computers_dict = computers_dict
        self.is_active = True
        self.is_connected = False
        self.client_to_server_socket = None
        self.port = self.computers_dict[self.ip].port

    def __del__(self):
        self.client_to_server_socket.close()

    @pyqtSlot()
    def connect_to_server(self):
        # this method behaves like a State Machine with two states (connected and not connected)
        # it handles disconnections timeouts and error on the connection via exceptions because this is how
        # windows handles these errors.

        # for te moment is_active will always be true
        while self.is_active:
            if self.is_connected:
                self.do_communications_state()
            else:
                self.try_connect_state()  # makes transition on self.is_connected when connected

    def try_connect_state(self):
        try:
            #logger.info(f"C : Connecting to : {self.computers_dict[self.ip].computer_name}({self.ip}:{self.port})"
            #            f" for agent : {self.computers_dict[self.ip].agent_name} ...")

            time.sleep(2)  # this sleep is to avoid network requests overloads
            if self.client_to_server_socket is None:
                self.client_to_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # connect is blocking with timeout exception so we jump to the exception on timeout
            self.client_to_server_socket.connect((self.ip, int(self.port)))
            #  this following line is executed only when we have effectively a connection
            self.is_connected = True
            logger.info("C : Connected !")
        except ConnectionRefusedError:
            pass
        except :
            logger.info("C : Connection error printing traceback and retrying to connect")
            traceback.print_exc()
            if self.client_to_server_socket is not None:
                self.client_to_server_socket.close()
                self.client_to_server_socket = None
            self.is_connected = False

    def do_communications_state(self):
        
        try:
            can_send = True
            while can_send:
                if self.sending_queue.qsize() != 0:
                    is_there_a_message_to_send = True
                    try:
                        message_to_send = self.sending_queue.get_nowait()
                    except queue.Empty:
                        logger.info(f"C : Queue for client {self.computers_dict[self.ip].computer_name} is Empty no message to send")
                        is_there_a_message_to_send = False
                    
                    if is_there_a_message_to_send:
                        self.client_to_server_socket.sendall(message_to_send)

        except:
            logger.info("C : Lost connection with server retrying in a moment ... ")
            logger.info("C : Quitting do_communications_state back to try_connect_state...")
            traceback.print_exc()
            if self.client_to_server_socket is not None:
                self.client_to_server_socket.close()
                self.client_to_server_socket = None
            self.is_connected = False


class MultiClientManager(QObject):
    def __init__(self, computers_dict, parent=None):
        super(MultiClientManager, self).__init__(parent)
        self.is_thread_created = False
        self.computers_dict = computers_dict
        self.client_to_server_objects = {}
        self.client_to_server_threads = {}
        self.sending_queue = {}
        self.create_client_thread_pool()
        
    def send_to_client_x(self, ip, message):
        if ip in self.sending_queue.keys() and ip in self.client_to_server_objects.keys():
            if self.client_to_server_objects[ip].is_connected:
                try:
                    self.sending_queue[ip].put_nowait(message)
                except queue.Full:
                    logger.info(f"C : Queue for client {ip} is Full can't send message")
        
    def create_client_thread_pool(self):
        for ip in self.computers_dict.keys():
            if not Tools.am_I_this_computer(ip):
                if ip not in self.sending_queue.keys():
                    self.sending_queue[ip] = queue.Queue()
                self.client_to_server_objects[ip] = ClientThreadObject(ip, self.computers_dict, self.sending_queue[ip])
                self.client_to_server_threads[ip] = QThread()
                self.client_to_server_objects[ip].moveToThread(self.client_to_server_threads[ip])
                self.client_to_server_threads[ip].started.connect(self.client_to_server_objects[ip].connect_to_server)
                self.client_to_server_threads[ip].start()
