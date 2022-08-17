try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk

import logging
from types import prepare_class
import pandas as pd
import numpy as np
import math
from tkcalendar import Calendar, DateEntry
import datetime 
from datetime import date 
import os
import shutil

logging.basicConfig(filename = str(date.today())+' '+str(datetime.datetime.now().strftime("%H.%M.%S"))+".txt", level=logging.NOTSET, filemode='w')
handle = '\n'
logger = logging.getLogger(handle)


def fetch_ics():
    icsFile = ''
    cwd = os.getcwd()
    ics = []
    for file in os.listdir(cwd):
        if file.endswith('.ics'):
            ics.append(file)
    if len(ics) >= 1:
        for i in ics:
            print(i)
        userInputIcs = input("Select an ICS file to process:")
        if userInputIcs in ics:
            icsFile = userInputIcs;
        else: 
            while userInputIcs not in ics:
                print("Invalid name")
                userInputIcs = input("Select an ICS file to process:")
            icsFile = userInputIcs;    
    elif len(ics) < 1:    
        print ("Please add an ICS file to current directory")
        return
    elif len(ics) == 1:
        icsFile = ics[0]
    else:
        print('Failed to imprint file ')
    
    base = os.path.splitext(icsFile)[0]
    shutil.copy(icsFile, 'ics2pandas.txt')
    return icsFile

