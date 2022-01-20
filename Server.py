import socket
import sys
import traceback
import Tools
from logger_configuration import logger
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
import queue
import functools

class AcceptingConnectionsThread(QObject):
    client_connected_sig = pyqtSignal(str)
    
    def __init__(self, computers_dict, server_to_clients_sockets, parent=None):
        super(AcceptingConnectionsThread, self).__init__(parent)
        self.computers_dict = computers_dict
        self.spawn_client_thread = False
        self.server_to_clients_sockets = server_to_clients_sockets
        port = 32000  # arbitrary non-privileged port
        self.srv_accepting_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP Socket
        # SO_REUSEADDR flag tells the kernel to reuse a local
        # socket in TIME_WAIT state, without waiting for its
        # natural timeout to expire
        self.srv_accepting_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger.info("S : Listening Socket created")
        try:
            self.srv_accepting_soc.bind(("", port))
        except:
            logger.info("S : Bind failed. Error : " + str(sys.exc_info()))
            traceback.print_exc()
            sys.exit()

    def __del__(self):
        self.srv_accepting_soc.close()

    @pyqtSlot()
    def start_listening_loop(self):
        # infinite listening loop
        while True:
            logger.info("S : Socket now listening")
            # Number of buffered connection rqsts (if all clients try to connect at the same time)
            nbr_of_simultaneous_conn = len(self.computers_dict) - 1
            self.srv_accepting_soc.listen(nbr_of_simultaneous_conn)
            # /!\ Blocking call /!\
            client_socket, address = self.srv_accepting_soc.accept()  # /!\accept returns only when a client connects/!\
            # /!\ Blocking call /!\
            ip, port = str(address[0]), str(address[1])
            distant_hostname = socket.gethostbyaddr(ip)[0]
            logger.info(f"S : Client {distant_hostname}({ip}:{port}) is trying to connect checking for authorization ...")
            if self._is_computer_known(ip) and not Tools.am_I_this_computer(ip):
                # cleaning up data structure if connection was lost before registering the new socket
                self._cleaning_old_socket(ip)
                self.server_to_clients_sockets[ip] = client_socket
                self.client_connected_sig.emit(ip)
                logger.info(f"S : OK")
            else:
                logger.info(
                    f"S : Client {distant_hostname}({ip}): not found in network_def.xml closing socket ...")
                client_socket.close()

    @pyqtSlot(str)
    def _cleaning_old_socket(self, ip):
        """
            if client already in management and not well cleansed when the connection was lost. Or double instance which
            should/will be forbidden.
        :param ip: client ip address to check for existence
        """
        if ip in self.server_to_clients_sockets.keys():  # the keys are the ip addresses
            logger.info(
                f"S : ip address already in server_to_clients_sockets dictionary closing old corresponding"
                f"socket before registering the new one ...")
            self.server_to_clients_sockets[ip].close()
            del self.server_to_clients_sockets[ip]

    def _is_computer_known(self, ip):
        for key in self.computers_dict:
            if ip == self.computers_dict[key].ip:
                return True
        return False


