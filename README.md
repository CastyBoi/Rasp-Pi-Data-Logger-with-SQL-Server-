So I am attempting to set this up as a way to store the progress of my "Data Logger". 
It is based on a Raspberry Pi, a custom bracket that attaches to a valve actuator, coded predominetly in Python.  
General Overview of Data Logger:
  - I have used a pair of 'Breakbeam' Sensors plugged into the GPIO pins of the RPI
  - The RPI is configured to read the sensor inputs using Python.
  - Sensor states are labeled as 'Broken' or 'Unbroken' depending on position of 'Flag' between beams
  - Data is then recorded and sent to a SQL Server for storage
  - (Only posts after verifiying it will not double record the same status)
  - Bash Scripts and CronTab are used to check the internet connectivity and restart the Application if necessary.

I took some inspiration from various other data logging programs I was able to find, and added in some extra bits to fit my specific application.