def format_ics(startDate, endDate, timesheet):
    allEvents = []
    writeOn = False
    icsRead = open('ics2pandas.txt')
    lines = icsRead.readlines()
    for line in lines:
        if "BEGIN:VEVENT" in line:
            writeOn = True
            newEvent = []
        elif "DTSTART" in line and writeOn:
            if 'VALUE=DATE' not in line:
                indexT = line.rindex("T")
                icsDate = line[indexT-8:indexT]    
                year = icsDate[0:4]
                month = icsDate[4:6]
                day = icsDate[6:8]
                icsTime = line[indexT+1:indexT+5]
                time = icsTime[0:4]
                time = (time[0:2]+":"+time[2:4])
                eventEnd = [year,month,day,time]
                newEvent.append(eventEnd)         
        elif "DTEND" in line and writeOn:
            if 'VALUE=DATE' not in line:
                indexT = line.rindex("T")
                icsDate = line[indexT-8:indexT]    
                year = icsDate[0:4]
                month = icsDate[4:6]
                day = icsDate[6:8]
                icsTime = line[indexT+1:indexT+5]
                time = icsTime[0:4]
                time = (time[0:2]+":"+time[2:4])
                eventEnd = [year,month,day,time]
                newEvent.append(eventEnd)       
        elif "RRULE" in line and writeOn:
            eventlist = [] 

            def generateFREQ(starttime,endtime,param): #just generates a full year of events. nothing else
                genEventList = []
                for i in range(365):
                    newEvent = (datetime.datetime.today()+datetime.timedelta(days=i)).strftime("%Y,%m,%d")
                    newEvent = newEvent.split(',')
                    endEvent = newEvent.copy()
                    endEvent.append(endtime)
                    newEvent.append(starttime)
                    genEvent = [newEvent,endEvent]
                    genEventList.append(genEvent)
                # if param == "DAILY":
                #     for i in range(365):
                #         newEvent = (datetime.datetime.today()+datetime.timedelta(days=i)).strftime("%Y,%m,%d")
                #         newEvent = newEvent.split(',')
                #         newEvent.append(time)
                #         genEventList.append(newEvent)
                # if param == "WEEKLY":
                #     for i in range(52):
                #         newEvent = (datetime.datetime.today()+datetime.timedelta(weeks=i)).strftime("%Y,%m,%d")
                #         newEvent = newEvent.split(',')
                #         newEvent.append(time)
                #         genEventList.append(newEvent)
                # if param == "MONTHLY":
                #     for i in range(12):
                #         newEvent = (datetime.datetime.today()+datetime.timedelta(weeks=i*4)).strftime("%Y,%m,%d")
                #         newEvent = newEvent.split(',')
                #         newEvent.append(time)
                #         genEventList.append(newEvent)
                # if param == "YEARLY":
                #     pass
                # print("FREQ")
                # print(genEventList)
                return (genEventList)
            
            def generateUNTIL(eventList,param): #slices away all events that occur after a set date
                genEventList = []
                untilYear = int(param[0:4])
                untilMonth = int(param[4:6])
                untilDay = int(param[6:8])
                for event in eventList:
                    if int(event[0][0]) < untilYear:
                        genEventList.append(event)
                    elif int(event[0][0]) == untilYear and int(event[0][1]) < untilMonth:
                        genEventList.append(event)
                    elif int(event[0][0]) == untilYear and int(event[0][1]) == untilMonth and int(event[0][2]) < untilDay:
                        genEventList.append(event)
                # print("UNTIL")
                # print(genEventList)
                return genEventList

            def generateBYDAY(eventlist,param,freq): # slices away all events not on the set BYDAYS
                if ("WEEKLY") not in freq:
                    #print(freq)
                    print("FAILURE OF FREQ AND BYDAY COMPARISON")
                    print("Or likely auto-confrence maker decided daily is a good FREQ,")
                    return
                paramlist = []
                genEventList = []
                if ("MO") in param:
                    paramlist.append(0)
                elif ("TU") in param:
                    paramlist.append(1)
                elif ("WE") in param:
                    paramlist.append(2)
                elif ("TU") in param:
                    paramlist.append(3)
                elif ("FR") in param:
                    paramlist.append(4)
                elif ("SA") in param:
                    paramlist.append(5)
                elif ("SU") in param:
                    paramlist.append(6)  
                # print(len(eventlist))                  
                for i in range(len(eventlist)):
                    testDate = datetime.datetime.strptime(eventlist[i][0][0]+","+eventlist[i][0][1]+","+eventlist[i][0][2], "%Y,%m,%d")
                    if (testDate.weekday()) in paramlist:
                        genEventList.append(eventlist[i]);
                # print("BYDAY")
                # print(genEventList)
                return genEventList

            rruleLine = line[6:]
            rrulelist = rruleLine.split(";")    
            for rule in rrulelist: #checks every rule in RRULES, split by semicolons, and grabbable by indexOf('=')
                if rule[0:4] == 'FREQ':
                    eventlist = generateFREQ(newEvent[0][3],newEvent[1][3],rule[rule.index("=")+1:])
                    freq = rule[rule.index("=")+1:]
                if rule[0:5] == "BYDAY":
                    eventlist = generateBYDAY (eventlist,rule[rule.index('=')+1:],freq)
                if rule[0:5] == "UNTIL":
                    eventlist = generateUNTIL(eventlist,rule[rule.index("=")+1:])
                    until = rule[rule.index("=")+1:rule.index("=")+8]
                if rule[0:5] == "COUNT":
                    pass
                if rule[0:8] == "INTERVAL":
                    pass
                if rule[0:8] == "BYSECOND":
                    pass
                if rule[0:8] == "BYMINUTE":
                    pass
                if rule[0:6] == "BYHOUR":
                    pass
                if rule[0:10] == "BYMONTHDAY":
                    pass
                if rule[0:9] == "BYYEARDAY":
                    pass
                if rule[0:8] == "BYWEEKNO":
                    pass
                if rule[0:7] == "BYMONTH":
                    pass
                if rule[0:8] == "BYSETPOS":
                    pass
                if rule[0:4] == "WKST":
                    pass
            if (eventlist is not None):
                allEvents = allEvents+eventlist
        elif 'END:VEVENT' in line and writeOn and len(newEvent)>1:
            writeOn = False
            allEvents.append(newEvent)
    tempAllEvents = []
    for event in allEvents: #purge events outside of timsheet's range
        # print(event[0][0])
        # print(event[0][1])
        # print(event[0][2])
        eventStartDate = datetime.date(year=int(event[0][0]),month=int(event[0][1]),day=int(event[0][2]))
        eventEndDate = datetime.date (year=int(event[1][0]),month=int(event[1][1]),day=int(event[1][2]))
        if datetime.datetime.combine(eventStartDate,datetime.time.min)<startDate or datetime.datetime.combine(eventEndDate,datetime.time.min)>endDate:
            pass
        else:
            tempAllEvents.append(event)
    #print (allEvents)
    allEvents = tempAllEvents
    #print (allEvents)
    for event in allEvents: #mark down timesheet with events
        eventStartDate = datetime.date(int(event[0][0]),int(event[0][1]),int(event[0][2]))
        eventEndDate = datetime.date(int(event[1][0]),int(event[1][1]),int(event[1][2]))
        eventStartDate = datetime.datetime.combine(eventStartDate,datetime.time.min)
        eventEndDate = datetime.datetime.combine(eventEndDate,datetime.time.min)
        eventStartTime = datetime.datetime.strptime(event[0][3],'%H:%M').time()
        eventEndTime = datetime.datetime.strptime(event[1][3],'%H:%M').time()
        timesheet.loc[eventStartTime:eventEndTime,eventStartDate] = 'X'
    return timesheet

