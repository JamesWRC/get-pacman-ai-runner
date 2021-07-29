#!/usr/bin/python3

import multiprocessing
from psutil import virtual_memory
from uuid import getnode as get_mac
import sys
import requests
RUNNER_MIN_RAM_TO_LOG = 104857600 # Approx 100 MB of RAM per runner
class Util:
    def __init__(self):
        self.cpuCount = multiprocessing.cpu_count()             # Get num of CPUs available.
        self.availableRAM = virtual_memory().total              # Get total amount of RAM available.
        self.numRunners = self.cpuCount if self.cpuCount == 1 else self.cpuCount-1

        self.disposableRAM = self.availableRAM - self.availableRAM *0.4


        self.runnerRamDiskAmt = (self.disposableRAM / self.numRunners)   
        self.hostRamDiskAmt = (self.runnerRamDiskAmt * self.numRunners)//2

        # If the host can handle enough RAM for 0.5GB per runner
        self.canLog = self.runnerRamDiskAmt >= RUNNER_MIN_RAM_TO_LOG//2 

    def getCanLog(self):
        """
        Returns if this servers hardware is strong enough to 
        handle full logging for runners.
        """
        return self.canLog

    def getHostRamDiskAmt(self):
        """
        WARNING:    Returned value used in install script, DO NOT CHANGE.

        Returns the amount of RAM needed for a host RAM disk.
        """
        return self.bytesToMb(self.hostRamDiskAmt)

    def getRunnerRamDiskAmt(self):
        """
        Returns the amount of RAM needed for a runners RAM disk
        """
        return self.bytesToMb(self.runnerRamDiskAmt*1.001)
        

    def getNumRunners(self):
        """
        Returns the number of runers this server can support.
        """
        return self.numRunners

    def bytesToMb(self, amt):
        """
        Convert bytes to MB
        """
        return amt/1000/1000

    def getServerID(self):
        """
        Get the UUID of this server to give a unique ID for each runner.
        """
        return str(get_mac())

    def makeRequest(self, url, method, headers=None, json=None):
        """
        Request helper method to make requests using mutual authentication.
        """
        response = requests.request(method, url, headers=headers, json=json, cert=("./codebase/private.cert", "./codebase/private.key"))
        return response

    


if __name__ == "__main__":
    # Used to create the RAMDisk for the host in the install.sh script.
    util = Util()
    if len(sys.argv) > 1:
        if sys.argv[1] == "getHostRamDisk":
            print(int(util.getHostRamDiskAmt()))
        elif sys.argv[1] == "getRunnerRamDisk":
            print(int(util.getRunnerRamDiskAmt()))





