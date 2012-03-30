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
import xmlrpclib

from copy import deepcopy
import ManagedVM
from ManagedHost import ManagedHost
from LoginError import LoginError


#class ManagedXenPool represents a XenServer pool
class ManagedXenPool():
    
    def __init__(self, ip, username, password, slave): 
        self.__session = None                            #save session
        self. __session_id = None                        #save session id
        self.__vm_host_binding = None                    #used to see what VM is on what host; ManagedVM object is key to tupple of hostname and dropdown vm name string
        
        self.__filteredVMS = {}                          #dictionary of filtered powered-on VMs based on selected host
                                                         #dictionary = string name seen in drop down = ManagedVM object
                                                         
        self.__hosts = {}                                #dictionary of hosts in pool; string hostname = ManagedHost object
        
        self.__hostCount = 0                             #host count in pool             
        self.__vmCount = 0                               #vm count in pool
        
        session = XenAPI.Session("https://" + ip)        #string with ip used to create a session to the host      
        self.__setSession(session)                       #store the session
        self.__password = None


        try:
            if (slave): #if connecting to a slave host of the pool
                self.__session_id = session.slave_local_login_with_password(username, password)
            else: #connect to master host of pool
                self.__session_id = session.xenapi.login_with_password(username, password)
        except Exception:
            raise LoginError("Login Failed")
        finally:
            pass
            
        self.__password = password

        
    #finds powered on vms on host 'host' - sets __filteredVMS
    def filterByHost(self, host):
        vms = {}
        
        i = 1 
               
        for a_vm in self.__vm_host_binding.keys():           
            if(self.__vm_host_binding[a_vm][0] == host):
                vms[str(i) + ". " + self.__vm_host_binding[a_vm][1]] = a_vm 
                i += 1
            
        self.__setFilteredVMS(vms)
    
    
    def getPassword(self):
        return self.__password
    
    def setPassword(self, password):
        self.__password = password
        
    #finds hosts in pool - returns dictionary of hosts in pool and also sets self.__hosts; string hostname = ManagedHost object 
    def getHosts(self):        
        session = self.getSession()
        
        all_hosts = session.xenapi.host.get_all()
        
        for currHost in all_hosts:
            #hostName = session.xenapi.host.get_record(currHost)["name_label"]
            #what we want is hostname not "name_label" which appears in XenCenter
            hostName = session.xenapi.host.get_record(currHost)["hostname"]
            self.__hosts[hostName] = ManagedHost(session, session.xenapi.host.get_record(currHost))
        
        self.__hostCount = len(self.__hosts.keys())
        
        return self.__hosts
    
    
    #returns the # of hosts in the pool
    def getHostCount(self):
        return self.__hostCount
        
    
    #returns the session
    def getSession(self):
        return self.__session    
    

    #returns the session ID
    def getSessionID(self):
        return self.__session_id        
        
        
    #set the session
    def __setSession(self, session):
        self.__session = session
                

    #set the VMs based on selected host
    def __setFilteredVMS(self, vms):
       self.__filteredVMS = {} 
       self.__filteredVMS = vms 


    #returns the # of VMs in the pool
    def getVMCount(self):
        return self.__vmCount
         
         
    #returns hash -->  ManagedVM object is key to tupple of hostname and dropdown vm name string
    def __getVMHostBinding(self):
        return self.__vm_host_binding
    
    
    #function returns filtered vms; dictionary = string name seen in drop down = ManagedVM object
    def getFilteredVMS(self):
        return self.__filteredVMS
        
        
    #if hostFilter is true, then return hash of vm dropdown name string and ManagedVM objects based on vms on host 'theHost'  
    #function returns all vms in the pool  
    def getVMS(self):     
        session = self.getSession()
        
        the_vms = {}
        self.__vm_host_binding = {}

        vms_objs = session.xenapi.VM.get_all()
        

        i = 1
        for vm in vms_objs:  
            the_object = session.xenapi.VM.get_record(vm)
            #do not include templates and control domains
            if not(the_object["is_a_template"]) and not(the_object["is_control_domain"]):
                name = the_object["name_label"]
                
                the_host = session.xenapi.VM.get_resident_on(vm)
                mvm = ManagedVM.ManagedVM(self.getSession(), vm)
                
                if(str(the_host) != "OpaqueRef:NULL"): #if vm is not powered off
                    the_hostname = session.xenapi.host.get_hostname(the_host)
                    self.__vm_host_binding[mvm] = (the_hostname, name) #mvm object is key to hostname and vm name strings
                    
                    
                #add VM unique ID and VM name to VM dictionary; vm object is the value
                the_vms[str(i) + ". " + name] = mvm #the_object["uuid"]
                i += 1
                self.__vmCount += 1
                
        self.__setFilteredVMS(the_vms)
                                     
        return the_vms
    
    