def example1():
    def print_sel():
        print(cal.selection_get())

    top = tk.Toplevel(root)

    cal = Calendar(top, font="Arial 14", selectmode='day', locale='en_US',
                year=2018, month=2, day=5)
    
    cal.pack(fill="both", expand=True)
    ttk.Button(top, text="ok", command=print_sel).pack()

def example2():

    top = tk.Toplevel(root)
    top.update_idletasks()
    cal = Calendar(top, selectmode='none')
    date = cal.datetime.today() + cal.timedelta(days=2)
    cal.calevent_create(date, 'Hello World', 'message')
    cal.calevent_create(date, 'Reminder 2', 'reminder')
    cal.calevent_create(date + cal.timedelta(days=-2), 'Reminder 1', 'reminder')
    cal.calevent_create(date + cal.timedelta(days=3), 'Message', 'message')

    cal.tag_config('reminder', background='red', foreground='yellow')

    cal.pack(fill="both", expand=True)
    ttk.Label(top, text="Hover over the events.").pack()
    top.update_idletasks()

def taskProcess():
    top = tk.Toplevel(root)
    top.update_idletasks()
    tk.Label(top, text ='Processing...').pack(padx=10,pady=10)
    def popupExe():
        popup.grab_release()
        top.destroy()
    def popupDone():
        taskDisplay(0)
        popup.grab_release()
        top.destroy()   
    if len(taskHolding.taskList) <= 0:
        popup = tk.Toplevel(top)
        popup.grab_set()
        tk.Label(popup, text = 'Make sure you have some tasks to assign!').pack(padx=10,pady=10)
        tk.Button(popup,text = "Ok", command = popupExe).pack()
    else:
        popup = tk.Toplevel(top)
        popup.grab_set()
        tk.Label(popup,text = 'Done!').pack(padx=10,pady=10)
        tk.Button(popup,text = "Ok", command = popupDone).pack()
        
