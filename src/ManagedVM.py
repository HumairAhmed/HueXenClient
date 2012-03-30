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



from copy import deepcopy

import XenAPI
import VMNetMonitor
from VMXenToolsActionError import VMXenToolsActionError
from VMActionError import VMActionError


#Encapsulates the VM so additional functionality can be added-on
class ManagedVM():
    def __init__(self, session, vm, monitorState = 0): 
        self.__session = session                                      #store session
        self.__VM = vm                                                #store vm
        self.__uuid = session.xenapi.VM.get_uuid(vm)                  #store unique VM id
        self.__monitoredVM = VMNetMonitor.VMNetMonitor(session, vm)   #store monitoredVM object
        self.__monitorState = monitorState                            #used to see if VM being monitored
        
        
    #return the encapsulated VM
    def getVM(self):
        return self.__VM
    

    #returns the VM monitor for this VM (type: VMNetMonitor)
    def getVMMonitor(self):
        return self.__monitoredVM
        
        
    #check if the VM is being monitored
    def getMonitorState(self):
        return self.__monitorState
    
    
    #toggle the monitoring state
    def toggleMonitorState(self):
        if self.__monitorState == 0:
            self.__monitorState = 1
        else:
            self.__monitorState = 0
    
        
    #shutdown the VM
    def vmCleanShutdown(self): 
        try:           
            self.__session.xenapi.Async.VM.clean_shutdown(self.__VM) 
        except Exception:
            raise VMXenToolsActionError("Error during clean shutdown of VM") 
   
        
    #start the VM    
    def startVM(self):
        try:
            self.__session.xenapi.Async.VM.start(self.__VM, False, True) #start_paused = False; force = True 
        except Exception:
            raise VMActionError("Error starting VM")   
        
        
    #hard reboot the VM    
    def hardRebootVM(self):
        try:
            self.__session.xenapi.Async.VM.hard_reboot(self.__VM)
        except Exception:
            raise VMActionError("Error hard rebooting VM")    
                    
                    
    #suspend the VM    
    def suspendVM(self):
        try:        
            self.__session.xenapi.Async.VM.suspend(self.__VM)
        except Exception:
            raise VMXenToolsActionError("Error suspending VM")        
        
        
    #resume the vVM   
    def resumeVM(self):        
        try:
            self.__session.xenapi.Async.VM.resume(self.__VM, False, True)
        except Exception:
            raise VMXenToolsActionError("Error resuming VM")          
    
    
    #create a snapshot of the VM    
    def vmCreateSnapshot(self, name):
        try:
            self.__session.xenapi.Async.VM.snapshot(self.__VM, name)
        except Exception:
            raise VMActionError("Error creating snapshot of VM")    


    #Live migration not yet implemented
    def migrateVM(self):        
      # the_host = theCurrSession.xenapi.host.get_by_name_label("")
      # theCurrSession.xenapi.Async.VM.pool_migrate(theSelVMObj, the_host, {"live": "true"})
      # print 'VM successfully migrated'
      pass
        
    
    #If a copy is made, make sure nested objects are copied appropriately    
    def __deepcopy__(self, memo):
        return ManagedVM(self.__session, deepcopy(self.__VM), self.__monitorState)

        
