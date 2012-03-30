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


title = 'HueXenClient'

import re
# Import Pmw from this directory tree.
import sys
sys.path[:0] = ['../../..']

from Tkinter import *
import Tkinter
import tkMessageBox
import Pmw
import os
import math
import string

import XenAPI
from ManagedXenPool import ManagedXenPool
import ManagedVM
import VMNetMonitor
from LoginError import LoginError
from VMNetMonitorError import VMNetMonitorError
from VMXenToolsActionError import VMXenToolsActionError
from VMActionError import VMActionError


#Main window - GUI initialized for initial user login
class MainWindow():
    def __init__(self, parent): 
        self.__vmFrame = None                 #GUI frame for the VMs
        self.__menuBar = None                 #menubar for app
        self.__dropdown = None                #dropdown box for the VMs
        self.__session = None                 #stores the session
        self.__mainFrame = None               #main frame for the app
        self.__bottomFrame = None             #bottom frame that holds the actions drop down box and the output box
        
        self.__xenHost = None                 #store XenServer Pool
        self.__selectedVM = None              #currently selected VM
        self.__selectedAction = None          #currently selected action
        self.__toggleLoginSlaveVal = 0        #toggle value for 'Login to slave host' option
        self.__toggleVMNetMonitorVal = 0      #toggle for monitoring VM option
        self.__connected = 0                  #used to see is the client is already connected to a host
        
        
        #create the balloon for Pmw
        self.balloon = Pmw.Balloon(parent)
        
                  
        frame = Tkinter.Frame(parent)
        frame.pack(fill = 'both', expand = 1)
        self.__mainFrame = frame
        
        #create the menu bar
        self.menuBar = Pmw.MenuBar(frame, hull_relief = 'raised', hull_borderwidth = 1, balloon = self.balloon)  
        self.menuBar.pack(fill = 'x')
        
        inputFrame = Tkinter.Frame(frame)
        inputFrame.pack()
        
        buttonFrame = Tkinter.Frame(frame)
        buttonFrame.pack()
               

        inputFrame.grid_size()
        # parent.configure(background = 'gray')
        
        
        #add items to the menu bar
        self.menuBar.addmenu('File', 'Exit options')
        self.menuBar.addmenuitem('File', 'separator')
        self.menuBar.addmenuitem('File', 'command', 'Exit the application',
                            command = self.__exit, label = 'Exit')


        self.menuBar.addmenu('Options', 'Set user preferences/options')
        self.menuBar.addmenuitem('Options', 'command', 'Change system password',
                            command = self.__changeSysPass, label = 'Change system password')
    
        #checkbutton menu item for 'Login to slave host' option
        self.__toggleLoginSlave = Tkinter.IntVar()
        
        #checkbutton menu item for monitoring VM option
        self.__toggleVMNetMonitor = Tkinter.IntVar()
        
        #initialize the checkbutton items to 0:
        self.__toggleLoginSlave.set(0)
        self.__toggleVMNetMonitor.set(0)
        
        self.menuBar.addmenuitem('Options', 'checkbutton', 'Login to slave host',
                label = 'Login to slave host',
                command = self.__toggleSlaveLogin,
                variable = self.__toggleLoginSlave)
        
        self.menuBar.addmenuitem('Options', 'checkbutton', 'Start network monitoring on VM',
                label = 'Start network monitoring on VM',
                command = self.__toggleStartVMNetMonitor,
                variable = self.__toggleVMNetMonitor)
        
        self.menuBar.component('Options-menu').entryconfig(2,state='disabled')

        self.menuBar.addcascademenu('Options', 'Filter powered-on VMs by host', 'Filter powered-on VMs by host', traverseSpec = 'z', tearoff = 1)
        

        self.menuBar.addmenu('Help', 'Help', side = 'right')
        self.menuBar.addmenuitem('Help', 'command', 'About this application', command = ShowDialog('About'), label = 'About')
    
        self.menuBar.label_ip = Tkinter.Label(inputFrame, text="IP Address:")
        self.menuBar.label_ip.grid(row=0, column=0, sticky='nw', padx='5')

        self.text_ip = Tkinter.Entry(inputFrame, name="ip")
        self.text_ip.grid(row=1, column=0, sticky='nw', padx='5')  
 
        self.label_username = Tkinter.Label(inputFrame, text="Username:")
        self.label_username.grid(row=0, column=1, sticky='nw', padx='5')
        
        self.text_username = Tkinter.Entry(inputFrame, name="username")
        self.text_username.grid(row=1, column=1, sticky='nw', padx='5')
        
        self.label_password = Tkinter.Label(inputFrame, text="Password:")
        self.label_password.pack(side=LEFT, padx=0)
        self.label_password.grid(row=0, column=2, sticky='nw', padx='5')
        
        self.text_password = Tkinter.Entry(inputFrame, name="password", show="*")
        self.text_password.grid(row=1, column=2, sticky='nw', padx='5')
        
        buttonBox = Pmw.ButtonBox(buttonFrame)
        buttonBox.pack()
        buttonBox.add('connect', text = 'Connect', command = self.__connectButton)
        buttonBox.add('disconnect', text = 'Disconnect', command = self.__disconnectButton)

        self.menuBar.component('Options-menu').entryconfig(0,state='disabled')
        self.menuBar.component('Options-menu').entryconfig(3,state='disabled')


    #initialize bottom part of the main frame
    def __setBottomFrame(self, frame):
        self.__bottomFrame = Tkinter.Frame(frame)
        self.__bottomFrame.pack()
        
        
    #initialize part of the main frame that holds the VM drop down box    
    def __setVMFrame(self, frame):
        self.__vmFrame = Tkinter.Frame(frame)
        self.__vmFrame.pack()
        
        
    #initialize dropdown box with VMs
    def __setDropdown(self, vmFrame, label_text2, labelpos2, vms):
        self.__dropdown = Pmw.ComboBox(vmFrame, label_text = label_text2, labelpos = labelpos2, selectioncommand = self.__selectVM, scrolledlist_items = sorted(vms.keys(), cmp=self.__numeric_compare))
        self.__dropdown.pack()
             
        
    #return the bottom frame or bottom part of the main frame
    def __getBottomFrame(self):
        return self.__bottomFrame


    #return the dropdown box with VMs
    def __getDropdown(self):
        return self.__dropdown
    
        
    #function used to toggle value used to determine if to login to slave host 
    def __toggleSlaveLogin(self):
        if self.__toggleLoginSlaveVal:
            self.__toggleLoginSlaveVal = 0
            
        else:
            self.__toggleLoginSlaveVal = 1
            
            
    #function used to toggle starting and stopping VM monitoring of a VM
    def __toggleStartVMNetMonitor(self):
        session = self.__xenHost.getSession()        
        tempVM = self.__xenHost.getFilteredVMS()[self.__selectedVM]
        
        
        if tempVM.getMonitorState():
            tempVM.getVMMonitor().stopMonitor()
            tempVM.toggleMonitorState()
            self.__updateOutputText("VM monitoring successfully stopped")
        else:
            try:
                tempVM.getVMMonitor().startMonitor()
                tempVM.toggleMonitorState()
                self.__updateOutputText("VM monitoring successfully started")
            except VMNetMonitorError as error:
                self.__toggleVMNetMonitorVal = 0
                self.__toggleVMNetMonitor.set(0)
                command = ShowDialog("Error Monitoring VM")
                command.__call__()
            finally:
                pass
                        
            
    #called when a VM is selected from the VM dropdown box
    def __selectVM(self, vm):       
        self.__selectedVM = vm
        
        if self.__selectedVM and self.__toggleLoginSlaveVal == 0:
            self.menuBar.component('Options-menu').entryconfig(2,state='normal')
            
            
        ManagedVMObject = self.__xenHost.getFilteredVMS().get(self.__selectedVM)
        
        if ManagedVMObject.getMonitorState():
            self.__toggleVMNetMonitor.set(1)
        else:
            self.__toggleVMNetMonitor.set(0)
                        

    #called to update the results output box at the bottom of the main frame - passed-in parameter is the message to display
    def __updateOutputText(self, new_text):
        self.st.configure(text_state = 'normal') 
        self.st.component('text').delete('0.0', '20.0')
        self.st.component('text').insert('0.0', new_text + "\n")
        self.st.configure(text_state = 'disabled')


       
    #from 'actions' dropdown, select operation to perform on VM - called when dropdown is used to select action
    def __selectAction(self, action):        
        self.__selectedAction = action
        
        ManagedVMObject = self.__xenHost.getFilteredVMS().get(self.__selectedVM)
        
        if self.__selectedVM:        
            if self.__selectedAction == "Clean Shutdown VM":
                try:
                    ManagedVMObject.vmCleanShutdown()
                    self.__updateOutputText("VM clean shutdown request sent:\n\nXenTools must be installed on the VM\nfor this request to succeed.")                  
                except VMXenToolsActionError as error:
                    command = ShowDialog("VM XenTools Action Error")
                    command.__call__()
                    
            elif self.__selectedAction == "Start VM":
                try:
                    ManagedVMObject.startVM()
                    self.__updateOutputText("VM start request sent")                   
                except VMActionError as error:
                    command = ShowDialog("VM Action Error")
                    command.__call__()
                               
            elif self.__selectedAction == "Hard Reboot VM":
                try:
                    ManagedVMObject.hardRebootVM()
                    self.__updateOutputText('VM hard reboot request sent')                 
                except VMActionError as error:
                    command = ShowDialog("VM Action Error")
                    command.__call__()
                    
            elif self.__selectedAction == "Suspend VM":
                try:
                    ManagedVMObject.suspendVM()
                    self.__updateOutputText('VM suspend request sent:\n\nXenTools must be installed on the VM\nfor this request to succeed.')                  
                except VMXenToolsActionError as error:
                    command = ShowDialog("VM XenTools Action Error")
                    command.__call__()
                
            elif self.__selectedAction == "Resume VM":
                try:
                    ManagedVMObject.resumeVM()
                    self.__updateOutputText('VM resume request sent:\n\nXenTools must be installed on the VM\nfor this request to succeed.')                
                except VMXenToolsActionError as error:
                    command = ShowDialog("VM XenTools Action Error")
                    command.__call__()
                
            elif self.__selectedAction == "Create Snapshot":
                try:
                    root.update()
                    d = InputDialog(root, "Enter Snapshot Name")
                    root.wait_window(d.top)
            
                    snapshot_name = d.var.strip()
            
                    if snapshot_name:
                        if(re.match("^[A-Za-z0-9_-]{1,20}$", snapshot_name) != None): #validate snapshot name               
                            ManagedVMObject.vmCreateSnapshot(snapshot_name)
                            d.clearVar()
                            
                            self.__updateOutputText("Snapshot request sent")
                        else:
                            command = ShowDialog("Invalid Snapshot Name Error")
                            command.__call__()
                    else:
                        command = ShowDialog("No Snapshot Name Error")
                        command.__call__()                
                except VMActionError as error:
                    command = ShowDialog("VM Action Error")
                    command.__call__()
                    

            elif self.__selectedAction == "Live Migrate VM":
                #ManagedVMObject.migrateVM()
                #print 'VM successfully migrated'
                command = ShowDialog('Not Yet Implemented')
                command.__call__()
            else:
                pass
        else:
           command = ShowDialog('No VM Selected')
           command.__call__()


    #connect to the server
    def __connectButton(self):
        ip = self.text_ip.get()
        username = self.text_username.get()
        password = self.text_password.get()
        
        if(self.__connected == 0): #if not already connected
            if ip:
                if username:
                    if password:
                        try:
                            self.__xenHost = None
                            self.__setXenHost(ip, username, password, self.__toggleLoginSlaveVal) #login and set ManagedXenPool instance variables
                            self.__session = session = self.__xenHost.getSession() #get the current session
                        except LoginError as error:
                            command = ShowDialog("Login Error")
                            command.__call__()
                            root.destroy()
                            sys.exit()
                        finally:
                            pass
                        
                        self.__connected = 1    
                        self.__dropdown = None
                        self.__vmFrame = None
                        
                        self.__bottomFrame = None
                        self.__selectedVM = None
                        self.__selectedAction = None
                        self.__toggleVMNetMonitorVal = 0
                        
                        self.__setVMFrame(self.__mainFrame) 
                        self.__setBottomFrame(self.__mainFrame)   
                        
                        #get all hosts
                        hosts = self.__xenHost.getHosts()
                                           
                        self.__loadVMS(self.__vmFrame)
                        self.__loadActions()
                        self.__loadOutput()
        
                        for currHost in hosts.keys():
                            self.menuBar.addmenuitem('Filter powered-on VMs by host', 'command', 'Filter by ' + currHost, command = PrintVMs(currHost), label = currHost)
                        
                        if(self.__toggleLoginSlaveVal == 0):    
                            self.menuBar.component('Options-menu').entryconfig(0,state='normal')
                        self.menuBar.component('Options-menu').entryconfig(3,state='normal')
                        self.menuBar.component('Options-menu').entryconfig(1,state='disabled')
                    else:
                        command = ShowDialog("Missing Password")
                        command.__call__()
                else:
                    command = ShowDialog("Missing Username")
                    command.__call__()
            else:
                    command = ShowDialog("Missing IP Address")
                    command.__call__()
        else:
            command = ShowDialog('Already Connected')
            command.__call__()
                
        
    #disconnect from the server    
    def __disconnectButton(self):
        if(self.__connected == 1):
            session = self.__xenHost.getSession()
            session.xenapi.session.logout()
            self.__connected = 0
            
            self.__toggleLoginSlave.set(0)
            self.__toggleLoginSlaveVal = 0
            
            self.__toggleVMNetMonitor.set(0)
            self.__toggleVMNetMonitorVal = 0            
            
            #reinitialize respective menu items to logged-off defaults
            self.menuBar.component('Options-menu').entryconfig(0,state='disabled')
            self.menuBar.component('Options-menu').entryconfig(2,state='disabled')
            self.menuBar.component('Options-menu').entryconfig(3,state='disabled')
            self.menuBar.component('Options-menu').entryconfig(1,state='normal')
            
            
            #loop through all the VMs, and, if needed, get its monitoring object and shut it down  
            vms = self.__xenHost.getFilteredVMS()
            
            for vm in vms.values():                
                monitor = vm.getVMMonitor()
                pinger = monitor.getPinger()
                
                if pinger != None:
                    vm.getVMMonitor().stopMonitor()
            
            
            self.__vmFrame.destroy()
            self.__getBottomFrame().destroy()
            self.menuBar.deletemenuitems('Filter powered-on VMs by host', 0, self.__xenHost.getHostCount())
            
        else:
            command = ShowDialog('Already Disconnected')
            command.__call__()
  
    
    #load vms into respective dropdown box    
    def __loadVMS(self, vmFrame, hostFilter = False):       
        vms = {}      
            
        if(hostFilter):
            self.__getDropdown().destroy()
            vms = self.__xenHost.getFilteredVMS()
        else:  
            vms = self.__xenHost.getVMS()
 
        
        self.__setDropdown(vmFrame, 'Virtual Machines:', 'nw', vms)
        
                                       
     
    #regex to strip out the number in front and sort based off of it --- also used as the key to determine what vm was selected
    #since some vms may have the same name  
    def __numeric_compare(self,x,y):
        regexp = re.compile(r"(?P<the_x>^[\d]+)")
        result_x = regexp.search(x)
        
        regexp = re.compile(r"(?P<the_y>^[\d]+)")
        result_y = regexp.search(y)
        
        x_value = result_x.group('the_x')
        y_value = result_y.group('the_y')
        
        return int(x_value) - int(y_value)

        
        
    #load the 'actions' drop down box with operations that can be performed on VMs    
    def __loadActions(self):        
        vmActions = ('','Start VM', 'Clean Shutdown VM', "Hard Reboot VM", "Suspend VM", "Resume VM", "Create Snapshot", "Live Migrate VM")

        actionLabel = "Actions:"
        
        if self.__toggleLoginSlaveVal:
            actionLabel= "Actions: (Disabled - connected to slave!)"
        
        dropdownVmAction = Pmw.ComboBox(self.__getBottomFrame(), label_text = actionLabel, labelpos = 'nw', selectioncommand = self.__selectAction, scrolledlist_items = vmActions,)
        dropdownVmAction.pack()
        
        if self.__toggleLoginSlaveVal:
            dropdownVmAction.component('entry').config(state='disabled')
            dropdownVmAction.component('listbox').config(state='disabled')
            
        
        #display the first VM action which will be ''
        firstAction = vmActions[0]
        dropdownVmAction.selectitem(firstAction)
            
           
    #load the output scrolled text box and set initial values        
    def __loadOutput(self):
        
        #Create the ScrolledText with headers
        fixedFont = Pmw.logicalfont('Fixed')
        self.st = Pmw.ScrolledText(self.__getBottomFrame(),
        labelpos = 'n',
        label_text='',
        columnheader = 1,
        rowcolumnheader = 0,
        usehullsize = 1,
        hull_width = 400,
        hull_height = 300,
        text_wrap='none',
        text_font = fixedFont,
        Header_font = fixedFont,
        Header_foreground = 'blue',
        text_padx = 4,
        text_pady = 4,
        )
        
        headerLine="               Connected!                    "
        
        self.st.pack()
        self.st.component('columnheader').insert('0.0', headerLine)
        self.st.component('text').insert('0.0', "# of VMs in Cluster: " + str(self.__xenHost.getVMCount()) + "\n")
        self.st.component('text').insert('0.0', "# of Host Servers in Cluster: " + str(self.__xenHost.getHostCount()) + "\n")

        self.st.configure(
            text_state = 'disabled',
            Header_state = 'disabled',
        )          
            
            
    
    #filter VMs based on selected host
    def filterByHost(self, host):
        self.__toggleVMNetMonitor.set(0)
        self.menuBar.component('Options-menu').entryconfig(2,state='disabled')
        self.__xenHost.filterByHost(host)
        self.__loadVMS(self.__vmFrame, hostFilter = True)
                                    


    #change the system password of the master host of the pool
    def __changeSysPass(self):
        session = self.__xenHost.getSession()
        sessionID = self.__xenHost.getSessionID()
        
        d = InputDialog(root, "New system password:")
        root.wait_window(d.top)
            
        newPassword = d.var.strip()
        
        if newPassword:
            if(re.match("^[A-Za-z0-9_-]{1,20}$", newPassword) != None):                
                session.xenapi.session.change_password(self.__xenHost.getPassword(), newPassword)
                self.__xenHost.setPassword(newPassword)
                d.clearVar() 
                self.__updateOutputText("Password successfully changed")
            else:
                command = ShowDialog("Invalid Password Error")
                command.__call__()
        else:
                command = ShowDialog("No Password Error")
                command.__call__()

     
       
    #login to host and save respective info into ManagedXenPool object    
    def __setXenHost(self, ip, username, password, slave):
        try:
            self.__xenHost = ManagedXenPool(ip, username, password, slave)
        except LoginError as error:
             raise LoginError(error.message)
        finally:
             pass

       
    #loop through all the VMs, and, if needed, get its monitoring object and shut it down   
    def __exit(self):
        if(self.__connected):
            vms = self.__xenHost.getFilteredVMS()
            
            for vm in vms.values():                
                monitor = vm.getVMMonitor()
                pinger = monitor.getPinger()
                
                if pinger != None:
                    vm.getVMMonitor().stopMonitor()
        
        root.destroy()
        sys.exit()
            
       
               

