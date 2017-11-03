import time

class Logging:

    def logStateString(self, logStateString):
        self._dt = time.strftime("%d %b %Y", time.localtime(time.time()))
        self._logname = '/home/pi/PyIOT/logs/json/' + self._dt +'_log.txt'
        self._stateLogFile = open(self._logname, 'a')
        self._stateLogFile.write(logStateString + '\n')
        self._stateLogFile.close()



    def __init__(self):
        self._launchDate = time.strftime("%d %b %Y", time.localtime(time.time()))
        self._appLogFileName = '/home/pi/PyIOT/logs/applog/' + self._launchDate +'_applog.txt'
        self._logfile = open(self._appLogFileName, 'a')
        self._logfile.write(time.asctime( time.localtime(time.time())) + '\t' + 'App started\n')
        self._logfile.close()


