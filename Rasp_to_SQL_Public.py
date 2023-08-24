#!/usr/bin/env python3
# Path can be different based on your RPi setup

# Setup imports
import RPi.GPIO as GPIO
import pyodbc
import datetime
from time import sleep
import time


# User Login Connection
Driver_Name = 'FreeTDS' # Driver Name. This can change, but I was able to use the FreeTDS on the RPi relatively easily. 
Server_Name = '1.2.3.4' # Server Name. IP of where you are sending data. 
Port = 1400
Database_Name = 'Name_of_Database' # Name of the database you are trying to send information to.
Username_1 = 'Username' # User
Password_1 = 'Password' # Pass
Version = TDS_Version=8.0   # Version # could change but this one worked for my application.


# Define BEAM_PIN and other variable
# BEAM_PIN = 14 This can obvi be changed to suit whatever pin you want to use.
Var_Location = 'User Defined' # Set the location variable that gets posted with the rest of the data. I'm sure this could be made dynamic with another function that checks the local devices IP and references the geo location or whatever. 
global Var_Current_Beam_Status
global Var_SQL_Last_Entry

# Function for setting up GPIO Modes and BEAM_PIN
def setup_1():  
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
# Function for cleaning GPIO pins after ending function
def clean_1():
    GPIO.cleanup()

# Creating SQL Variable
def SQL_Var_1():
# Connection String
       connection = pyodbc.connect(driver = Driver_Name,
                            server = Server_Name,
                            database = Database_Name,
                            port = Port,
                            uid = Username_1,
                            pwd = Password_1,
                            TDS_Version = Version)
       cursor = connection.cursor()
       try:
              sql_1 = "SELECT TOP(1) Status FROM Table_1 order by TimeStamp desc" # Change Table_1 to the name of your table. Preference is to make table names without spaces as it makes searching easier.
              # SQL Command that pulls the top entry sorted by timestamp, I am sure there is another method of pulling the last entry but his is what I got.
              global Var_SQL_Last_Entry
              cursor.execute(sql_1)
              Var_SQL_Last_Entry = cursor.fetchone()[0]
              # Create the variable for last entry
              cursor.commit()
              cursor.close()
              connection.close()
       except TypeError as e :
              Var_SQL_Last_Entry = 'What' 
              # This should only ever happen the first time you add data to the table, and you can very easily write a query to delete any entry titled "What"
              print(f'Error: {e}')

# Funcion for creating Current_Beam_Status_Var 
def Current_Beam_Status():
       global Var_Current_Beam_Status
       if GPIO.input(14):
           Var_Current_Beam_Status = 'Beam Un-Broken'
           sleep(.5)
        # Might have to tweak the print output to reflect whatever status you are wanting to record/
       else:
           Var_Current_Beam_Status = 'Beam Broken'
           sleep(.5)
        # You can likley use the return command here, but this is how I have it working currently so I will change in a future update.

# Main Function for Status Check
def Beam_Status_Check_1(x):
    try:
           connection = pyodbc.connect(driver = Driver_Name,
                         server = Server_Name,
                         database = Database_Name,
                         port = Port,
                         uid = Username_1,
                         pwd = Password_1,
                         TDS_Version = Version)
                         
           Var_TimeStamp = datetime.datetime.now()
           SQL_Var_1()
           Current_Beam_Status()
           
           if Var_SQL_Last_Entry != Var_Current_Beam_Status:
                  cursor = connection.cursor()
                  cursor.execute('INSERT INTO Table_1 VALUES (?,?,?)', (Var_Current_Beam_Status, Var_TimeStamp, Var_Location))
                  cursor.commit()
                  cursor.close()
                  print(Var_Current_Beam_Status)
                  print('Posted to Server: Updated Status')
                  print('\n')
                  sleep(.5)
            # If status doesn't match then it will post. Else it will just print something, this could likely be setup to log the information to a text file instead of just printing to terminal for a record of the information that didn't get posted.

           else:
                  print(Var_Current_Beam_Status)
                  print('Not Posted to Server: Same Status')
                  print('\n')
                  sleep(.5)
    except pyodbc.OperationalError as e:
        error_code = e.args[0]
        if error_code == '08S01' or error_code == 20009:
            print('Did not post. Unable to connect to server.')
    except Exception as e:
        print('Unexpected error occured.')
        print(f'Details: {e}')
        
    sleep(1)
    
# Function for calling the Edge Detection Loop
def Event_Detect_1():
    GPIO.add_event_detect(14, GPIO.BOTH, callback=Beam_Status_Check_1, bouncetime=500)
    while True:
        time.sleep(0.1)
        pass 
# To be honest I don't really get this bit, but from what I gather the event_detect is a RPi specific command, that allows you to set the pin to check, if its HIGH or LOW or BOTH, the 'callback' being the function it runs when it detects a change, and the bouncetime to keep from multiple detects (might play with value depending on your applicaiton)

# This is what starts the whole thing. Might have to change this to something else but idk. This works for my use, and keeps the program running and checking status for a seemingly infinite amount of time. I have ran this for months without issue posting or reading data. 
while True:
       setup_1()
       try: 
              Event_Detect_1()
              time.sleep(1)
       except ValueError:
              clean_1()
              time.sleep(1)

## Closing notes

# I am running this in conjunction with a bash script on the RPi that checks the status of the internet connection, turns off the wireless lan, and will either start or stop the service associated with this program then restart after waiting a certain amount of time and restarting the networking. Helps with keeping program active despite internet issues. 
# Also used Cron to schedule the Bash script
# Also used Systemd to create a service that runs on boot, after network connection. 
# Bash Script 