def taskDisplay(dailyTaskLimit):
    taskSlicer() #tasks are assumed ready and will now be sliced
     #??? why does tkinter hate you mr calander
    headers = ['Subject','Start Date','Start Time', 'End Date', 'End Time', 'All Day Event', 'Description']
    clocktime = datetime.datetime.strptime('00:00','%H:%M') #pain datetime is module AND class name :shikipain: 
    wholeclock = []
    for i in range (1440): #this creates a list of times from 0:00 to 23:59
        tmp = clocktime+datetime.timedelta(minutes=i)

        wholeclock.append(tmp.time()) 
    calsheet = pd.DataFrame(headers).T
    calsheet.reset_index()
    datetimeYearFromToday = pd.date_range(taskHolding.today,taskHolding.today+datetime.timedelta(days=365),freq='d')
    datetimeYearFromToday = datetimeYearFromToday.to_pydatetime()
    #print(type(datetimeYearFromToday[0]))  
    timesheet = pd.DataFrame(columns=datetimeYearFromToday,index = wholeclock)
    #print(datetimeYearFromToday[0])
    fetch_ics()
    timesheet = format_ics(taskHolding.today,taskHolding.today+datetime.timedelta(days=365),timesheet)

    #print(timesheet)
    # print (cal)
    logging.info('taskHolding''s tasklist')
    logging.info(taskHolding.taskList)
    for task in taskHolding.taskList:
        currentTaskNum = taskHolding.taskList.index(task) #the powerful for loop without for looping. 
        taskOverload = False
        dailyWorkLimit = 240 #comment out as needed
        dailyTaskLimit = 6
        totalTaskTime = task[2]
        taskStartDate = task[3]
        taskEndDate = task[4].date()
        totalDays = task[4]-task[3] 
        totalDays = totalDays.days
        daysBetweenTasks = 0
        

        taskStartTime = (datetime.datetime.strptime('10:00','%H:%M')).time() #establishes start and end points  
        taskEndTime = datetime.datetime.strptime('22:00','%H:%M').time()
        taskBreakTime = 10 #change as needed

        currentTaskDate = taskStartDate.date()
        pandasTaskDate = taskStartDate
        currentTaskStartTime = taskStartTime

        currentSlicedTasks = taskHolding.slicedTaskList[currentTaskNum]
        totalSlicedTasks = len(currentSlicedTasks)
        # print (totalDays)
        
        if int(totalSlicedTasks) > int(totalDays):
            taskOverload = True
            repeats = math.floor(totalDays/totalSlicedTasks)
        else:
            taskOverload = False
            daysBetweenTasks = math.floor(totalDays/totalSlicedTasks)
        for slices in currentSlicedTasks:
            logger.info('Current Timesheet')
            logger.info(timesheet.iloc[:,0:5]) #looks ahead a little bit
            logger.info('Current Slice')
            logger.info(slices)
            taskTime = datetime.datetime.strptime('00:'+str(slices[0]),'%H:%M').time()
            if taskOverload:
                logging.info("taskOverload?")
                logging.info(taskOverload)
                currentTaskEndTime = datetime.datetime.strptime(str(currentTaskStartTime),'%H:%M:%S')+datetime.timedelta(hours=taskTime.hour,minutes=taskTime.minute)
                currentTaskEndTime = currentTaskEndTime.time()
                #print(currentTaskStartTime)
                #print(currentTaskEndTime)
                #print(pandasTaskDate)
                nanSlice = timesheet.loc[currentTaskStartTime:currentTaskEndTime,pandasTaskDate] 
                logger.info(nanSlice.to_string())
                    ### documentation for nanChecker, the bane of my existance
                    # grabs a slice of time as a series, column is currentTaskDate, and checks if the slice is all empty
                    # if it is, deposit the taskslice there. If not, move down 10 min (the length of a break) and try again. 
                nanChecker = nanSlice.isnull().values.all()
                logger.info(nanChecker)
                if nanChecker == False:
                    while nanChecker==False:
                        if currentTaskEndTime >= taskEndTime: #WORK START HERE check if currentTaskEndTime exceeds a day
                            logging.info('NEW DAY ADDED')
                            currentTaskDate= currentTaskDate+datetime.timedelta(days=1)  
                            pandasTaskDate= datetime.datetime.combine(currentTaskDate,datetime.time.min)
                            currentTaskStartTime = taskStartTime
                            currentTaskEndTime = (datetime.datetime.combine(currentTaskDate,currentTaskStartTime)+ datetime.timedelta(hours=taskTime.hour,minutes=taskTime.minute)).time()
                        else:
                            currentTaskStartTime = (datetime.datetime.combine(currentTaskDate, currentTaskStartTime)+datetime.timedelta(minutes = taskBreakTime)).time()
                            currentTaskEndTime = (datetime.datetime.combine(currentTaskDate,currentTaskEndTime)+datetime.timedelta(minutes = taskBreakTime)).time()
                        nanSlice = timesheet.loc[currentTaskStartTime:currentTaskEndTime,pandasTaskDate]
                        logging.info(nanSlice)
                        nanChecker = nanSlice.isnull().values.all()
                        logger.info(nanChecker)
                    timesheet.loc[currentTaskStartTime:currentTaskEndTime,pandasTaskDate] = task[0]
                    tmp = pd.DataFrame([task[0],currentTaskDate.strftime("%m/%d/%Y"),currentTaskStartTime.strftime("%H:%M"),currentTaskDate.strftime("%m/%d/%Y"),currentTaskEndTime.strftime("%H:%M"),'False',task[1]]).T
                    calsheet.drop_duplicates()
                    calsheet.reset_index()
                    calsheet = pd.concat([calsheet,tmp],ignore_index=True)
                    currentTaskDate = datetime.datetime.combine(currentTaskDate,datetime.time.min)+datetime.timedelta(days=1);
                    if currentTaskDate > datetime.datetime.combine(taskEndDate,datetime.time.min):
                        currentTaskDate = taskStartDate
                    pandasTaskDate = currentTaskDate
                    currentTaskDate = currentTaskDate.date()
                    logger.info("PandasTaskDate")
                    logger.info(pandasTaskDate)    
                    #If out of time, split task into smaller ones and try cramming them into past taskEnd or task Start (to be implemented)
                    pass
                elif nanChecker == True: 
                    timesheet.loc[currentTaskStartTime:currentTaskEndTime,pandasTaskDate] = task[0]
                    tmp = pd.DataFrame([task[0],currentTaskDate.strftime("%m/%d/%Y"),currentTaskStartTime.strftime("%H:%M"),currentTaskDate.strftime("%m/%d/%Y"),currentTaskEndTime.strftime("%H:%M"),'False',task[1]]).T
                    calsheet.drop_duplicates()
                    calsheet.reset_index()
                    calsheet = pd.concat([calsheet,tmp],ignore_index=True)
                else :
                    print("ERROR: UNACCESSABLE NANCHECKER STATE. PLEASE REFER TO LOGS FOR MORE INFO")
            elif not taskOverload:       
                logging.info("taskOverload?")
                logging.info(taskOverload)
                currentTaskEndTime = datetime.datetime.strptime(str(currentTaskStartTime),'%H:%M:%S')+datetime.timedelta(hours=taskTime.hour,minutes=taskTime.minute)
                currentTaskEndTime = currentTaskEndTime.time()
                nanSlice = timesheet.loc[currentTaskStartTime:currentTaskEndTime,pandasTaskDate]
                logger.info(nanSlice.to_string())
                nanChecker = nanSlice.isnull().values.all()
                logger.info(nanChecker)
                if nanChecker == False:
                    while nanChecker==False:
                        if currentTaskDate > taskEndDate: #loop back to the start and look for possible more days
                            currentTaskDate = (datetime.datetime.combine(taskStartDate,datetime.time.min)+datetime.timedelta(days=1)).date()
                            pandasTaskDate = currentTaskDate
                        if currentTaskEndTime >= taskEndTime: #WORK START HERE check if currentTaskEndTime exceeds a day
                            logging.info('NEW DAY ADDED')
                            currentTaskDate= currentTaskDate+datetime.timedelta(days=1)  
                            pandasTaskDate= datetime.datetime.combine(currentTaskDate,datetime.time.min)
                            currentTaskStartTime =  taskStartTime
                            currentTaskEndTime = (datetime.datetime.combine(currentTaskDate,currentTaskStartTime)+ datetime.timedelta(hours=taskTime.hour,minutes=taskTime.minute)).time()
                        else:
                            currentTaskStartTime = (datetime.datetime.combine(currentTaskDate, currentTaskStartTime)+datetime.timedelta(minutes = taskBreakTime)).time()
                            currentTaskEndTime = (datetime.datetime.combine(currentTaskDate,currentTaskEndTime)+datetime.timedelta(minutes = taskBreakTime)).time()
                        nanSlice = timesheet.loc[currentTaskStartTime:currentTaskEndTime,pandasTaskDate]
                        logger.info(nanSlice)
                        nanChecker = nanSlice.isnull().values.all()
                        logger.info(nanChecker)
                    timesheet.loc[currentTaskStartTime:currentTaskEndTime,pandasTaskDate] = task[0]
                    tmp = pd.DataFrame([task[0],currentTaskDate.strftime("%m/%d/%Y"),currentTaskStartTime.strftime("%H:%M"),currentTaskDate.strftime("%m/%d/%Y"),currentTaskEndTime.strftime("%H:%M"),'False',task[1]]).T
                    calsheet.drop_duplicates()
                    calsheet.reset_index()
                    calsheet = pd.concat([calsheet,tmp],ignore_index=True)
                    
                else: 
                    timesheet.loc[currentTaskStartTime:currentTaskEndTime,pandasTaskDate] = task[0]
                    tmp = pd.DataFrame([task[0],currentTaskDate.strftime("%m/%d/%Y"),currentTaskStartTime.strftime("%H:%M"),currentTaskDate.strftime("%m/%d/%Y"),currentTaskEndTime.strftime("%H:%M"),'False',task[1]]).T
                    calsheet.drop_duplicates()
                    calsheet.reset_index()
                    calsheet = pd.concat([calsheet,tmp],ignore_index=True)
                    currentTaskDate = datetime.datetime.combine(currentTaskDate,datetime.time.min)+datetime.timedelta(days=daysBetweenTasks);
                    pandasTaskDate = currentTaskDate
                    currentTaskDate = currentTaskDate.date()
                    logger.info("PandasTaskDate")
                    logger.info(pandasTaskDate)               
    
    #print(calsheet)
    logging.info("TIME SHEET")  
    pd.set_option('max_rows', None)   
    logging.info(timesheet)

    timesheet.to_csv('timesheet.csv')      
    calsheet.to_csv('calsheet.csv', index=False, header=False)
     
