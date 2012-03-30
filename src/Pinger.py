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

import threading
import subprocess
import warnings
warnings.filterwarnings('ignore', '.*')
import sys
import time
import os

#used to create hash for threads
#get_ident - gets thread identifier of the current thread
try: 
    from thread import get_ident 
except ImportError: 
    try: 
        from _thread import get_ident 
    except ImportError: 
        def get_ident(): 
            return 0 


import ping
from ping import Ping
import ManagedVM


#every VMNetMonitor has a Pinger object for managing its pings
class Pinger(threading.Thread):
    pingerCount = 0  
    error_occurred = False

    def __init__(self, session, vm, ip): 
        lock = threading.Lock()
        with lock: 
            threading.Thread.__init__(self)
            Pinger.pingerCount = Pinger.pingerCount + 1                 #pinger count - also used in VM unique has algorithm
         
            self.__stopPings = 0;                                       #stop pings toggle
            self.__session = session                                    #save session
            self.__VM = vm                                              #save vm being monitored
            self._id = (get_ident() ^ os.getpid()) + Pinger.pingerCount #create a unique hash for the VM - needed for ICMP pings

            self.__ip = ip                                              #save ip 
            self.__missedPings = 0                                      #number of missed pings
            self.__pingObj = Ping(ip, 1000, 55, self._id)               #create Ping object
            self.__snapped = 0                                          #toggle for if snapshot has already occurred
            self.misses = 2                                             #number of missed pings allowed
       
                  
    #stop pinging
    def stop(self):
        lock = threading.Lock()
        with lock: 
            self.__stopPings = 1            
                
            
    #ping function - starts the Ping object thread which starts pinging the VM and reporting results
    def ping(self): 
        lock = threading.Lock()
        with lock:  
            i = 0
            #keep pinging until told to stop or snapshot gets created due to missing pings
            while(self.__stopPings == 0 and self.snapped == 0):
                #get missed pings- hopefully 0
                self.__missedPings = self.__pingObj.run(self.misses) 
                time.sleep(5) #wait 5 seconds - let's not go overboard
                i = i + 1
                
                #if threshold for missed pings is hit, create a snapshot
                if self.__missedPings == self.misses:
                    if self.snapped == 0:
                        self.__session.xenapi.Async.VM.snapshot(self.__VM, "Network_Down") # create a snapshot
                        self.snapped = 1
                                       

    #initialize variables for thread object
    def run(self): 
        lock = threading.Lock()
        with lock:  
            self.__stopPings = 0
            self.__missedPings = 0
            self.snapped = 0
        
            self.ping() #start pingign
        