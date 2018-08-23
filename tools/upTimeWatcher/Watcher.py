#!/usr/bin/python

import re
import os
import json
import subprocess
import time
import io
import datetime

statusReg = r"^Host:\s*(?P<ip>[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3})\s*\((?P<hostName>.*)\)\s*Status:\s*(?P<status>.*)$"
portsReg = r"^Host:\s*(?P<ip>[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3})\s*\((?P<hostName>.*)\)\s*Ports:\s*((?P<port>[0-9]*)/(?P<pStatus>[a-z]*)/(?P<tProto>[a-z]*)//(?P<aProto>[a-z]*)///,?\s?)+$"

def parse(inFile, outFile = 'out.json'):
    '''Parse nmap output to be stored in json format.

    Turns nmap output stored in file to a json formatted list of ip addresses.

    Note:
        nmap should be run as 'nmap -sS -p 3632 -oG - ' followed by a list of ip addresses.

    Args:
        inFile (str): path to file with output of nmap.
        outFile (str, optional): path to file for parsed data storage.
            Default: 'out.json'

    Returns:
        None
    '''
    hosts = []
    with open(inFile, "r") as data:
        host = {}

        for item in data:
            if not host:
                status = re.match(statusReg, item)
                if status:
                    host = status.groupdict()
                continue

            if host:
                if host['status'] == 'Up':
                    ports = re.match(portsReg, item)
                    if ports:
                        ports = ports.groupdict()
                        if ports['ip'] == host['ip'] and ports['hostName'] == host['hostName']:
                            host.update(ports)
                hosts.append(host)
                host = {}

    with open(outFile, "w") as out:
        out.write(json.dumps(hosts, indent=2, separators=(',', ':')))