def taskSlicer ():
    #task is a list of [str(task name),str(task description),int(total Time for task),
    # datetime(startdate),datetime(enddate),int(priority)]
    #partitionLength is a int
    partitionLength = 0
    taskList = [] 

    for tasks in taskHolding.taskList:
        totalLength = tasks[2]
        partitionTaskList = []
        delta = (tasks[4])-(tasks[3])
        days = delta.days    
        priority = tasks[5]
        if priority == 5:  #no case/switch in python, values are adjustable
            partitionLength = 20
        elif priority == 4:
            partitionLength =  25
        elif priority == 3:
            partitionLength =  30
        elif priority == 2:
            partitionLength =  40
        elif priority == 1:
            partitionLength =  45
        else: 
            partitionLength = 30 #(default for -1 partitionLength or errors that can occur) 
        totalslices = tasks[2]/partitionLength
        roundedslices = int(totalslices) #watch for weird behavior for int just in case
        for i in range(roundedslices):
            divTask =  (partitionLength, tasks[0]+":Part "+str(int(i+1))) #this is a slice
            partitionTaskList.append(divTask)
            totalLength = totalLength - partitionLength
        if (roundedslices < totalslices): #checks if the slices are cut evenly, if not, add one final task
            divTask = (totalLength, tasks[0]+":Part "+str(int(roundedslices)))  
            partitionTaskList.append(divTask)
        taskList.append(partitionTaskList)
    taskHolding.slicedTaskList = taskList
    #print(taskList)
    return taskList

