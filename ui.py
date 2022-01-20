from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import mainwindowUI
from logger_configuration import logger
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer, QObject
import traceback
import MultiClientManager
import Server
import Tools
import functools
import testrunner_pb2
import psutil


class TestRunnerUi(QtWidgets.QMainWindow, mainwindowUI.Ui_MainWindow):
    def __init__(self, computers_dict, parent=None):
        super(TestRunnerUi, self).__init__(parent)
        self.setupUi(self)
        self.computers_dict = computers_dict

        self.icon_connected = QtGui.QIcon()
        self.icon_disconnected = QtGui.QIcon()
        self.icon_disconnected.addPixmap(QtGui.QPixmap("icons/Disconnected.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.icon_connected.addPixmap(QtGui.QPixmap("icons/connected.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        self.SendMessageBtn.setEnabled(True)
        self.SendMessageBtn.clicked.connect(self.send_print_msg_MSG)
        # creating a server instance (it's a QObject to be able to connect with signal slots to this UI)
        self.server_instance = Server.Server(self.computers_dict)

        # Connecting events from the Server to their generated effects in the GUI
        self.server_instance.client_connected_sig.connect(self.set_icon)
        self.server_instance.client_disconnected_sig.connect(self.set_icon)
        self.server_instance.client_disconnected_sig.connect(self.remove_client_widgets)
        
        self.multi_client_manager = MultiClientManager.MultiClientManager(self.computers_dict)
        
        #processes we don't care about to see them
        self.filtered_process_names = ["conhost.exe", "svchost.exe", "csrss.exe", "winlogon.exe", "system", 
                                       "runtimebroker.exe", "spoolsv.exe", "smss.exe", "lsass.exe", "wininit.exe",
                                       "lsalso.exe", "services.exe"]        
        
        self.hearbeat_timer_obj = HeartBeatTimer(self.filtered_process_names, time_out=3000)
        self.thread_heartbeat = QThread()
        self.hearbeat_timer_obj.moveToThread(self.thread_heartbeat)
        self.thread_heartbeat.started.connect(self.hearbeat_timer_obj.fill_protobuf_Heartbeat_MSG)
        self.thread_heartbeat.start()
        
        self.gui_polling_timer = QTimer()
        self.gui_polling_timer.timeout.connect(self.receive_message_from_clients)
        self.gui_polling_timer.start(200)
        
        self.send_HB_message_timer = QTimer()
        self.send_HB_message_timer.timeout.connect(self.send_protobuf_to_all_clients)
        self.send_HB_message_timer.start(6000)        

        self.SendKillProcessBtn.pressed.connect(self.send_kill_process_MSG)
        self.SendRunProcessBtn.pressed.connect(self.send_run_process_MSG)
        self.locally_run_processes = {}
        
        #setting icon management
        self.computer_to_widget_item = {}
        self.computer_to_widget_item_process = {}
        
        #hiding the treeWidgetProcess used as template from gui to recover its positions (geometry)
        self.treeWidgetProcess.hide()
        self.treeWidgetProcessAllComputers = {}
        self.treeWidgetComputers.itemClicked.connect(self.show_computer_processes)
        self.treeWidgetComputers.setHeaderLabels(["ComputerName", "Agent", "Memory %", "CPU %"])
        self.treeWidgetComputers.setAlternatingRowColors(True)
        self.treeWidgetComputers.setSortingEnabled(True)
        for ip in self.computers_dict.keys():
            if not Tools.am_I_this_computer(ip):
                computer_data = self.computers_dict[ip]
                item = QtWidgets.QTreeWidgetItem()
                item.setIcon(0, self.icon_disconnected)
                item.setText(0, f"{computer_data.computer_name}")
                item.setText(1, f"{computer_data.agent_name}")
                
                self.treeWidgetComputers.insertTopLevelItem(0, item)
                self.computer_to_widget_item[ip] = item
                
                self.treeWidgetProcessAllComputers[ip] = QtWidgets.QTreeWidget(self.system_tab)
                self.treeWidgetProcessAllComputers[ip].setGeometry(self.treeWidgetProcess.geometry())
                self.treeWidgetProcessAllComputers[ip].setObjectName(f"treeWidgetComputersProcess{ip}")
                self.treeWidgetProcessAllComputers[ip].setHeaderLabels(["PID", "Name", "Memory(MB)", "Command Line"])
                self.treeWidgetProcessAllComputers[ip].setAlternatingRowColors(True)
                self.treeWidgetProcessAllComputers[ip].setSortingEnabled(True)
                self.treeWidgetProcessAllComputers[ip].hide()
                
                # we init this dict to empty dict for it to be automatically populated with its ip keys.
                self.computer_to_widget_item_process[ip] = {}
                
    @pyqtSlot()
    def show_computer_processes(self):
        selected_items = self.treeWidgetComputers.selectedItems()
        ip_list = self._get_ip_list_from_list_widget(selected_items)  # desormais on a qu'un pc selectionnable à la fois.
        
        for item in self.treeWidgetProcessAllComputers.keys():
            self.treeWidgetProcessAllComputers[item].hide()
            
        self.treeWidgetProcessAllComputers[ip_list[0]].show()
        self.SelectedMachineLbl.setText(self.computers_dict[ip_list[0]].computer_name)
        
        
    @pyqtSlot(str)
    def set_icon(self, ip):
        if ip in self.computers_dict.keys():
            item = self.computer_to_widget_item[ip]
            if ip in self.server_instance.server_to_clients_sockets.keys():
                item.setIcon(0, self.icon_connected)
            else:
                item.setIcon(0, self.icon_disconnected)
    
    @pyqtSlot(str)
    def remove_client_widgets(self, ip):
        self.treeWidgetProcessAllComputers[ip].clear()
        self.computer_to_widget_item_process[ip].clear()

    def _get_ip_list_from_list_widget(self, list_widgets):
        """
        this function can be optimized to a static dict with the object as key
        """
        ip_list = []
        for item in list_widgets:
            for ip in self.computer_to_widget_item.keys():
                if self.computer_to_widget_item[ip] == item:
                    ip_list.append(ip)
        return ip_list
    
    @pyqtSlot()
    def receive_message_from_clients(self):
            for ip in self.computers_dict.keys():
                client_x_messages = self.server_instance.get_client_message_queue(ip)
               
                if client_x_messages is not None:
                    while client_x_messages.qsize() != 0:
                        received_message = client_x_messages.get_nowait()
                        try:
                            testrunner_protocol_obj = testrunner_pb2.TestRunnerProtocol()
                            testrunner_protocol_obj.ParseFromString(received_message)
                        except Exception as e:
                            logger.info(f"Exeption While deserializing protobuf !:{e}")
                            
                        which_oneof = testrunner_protocol_obj.WhichOneof("OneOfSwitchSubMessage")

                        if which_oneof == "HB":
                            self.handle_heartbeat_MSG(testrunner_protocol_obj, ip)
                        if which_oneof == "print_msg":
                            self.handle_print_msg_MSG(testrunner_protocol_obj, ip)
                        if which_oneof == "run_process":
                            self.handle_run_process_MSG(testrunner_protocol_obj, ip)
                        if which_oneof == "kill_process":
                            self.handle_kill_process_MSG(testrunner_protocol_obj, ip)

    def handle_heartbeat_MSG(self, protocol_obj, ip):
        if ip in self.computer_to_widget_item.keys():
            memory = Tools.truncate(protocol_obj.HB.machine_used_memory_percent, 2)
            cpu = Tools.truncate(protocol_obj.HB.machine_used_cpu_percent, 2)
            self.computer_to_widget_item[ip].setData(2, QtCore.Qt.DisplayRole, memory)
            self.computer_to_widget_item[ip].setData(3, QtCore.Qt.DisplayRole, cpu)

        for existing_pid in list(self.computer_to_widget_item_process[ip].keys()):
            is_pid_out_of_date = True
            for process in protocol_obj.HB.process_list:
                new_pid = process.process_id
                if existing_pid == new_pid:
                    is_pid_out_of_date = False
                    break
            if is_pid_out_of_date:
                idx = self.treeWidgetProcessAllComputers[ip].indexOfTopLevelItem(self.computer_to_widget_item_process[ip][existing_pid])                
                self.treeWidgetProcessAllComputers[ip].takeTopLevelItem(idx)
                del self.computer_to_widget_item_process[ip][existing_pid]

        for process in protocol_obj.HB.process_list:
            if process.process_name.lower() in self.filtered_process_names:
                continue
            pid = process.process_id
            memory_mb = process.process_memory_bytes / (1024 * 1024)  # in MB
            if pid not in self.computer_to_widget_item_process[ip].keys():
                item = QtWidgets.QTreeWidgetItem()
                item.setData(0, QtCore.Qt.DisplayRole, process.process_id)
                item.setText(1, f"{process.process_name}")
                item.setData(2, QtCore.Qt.DisplayRole, Tools.truncate(memory_mb, 2))
                item.setText(3, f"{process.process_cmdline}")
                self.treeWidgetProcessAllComputers[ip].insertTopLevelItem(0, item)
                self.computer_to_widget_item_process[ip][pid] = item
            else:  # updating existing widget with the new data about memory and CPU
                item = self.computer_to_widget_item_process[ip][pid]
                item.setData(2, QtCore.Qt.DisplayRole, Tools.truncate(memory_mb, 2))


        # benchmarking code
        # import timeit
        # start = timeit.default_timer()
        # time_diff = timeit.default_timer() - start
        # print (f"Took : {time_diff } s")

    @staticmethod
    def _make_unique_dict_key(process_id, process_name):
        return f"{process_id} : {process_name}"
    
    @staticmethod
    def _decode_key(key):
        return key.split(" : ")

    def handle_print_msg_MSG(self, protocol_obj, ip):
        self.MessageRecv.setText(f"received from {ip} {protocol_obj.print_msg.message_to_print}")
        
    def handle_run_process_MSG(self, protocol_obj, ip):
        logger.info(f"Running {protocol_obj.run_process.process_path} ...")
        try:
            proc = psutil.Popen(protocol_obj.run_process.process_path)
            self.locally_run_processes[proc.pid] = proc
        except Exception as e:
            logger.info(f"Exception ! : {e} ")

    def handle_kill_process_MSG(self, protocol_obj, ip):        
        logger.info(f"Killing process_pid{protocol_obj.kill_process.process_pid} ...")
        try:
            process = psutil.Process(protocol_obj.kill_process.process_pid)
            if process.pid in self.locally_run_processes.keys():
                del self.locally_run_processes[process.pid]
            process.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
                logger.info(f"NoSuchProcess or AccessDenied for pid {protocol_obj.kill_process.process_pid}")
        
    @pyqtSlot()
    def send_print_msg_MSG (self):
        msg = testrunner_pb2.TestRunnerProtocol()
        msg.print_msg.message_to_print = self.textEdit.toPlainText()
        self.send_protobuf_to_selected_clients(msg)
        
    def send_protobuf_to_selected_clients(self, msg):
        logger.info(f"Sending protobuf : {msg}")
        selected_computers = self.treeWidgetComputers.selectedItems()
        ip_list = self._get_ip_list_from_list_widget(selected_computers)
        logger.info(f"selected_computers :{ip_list}")
        if ip_list is not None:
            for ip in ip_list:
                self.multi_client_manager.send_to_client_x(ip, msg.SerializeToString())

    @pyqtSlot()
    def send_protobuf_to_all_clients(self):
        for ip in self.computers_dict.keys():
            self.multi_client_manager.send_to_client_x(ip, self.hearbeat_timer_obj.get_protobuf_HB_msg().SerializeToString())
            
    @pyqtSlot()
    def send_kill_process_MSG(self):
        
        selected_computers = self.treeWidgetComputers.selectedItems()
        ip_list = self._get_ip_list_from_list_widget(selected_computers)
        logger.info(f"selected_computers :{ip_list}")
        
        if ip_list is not None and len (ip_list) == 1:
            selected_processes = self.treeWidgetProcessAllComputers[ip_list[0]].selectedItems()
        if selected_processes is not None:
            for item in selected_processes:
                msg = testrunner_pb2.TestRunnerProtocol()
                msg.kill_process.process_pid = int(item.text(0))
                self.send_protobuf_to_selected_clients(msg)
                
    @pyqtSlot()
    def send_run_process_MSG(self):            
        msg = testrunner_pb2.TestRunnerProtocol()
        msg.run_process.process_path = self.RunProcessTextEdit.toPlainText()
        self.send_protobuf_to_selected_clients(msg)
        

class HeartBeatTimer(QObject):
    """
    this  class is used to run into a thread the getting of the process list because it takes time
    @param: filtered_process_names : list of unwanted process names to not send because irrelevent.
    """    
    def __init__(self, filtered_process_names, time_out, parent=None):
        super(HeartBeatTimer, self).__init__(parent)
        self.filtered_process_names = filtered_process_names
        self.HeartBeatTimer = QTimer()
        self.HeartBeatTimer.setInterval(time_out)
        self.HeartBeatTimer.timeout.connect(self.fill_protobuf_Heartbeat_MSG)
        self.protobuf_HB_msg = testrunner_pb2.TestRunnerProtocol()
        self.HeartBeatTimer.start()
        
    def get_protobuf_HB_msg(self):
        return self.protobuf_HB_msg

    @pyqtSlot()
    def fill_protobuf_Heartbeat_MSG(self):
        self.protobuf_HB_msg.Clear()
        self.protobuf_HB_msg.HB.heart_beat_id = 1 #cet id ne sert à rien mais ça fait du bien d'en avoir un ...
        self.protobuf_HB_msg.HB.machine_used_memory_percent = psutil.virtual_memory().percent
        self.protobuf_HB_msg.HB.machine_used_cpu_percent = psutil.cpu_percent()
        
        # Iterate over all running process
        for proc in psutil.process_iter(attrs=["pid", "name", "cmdline", "memory_info"]):
            try:
                if proc.name().lower() in self.filtered_process_names:
                    continue
                
                #creating a new entry in the repeated protobuf message structure
                process_item = self.protobuf_HB_msg.HB.process_list.add()
                # Get process name & pid from process object.
                process_item.process_name = proc.name()
                process_item.process_id = proc.pid
                cmd_line = proc.cmdline()
                cmd_line_str = " ".join(cmd_line)
                process_item.process_cmdline = cmd_line_str                
                process_item.process_memory_bytes = proc.memory_info().rss

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