class Host:
    ''' Statistic storage for a single host

    This class represents a storage of basic information about a host to be observed.
    It provides basic functionality for the stored information to be human readable formated

    Note:
        Each attribute not mentioned in 'Attributes' section is updated automatically and therefore must not be changed with someone's dirty hands.

    Attributes:
        saveToFile (bool): defines whether logs should be stored to file.
        logStorage (string): directory for storage logfiles of specific hosts (filename will be generated automatically)

    Args:
        hostParams (:obj: dict, string ,optional): basic parameters for host to be initialised.
            Can be  omitted if there is no any data available initially.
            If string is provided, it will be considered as an ip address
            If dictionary is provided, all the provided parameters will be used and the format should be as follows:
                'ip': ip-address of host
                'hostName': hostname of host
                'status': current host status
                'aProto': application leyer protocol to be considered
                'tProto': transport layer protocol to be considered
                'port': port to be observed (mostly defines aProto)
                'pStatus': status of observed port
    '''
    def __init__(self, hostParams = None):
        if not isinstance(hostParams, dict) or hostParams == None:
            hostParams = {
                'ip': "" if hostParams == None else hostParams,
                'hostName': "",
                'status': "Down",
                'aProto': "",
                'tProto': "",
                'port': "",
                'pStatus': ""
            }
        self.ip = hostParams['ip']

        self.hostName = hostParams['hostName']
        self.status = hostParams['status']
        self.applicationProtocol = hostParams['aProto']
        self.transportProtocol = hostParams['tProto']
        self.port = hostParams['port']
        self.portStatus = hostParams['pStatus']

        self.saveToFile = False
        self.logStorage = ''

        self.watchStart = time.time()

        self.upTime = []
        if self.status == 'Up':
            self.upTime.append(self.watchStart)

        self.pUpTime = []
        if self.portStatus == 'open':
            self.pUpTime.append(self.watchStart)

        self.lastUpdate = self.watchStart

        self.log('Host ' + self.hostName + ':' + self.ip + ' initialized. Status: ' + self.status)

    def update(self, params):
        '''Listens to updates of host information.

        Watch the updates provided by external application. In case of new one, one of the following actions will be performed:
            1) update host info - if host is empty (initialization failed since not enough data was provided) all the provided info regarding certain host will be stored
            2) update uptime and log update - if state of host or protocol has changes, new state should be stored and changes has to be logged
            3) skip update - if nothing new happend (status of host remains the same)

        Args:
            params: distionary with update info of the following format:
                'ip': ip-address of host
                'hostName': hostname of host
                'status': current host status
                'aProto': application leyer protocol to be considered
                'tProto': transport layer protocol to be considered
                'port': port to be observed (mostly defines aProto)
                'pStatus': status of observed port

        Return:
            None
        '''
        self.lastUpdate = time.time()

        if not self.hostName and params['hostName']:
            self.hostName = params['hostName']
            self.applicationProtocol = params['aProto']
            self.transportProtocol = params['tProto']
            self.port = params['port']

        if self.status != params['status']:
            self.upTime.append(self.lastUpdate)
            self.status = params['status']
            self.log('Host ' + self.hostName + ':' + self.ip + ' changed its status. Status: ' + self.status)

        if self.portStatus != params['pStatus']:
            self.pUpTime.append(self.lastUpdate)
            self.portStatus = params['pStatus']
            self.log('Host ' + self.hostName + ':' + self.ip + ' updated. Port status: ' + self.portStatus)


    def singleLineStat(self):
        '''Gives instantaneous statistic of a host

        Gethers basic statistic of a certain host: ip, hostname, host uptime and protocol uptime.
        The format is following:
            'Host: <hostname>; ip <ip>; Host UpTime: <uptime> of overall watch time: <overallWorkTime>; Proto UpTime: <uptime> of overall watch time: <overallWorkTime>.'

        Args:
            None

        Returns:
            str: host statistic.
        '''
        hostUpTime = self.getUpTime(self.upTime)
        protoUpTime = self.getUpTime(self.pUpTime)
        logLine = 'Host: ' + self.hostName + '; ip: ' + self.ip + '; ' + \
        'Host UpTime: ' + str(hostUpTime[0]) + ' of overall watch time: ' + str(hostUpTime[1]) + '; ' + \
        'Proto UpTime: ' + str(protoUpTime[0]) + ' of overall watch time: ' + str(protoUpTime[1]) + '.'
        return logLine

    def getUpTime(self, upTimeList):
        '''Calculates full uptime of host and a specific protocol.

        Calculates overall uptime based on a list of timestamps represented by upTimeList.
        Each timestamp with even index (0,2,4...) is considered as moment of rising up and vice-versa
        (each timestamp with odd index (1,3,5...) is considered as moment of shutting down).
        Uptime calculation does not depends on watched subject, so it could be port (specific protocol), host etc.

        Note:
            If number of timestamps is odd, current time will be taken as a last one.

        Args:
            upTimeList (list<float>): list of timestamps.

        Returns:
            tuple(datetime.timedelta, datetime.timedelta): First one stands for uptime and the second one is for overall observation time.
        '''
        upTime = 0
        if len(upTimeList) == 1:
            upTime = int(time.time() - upTimeList[0])
        elif len(upTimeList) > 1:
            for i in range(len(upTimeList))[1:]:
                if i%2 == 0:
                    upTime += upTimeList[i] - upTimeList[i-1]
            if len(upTimeList)%2:
                upTime += int(time.time() - upTimeList[-1])
        return (datetime.timedelta(seconds=int(upTime)), datetime.timedelta(seconds=int(time.time() - self.watchStart)))

    def log(self, message):
        '''Writes message to stdout and (if configured) to file.

        Message to be logged will be written to stdout and if it's configured to a file
        named by 'hostLog_' prefix followed by ip and hostname of observable host.

        Args:
            message (str): Message to be logged in.

        Returns:
            None.

        Raises:
            IOError: An error occured accessing logfile, if enabled.
        '''
        message = datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y') + '>>' + message
        print message
        if self.saveToFile:
            fName = os.path.join(self.logStorage, 'hostLog_%s_%s.log'%(self.hostName, self.ip))
            with open(fName, 'a') as logFile:
                logFile.write(message + '\n')