def taskAssigner (taskList, startDate, endDate): #why did I even make you
    user = userData
    delta = endDate - startDate
    totalHours = delta.days*10 

def taskPriority():
    def popupExe():
        top.grab_release() 
        top.destroy()
    def submitPrio():
        for task in taskHolding.taskList:
            task[5] = (buttonControl[taskHolding.taskList.index(task)])
        top.destroy()
        

    top = tk.Toplevel(root)
    if len(taskHolding.taskList): #0 is false in python. good to know :rocry:
        
        r1,r2,r3,r4,r5,r6,r7,r8,r9,r10=tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar()#forgive me father, for I have sinned
        buttonControl = [r1,r2,r3,r4,r5,r6,r7,r8,r9,r10]

        tk.Label(top, text = "Assinging Priority: 5 is lowest, 1 is highest").grid(row=0,column=0)
        for i in range(len(taskHolding.taskList)):
            if (i>9):
                #we only want 10 tasks to assign atm, we can rewrite something here eventually.
                break
            tk.Label(top,text = taskHolding.taskList[i][0]).grid(row=i+1,column = 0) 
            for j in range(5):
                tempRadioButton = tk.Radiobutton(top, text = str(5-j),justify="left",variable = buttonControl[i], value = 5-j, tristatevalue=-1)
                tempRadioButton.grid(row = i+1, column = j+1)
        
        gridDim = top.grid_size()
        tk.Button(top, text ="Submit", command = submitPrio).grid(row=11, column =5,padx=10, pady=(5,10))
    else:
        top.grab_set()
        tk.Label(top, text = "There are no current tasks, go assign some!").pack()
        tk.Button(top, text = "OK", command = popupExe).pack()

