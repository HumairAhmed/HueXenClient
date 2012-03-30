#/****************************************************************/ 
# Program:  HueXenClient
# Version:  1.0
# Date:     03/28/2012
# Website:  http://www.HumairAhmed.com
#
# Lead Developer:   Humair Ahmed 
#
# Open Source Code used:     
# The ping.py file was used and edited from the open source python ping implementaion
# from jedie / python-ping  which was forked from samuel/python-ping. You can find the
# original code on GitHub. This code has been modified to contain everything in the 
# class Ping and provide required fucntioality for this app.
#
  
# License:
# 
# Open source software being distributed under GPL license. For more information see here:
# http://www.gnu.org/copyleft/gpl.html. 
# 
# Can edit and redistribute code as long as above reference of authorship is kept within the code.
#/****************************************************************/

import XenAPI

import platform
import threading

import Pinger
import ping
from ping import Ping

import ManagedVM
from VMNetMonitorError import VMNetMonitorError


#Every ManagedVM has an associated VMNetMonitor object which monitors that VM
class VMNetMonitor():
    def __init__(self, session, vm): 
        self.__session = session       #store the session
        self.__managedVM = vm          #store the VM
        self.__missedPings = 0         #store the number of missed pings
        self.__ip = None               #store the ip address             
        self.__pinger = None           #store the Pinger object
        
        
    #detect the operating system of the VM    
    def __detectOS(self):
        return platform.system()  #returns "Linux", "Windows", "Java", or ""
        
        
    #get the IP address of this VM
    #NOTE: Currently I have this set to get the IP address of the first NIC card
    #I have not yet implemented functionality to support VMs with multiple NICS
    def __getVMIP(self):
        guestMetrics = self.__session.xenapi.VM.get_guest_metrics(self.__managedVM)
        ips = self.__session.xenapi.VM_guest_metrics.get_networks(guestMetrics).values()
        
        return ips
    
    
    #get the assoicated Pinger object for this VM
    def getPinger(self):
        return self.__pinger
    
    
    #start monitoring the VM
    def startMonitor(self):
        try:
            self.__ip = self.__getVMIP()[0]
            self.__pinger = Pinger.Pinger(self.__session, self.__managedVM, self.__ip)
            self.__pinger.start()
        except Exception:
            raise VMNetMonitorError("Error Monitoring VM")
        finally:
            pass
        
        
    #stop monitoring the VM    
    def stopMonitor(self):
        self.__pinger.stop()
        
        
        
        
    
    