class Watcher:
    '''
    Watcher for observation of hosts status and status of a specific port on each one.

    Note:
        Each attribute not mentioned in 'Attributes' section is updated automatically and therefore must not be changed with someone's dirty hands.

    Attributes:
        updateInterval (int): number of seconds between nmap running.
            Default: 5
        logUpdateInterval (int): number of secconds between writing statistic to file.
            Default: 30
        logFileName (str): namee of file to store log.
            Default: 'log.log'

    Args:
        ips_filename (str): name of .json file with stored information of observed hosts.
    '''
    def __init__(self, ips_filename):
        self.ipsToWatch = self.getIpsToCheck(ips_filename)
        self.logFileName = 'log.log'

        self.hosts = []

        self.startTime = 0
        self.updateInterval = 5
        self.logUpdateInterval = 30

        self.nmap(init=True)
        for item in self.ipsToWatch:
            if next((host for host in self.hosts if host.ip == item), -1) == -1:
                self.hosts.append(Host(item))

    def getIpsToCheck(self, filename):
        '''Gets list of ip addresses ready for nmap.

        Nmap output parsed to json format should be used as initial data file.
        But actually, its enough to have following format:
            [
                {
                    'ip': '127.0.0.1'
                },
                .
                .
                .
            ]

        Args:
            filename (str): name of file with parsed nmap output.

        Returns:
            str: space separated list of ip addresses
        '''
        with io.open(filename, encoding='utf-8') as data:
            net = json.load(data)

        ip_list = []
        for item in net:
            if not item['ip'] == "" and not item['ip'] in ip_list:
                ip_list.append(item['ip'])

        return ip_list

    def run(self):
        '''Runs main application loop

        Main workflow includes collection of nmap data, updating host information and data storage to a log file.
        Update intervals are configurable.

        Args:
            None.

        Return:
            None.
        '''
        updateMonitor = 0
        logDumpMonitor = 0
        while True:
            if updateMonitor >= self.updateInterval:
                print 'Nmap running...'
                self.nmap()
                print 'Nmap finished!'
                updateMonitor = 0
            if logDumpMonitor >= self.logUpdateInterval:
                print 'Logging to file...'
                self.writeLog()
                print 'Log file is updated!'
                logDumpMonitor = 0
            updateMonitor += 1
            logDumpMonitor += 1
            time.sleep(1)

    def nmap(self, init=False):
        '''Monitors nmap output.

        Runs nmap and updating statistic.

        Args:
            init(bool): whether ran in initialisation mode. If true, host list will be updated,
                otherwise, host will updated.

        Returns:
            None.

        Raise:
            KeyError: If host cannot be found in list of observable hosts by ip address
            NameError: If host and port status messages do not corresponds. Recheck nmap output.
        '''
        host = {}
        for line in self.nmapRun():
            statusMatch = re.match(statusReg, line)
            if statusMatch:
                host = statusMatch.groupdict()
                continue
            portsMatch = re.match(portsReg, line)
            if portsMatch:
                ports = portsMatch.groupdict()
                if host and ports['ip'] == host['ip'] and ports['hostName'] == host['hostName']:
                    host.update(portsMatch.groupdict())
                    if init:
                        self.hosts.append(Host(host))
                    else:
                        ind = next((i for i, item in enumerate(self.hosts) if item.ip == host['ip']), -1)
                        if ind == -1:
                            raise KeyError("Can't find element")
                        self.hosts[ind].update(host)
                else:
                    raise NameError("Unknown host status " + ports['ip'])

    def nmapRun(self):
        '''Generator for nmap output processing.

        Runs nmap application and watch it's output string by string.

        Args:
            None.

        Yields:
            str: Single nmap output line.
        '''
        ips = ' '.join(self.ipsToWatch)
        cmd = "nmap -sS -p 3632 -oG - " + ips
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        while True:
            line = process.stdout.readline()
            if not line:
                break
            yield line

    def writeLog(self):
        '''Writes generated log to a file.

        Args:
            None.

        Returns:
            None.

        Raises:
            IOError: An error occured accessing logfile.
        '''
        log = self.generateLog()
        with open(self.logFileName, 'w') as dataOut:
            dataOut.write('\n'.join(log))

    def generateLog(self):
        '''Gethers log from all of the observable hosts

        Args:
            None

        Returns:
            list<str>: list with hosts statistic
        '''
        log = []
        for host in self.hosts:
            log.append(host.singleLineStat())
        return log

def main():
    watcher = Watcher('ipList.json')
    watcher.run()

if __name__ == '__main__':
    main()