def taskRequest ():
    def verifyInt(input):
        try:
            val =int(str(input.get()))
        except ValueError:
            return False
        return True

    def submitTask():
        taskHolding.taskName = taskName_var.get()
        taskHolding.taskDesc = taskDesc_var.get()
        if verifyInt(taskTotalTime_var):
            taskHolding.taskTotalTime = taskTotalTime_var.get()
            taskHolding.taskTotalTime = int(taskHolding.taskTotalTime)*60

            def endDateSelector(): #function was drawn up elsewhere and airdropped into here. I would remove the function if it doesnt affect anything else
                def submitDate():
                    taskHolding.endTime = datetime.datetime.combine(endDate.get_date(),datetime.datetime.min.time())
                    taskHolding.startTime = datetime.datetime.combine(startDate.get_date(),datetime.datetime.min.time())
                    if taskHolding.startTime < taskHolding.endTime:
                        task = [taskHolding.taskName, taskHolding.taskDesc, taskHolding.taskTotalTime, taskHolding.startTime, taskHolding.endTime,-1]
                        taskHolding.taskList.append(task)
                        #print(taskHolding.taskList)
                        top.destroy()
                    elif taskHolding.endTime < taskHolding.startTime:
                        def popupExe():
                            popup.grab_release() 
                            popup.destroy()
                        popup = tk.Toplevel(top)
                        popup.grab_set()
                        tk.Label(popup, text = 'Make sure the start date occurs before the end date').pack(padx=10,pady=10)
                        tk.Button(popup,text = "Ok", command = popupExe).pack()

                top2 = tk.Toplevel(top)
                top2.grab_set()
                currentyear = date.today().year
                ttk.Label(top2, text='Choose Start Date').pack(padx=10, pady=10)
                startDate = DateEntry(top2, width=12, background='darkblue',
                                foreground='white', borderwidth=2, year=currentyear)
                startDate.pack(padx=10, pady=10)

                ttk.Label(top2, text='Choose End Date').pack(padx=10, pady=10)
                endDate = DateEntry(top2, width=12, background='darkblue',
                                foreground='white', borderwidth=2, year=currentyear)
                endDate.pack(padx=10, pady=10)
                
                tk.Button(top2, text='Submit', command = submitDate).pack() 
                logging.info("Task Added")
                
            endDateSelector()

        else:
            def popupExe():
                popup.grab_release() 
                popup.destroy()
            popup = tk.Toplevel(top)
            popup.grab_set()
            tk.Label(popup, text = 'Please enter only integers').pack(padx=10,pady=10)
            tk.Button(popup,text = "Ok", command = popupExe).pack()
            
    top = tk.Toplevel(root)
    top.geometry('400x250')
    taskName_var = tk.StringVar()
    taskDesc_var = tk.StringVar()
    taskTotalTime_var = tk.StringVar()
    tk.Label(top, text = 'Task Name').pack() 
    tk.Entry(top, textvariable = taskName_var,width = 50).pack(padx=10,pady=10)

    tk.Label(top, text = 'Task Description').pack()
    tk.Entry(top,textvariable = taskDesc_var,width = 50).pack(padx=10,pady=10)
    
    tk.Label (top, text = 'Task Length (in hours)').pack()
    tk.Entry(top, textvariable = taskTotalTime_var).pack(padx=10,pady=10)
    
    tk.Button(top,text = "Submit", command = submitTask).pack()

class userData:
    optTaskStartTime = 0    #opt = optimal


class taskData:
    # 
    taskList = [] #tasks contain all the below
    slicedTaskList =[] #tasks with given partitions
    today = datetime.datetime.combine(date.today(),datetime.datetime.min.time())
    endTime = None
    startTime = None
    taskName = None
    taskDesc = None
    taskTotalTime = 0
    priority = -1
    def __str__(self):
        return "taskName: "+self.taskName

taskHolding = taskData 
today = datetime.datetime.combine(date.today(),datetime.datetime.min.time())
            
root = tk.Tk()
root.geometry ('300x150')
ttk.Button(root, text='Task Entry', command = taskRequest).pack(padx=10,pady=10)
ttk.Button(root, text='Task Priority', command=taskPriority).pack(padx=10, pady=10)
ttk.Button(root, text='Task Calendar', command=taskProcess).pack(padx=10, pady=10)

root.mainloop()