#used for when "Filter powered-on VMs by host" option is selected from the 'Options menu' - sends the hostname to the
#filterByHost method       
class PrintVMs:
    def __init__(self, text):
        self.text = text

    def __call__(self):
        MainWindow.filterByHost(widget, self.text)
        


#dialog for communicating info, errors/exceptions
class ShowDialog:
    def __init__(self, text):
        self.text = text
        
    def __call__(self):
        if self.text == "About":
            tkMessageBox.showinfo("About", "Lead Developer:\n\nHumair Ahmed")
        elif self.text == "Already Disconnected":
            tkMessageBox.showinfo("Disconnected", "You are already disconnected!")
        elif self.text == "Already Connected":
            tkMessageBox.showinfo("Disconnected", "You are already connected!")
        elif self.text == "Not Yet Implemented":
            tkMessageBox.showinfo("VMotion", "This functionality has not\nyet been implemented!")
        elif self.text == "Missing IP Address":
            tkMessageBox.showinfo("Login Error", "Please enter an IP address!")
        elif self.text == "Missing Username":
            tkMessageBox.showinfo("Login Error", "Please enter a username!")
        elif self.text == "Missing Password":
            tkMessageBox.showinfo("Login Error", "Please enter a password!")
        elif self.text == "Login Error":
            tkMessageBox.showinfo("Server Connection Error", "Server Connection Error - verify connectivity and  XenServer\nlogin credentials.\n\nIf logging into a host of a XenServer pool, you must login to\nthe master host, otherwise, you must select the 'Login to slave\nhost' option in the 'Options' menu before connecting.")
        elif self.text == "No Snapshot Name Error":
            tkMessageBox.showinfo("No Snapshot Created", "No snapshot created!\n\nEnter a maximum 20 character name with only\nnumber, letter, '-', or ' _' characters  and click 'Ok'.")
        elif self.text == "Invalid Snapshot Name Error":
            tkMessageBox.showinfo("Invalid Snapshot Name", "No snapshot created: Invalid snapshot name!\n\nEnter a maximum 20 character name with only\nnumber, letter, '-', or ' _' characters  and click 'Ok'.")
        elif self.text == "No VM Selected":
            tkMessageBox.showinfo("Cannot Perform Action", "Cannot Perform Action: No VM Selected!")  
        elif self.text == "Error Monitoring VM":   
            tkMessageBox.showinfo("Error Monitoring VM", "An error occurred when attempting to monitor the VM.\n\nCurrently the application only supports monitoring a VM\nwith one NIC and IP assigned. XenTools must also be\ninstalled on the VM.\n\nPlease make sure the selected VM meets these requirements\nand confirm the state of the VM.") 
        elif self.text == "No Password Error":
            tkMessageBox.showinfo("Password Not Changed", "The password was not changed!\n\nEnter a maximum 20 character password with only\nnumber, letter, '-', or ' _' characters  and click 'Ok'.")
        elif self.text == "Invalid Password Error":
            tkMessageBox.showinfo("Invalid Password", "Password not changed: Invalid password!\n\nEnter a maximum 20 character password with only\nnumber, letter, '-', or ' _' characters  and click 'Ok'.")              
        elif self.text == "VM XenTools Action Error":
            tkMessageBox.showinfo("Cannot Perform Action", "Cannot Perform Action: Confirm state of VM.\n\nThis action also requires XenTools to be installed\non the VM; confirm the selected VM meets this\nrequirement.")             
        elif self.text == "VM Action Error":
            tkMessageBox.showinfo("Cannot Perform Action", "Cannot Perform Action: Confirm state of VM.\n\nAn error was encountered when attempting to perform\nthis operation.")    
  
  
#dialog for when input from the user is needed - pass in custom message as parameter  
class InputDialog:
    def __init__(self, parent, customDialogMessage):
        self.var = ""
        
        top = self.top = Toplevel(parent)

        Label(top, text=customDialogMessage + ":").pack()

        self.e = Entry(top)
        self.e.pack(padx=5)

        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=5)


    
    def clearVar(self):
        self.var = ""



    def ok(self):
        self.var = self.e.get()
        self.top.destroy()            


#************************************************************************************#
if __name__ == '__main__':
    root = Tkinter.Tk()
  # root.maxsize(600,600)
    root.title(title)
    Pmw.initialise(root)
    widget = MainWindow(root)
    root.mainloop()