class ClientManagementThread(QObject):
    client_disconnected_sig = pyqtSignal(str)

    def __init__(self, server_to_clients_sockets,  handled_client_ip, parent=None):
        super(ClientManagementThread, self).__init__(parent)
        self.received_messages_queue = queue.Queue(maxsize=0)  # infinite size queue
        self.server_to_clients_sockets = server_to_clients_sockets
        self.this_client_ip = handled_client_ip
        self.is_active = False

    def get_messages_queue(self):
        return self.received_messages_queue

    @pyqtSlot()
    def manage_client(self):
        max_buffer_size = 10000
        self.is_active = True
        while self.is_active:
            try:
                if self.this_client_ip in self.server_to_clients_sockets.keys():
                    client_input = self._receive_input(self.server_to_clients_sockets[self.this_client_ip], max_buffer_size)
                    if client_input is not None:
                        try:
                            self.received_messages_queue.put_nowait(client_input)
                            # this line adds coupling between HMI event loops and data reception which is a base idea
                            # we need to use a pooling mechanism to make the hmi smooth
                            #  self.client_x_messages_received.emit(self.this_client_ip)
                        except queue.Full:
                            logger.info(f"S : Client sending a message while last message not yet processed !"
                                        f" the new message is dropped")
            except:
                hostname = socket.gethostbyaddr(self.this_client_ip)[0]
                logger.info(f"S : Connection lost with client {hostname}({self.this_client_ip}) thread quitting ...")
                traceback.print_exc()
                if self.this_client_ip in self.server_to_clients_sockets.keys():
                    self.server_to_clients_sockets[self.this_client_ip].close()
                    del self.server_to_clients_sockets[self.this_client_ip]
                else:
                    logger.info(f"S : Exception : Key {self.this_client_ip} not found int dict server_to_clients_sockets")
                self.client_disconnected_sig.emit(self.this_client_ip)
                self.is_active = False

    def _receive_input(self, connection, max_buffer_size):
        """
        This methode needs to manage the case where recv returns splitted chunks when reading 
        we must always try to read a fixed size?
        """
        client_input = connection.recv(max_buffer_size)  # blocking call released when at least one byte received
        client_input_size = sys.getsizeof(client_input)

        if client_input_size > max_buffer_size:
            logger.info(
                f"S : The input size is greater than expected, received {client_input_size} > {max_buffer_size}")
            
        return client_input 


class Server(QObject):
    client_disconnected_sig = pyqtSignal(str)
    client_connected_sig = pyqtSignal(str)

    def __init__(self, computers_dict, parent=None):
        super(Server, self).__init__(parent)
        self.computers_dict = computers_dict
        self.server_to_clients_sockets = {}
        self.server_to_clients_threads = {}
        self.server_to_clients_objects = {}
        # At Server creation we instantiate a new thread listening and accepting connections
        # When a client connects the listening thread calls create_client_thread() to spawn a handler thread for the
        # corresponding client
        self.listening_object = AcceptingConnectionsThread(self.computers_dict, self.server_to_clients_sockets)
        self.listening_thread = QThread()
        self.listening_object.moveToThread(self.listening_thread)
        self.listening_thread.started.connect(self.listening_object.start_listening_loop)
        # Connecting client connected event to the client thread factory code (ip is the param)
        self.listening_object.client_connected_sig.connect(self.create_client_handler_thread)
        self.listening_object.client_connected_sig.connect(self.client_connected_sig)
        
        # Starting the listening thread to accept new connections asynchronously
        self.listening_thread.start()

    @pyqtSlot(str)
    def create_client_handler_thread(self, ip):
        self.server_to_clients_objects[ip] = ClientManagementThread(self.server_to_clients_sockets, ip)
        try:
            self.server_to_clients_threads[ip] = QThread()
            self.server_to_clients_objects[ip].moveToThread(self.server_to_clients_threads[ip])
            # connecting signal to signal is possible, useful to communicate with GUI from a not yet existing client
            # object
            self.server_to_clients_objects[ip].client_disconnected_sig.connect(self.client_disconnected_sig)
            self.server_to_clients_objects[ip].client_disconnected_sig.connect(self._cleaning_old_data)

            self.server_to_clients_threads[ip].started.connect(self.server_to_clients_objects[ip].manage_client)
            self.server_to_clients_threads[ip].start()
        except:
            logger.info("S : QThread did not start.")
            traceback.print_exc()
            self._cleaning_old_data()
            
    @pyqtSlot(str)
    def _cleaning_old_data(self, ip):
        """
            if client already in management and not well cleansed when the connection was lost. Or double instance which
            should/will be forbidden.
        :param ip: client ip address to check for existence
        """

        if ip in self.server_to_clients_objects.keys():
            del self.server_to_clients_objects[ip]
        if ip in self.server_to_clients_threads.keys():
            logger.warning(f"S : Client : {ip} disconnected cleaning list of handled client threads ")
            self.server_to_clients_threads[ip].terminate()
            del self.server_to_clients_threads[ip]

    def get_client_message_queue(self, ip):
        if ip in self.server_to_clients_objects.keys():
            return self.server_to_clients_objects[ip].get_messages_queue()
