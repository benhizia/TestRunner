from logger_configuration import logger
import Parser
import collections
import Tools
import Server
import MultiClientManager
import time
import ui
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from pprint import pprint, pformat



def main():
    logger.info("###########  Starting the TestRunner programme ###########")
    logger.info('''Every instance acts as a server connecting to all the computers declared in network_def.xml file
and, at the same time as a client to all other instances. This creates a meshed network which is
robust to single server losses. Instances of TestRunner can disconnect and reconnect on the fly to
the meshed network as long as the network_def.xml is not changed ''')

    logger.info('''The Logging is prefixed with :
       'M : ' for main thread messages
       'S : ' for Server to clients messages ( there is one listening thread and one thread per client)
       "C : ' for Client to server messages (one thread per connection)
    
    ''')
    logger.info("########### end of welcome message ###########")
    computers_dict = collections.OrderedDict()
    Parser.parse_config_file(computers_dict)

    # logger.debug(pformat(computers_dict))

    app = QtWidgets.QApplication(sys.argv)
    form = ui.TestRunnerUi(computers_dict)
    form.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
