import os
import shutil

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
    elif len(ics) < 1:    
        print ("Please add an ICS file to current directory")
        return
    elif len(ics) == 1:
        icsFile = ics[0]
    
    base = os.path.splitext(icsFile)[0]
    shutil.copy(icsFile, 'ics2pandas.txt')
    return icsFile

def format_ics():
    allEvents = []
    writeOn = False
    icsRead = open('ics2pandas.txt')
    lines = icsRead.readlines()
    for line in lines:
        if "BEGIN:VEVENT" in line:
            writeOn = True
            newEvent = []
        elif "DTSTART" in line and writeOn and ";" not in line:
            year = line[8:12]
            month = line[12:14]
            day = line[14:16]
            time = line[17:21]
            eventStart = [year,month,day,time]
            newEvent.append(eventStart)
        elif "DTEND" in line and writeOn and ";" not in line:
            year = line[8:12]
            month = line[12:14]
            day = line[14:16]
            time = line[17:21]
            eventEnd = [year,month,day,time]
            newEvent.append(eventEnd)           
        elif 'END:VEVENT' in line and writeOn:
            writeOn = False
            allEvents.append(newEvent)
            pass
    for event in allEvents:
       
        pass


def main():
    format_ics()
    pass


    

if __name__ == "__main__":
    main()