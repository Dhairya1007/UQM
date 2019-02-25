import pygatt
import time
import struct
from Adafruit_IO import Client,Feed
from firebase import firebase
import csv
import geocoder

firebase = firebase.FirebaseApplication("Your Firebase URL")
adapter = pygatt.GATTToolBackend()
locate = geocoder.ip('me')
locate1 = locate.latlng
#NXP Mac Address which is located at the back of the device
BLE_ADDRESS = 'Your Rapid IoT MAC Address'
#Adafruit IO Configuration
ADAFRUIT_IO_USERNAME = "Your AIO Username"
ADAFRUIT_IO_KEY = "Your AIO Key"

aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)   #Starting the Adafruit Client

#Defining the feed keys 
light_feed = aio.feeds('light-feed')
temp_feed = aio.feeds('temp-feed')
humidity_feed = aio.feeds('humidity-feed')
air_feed = aio.feeds('air-feed')
pressure_feed = aio.feeds('pressure-feed')

#Starting of the main fetching program
try:
    adapter.start()     #Starting the BLE Adapter
    device = adapter.connect(BLE_ADDRESS)     #connect to the Rapid IoT prototying kit
    
    while True:      #Loop to continuously fetch the vallues

        # Value fetching, can be done with a loop too but I did this for easy interpretation
        
        light_initial = device.char_read("1493dd8e-8c3e-4e79-a4ff-6f0cd50005f9")    #Ambient Light Value in bytearray     
        temp_initial = device.char_read("1493dd8e-8c3e-4e76-a4ff-6f0cd50005f9")    #Temperature Value in bytearray
        humidity_initial = device.char_read("1493dd8e-8c3e-4e77-a4ff-6f0cd50005f9")  #Humidity Value in bytearray
        air_initial = device.char_read("1493dd8e-8c3e-4e75-a4ff-6f0cd50005f9")      #Air Quality Value in bytearray
        pressure_initial = device.char_read("1493dd8e-8c3e-4e78-a4ff-6f0cd50005f9")  #Pressure Value in bytearray
        battery_initial = device.char_read("964bf77c-9f4d-4b27-9340-7eb81c1dfbd5")   #Battery Level value in bytearray
        state_initial = device.char_read("964bf77c-9f4d-4b27-9340-7eb81c1dfbd6")    #Charging state value in bytearray

        # Location information
        lat = locate1[0]
        lon = locate1[1]
        #converting bytearray to normal value and accessing the actual value(in Tuple)
        
        light_value = struct.unpack('i',light_initial)     
        light_value1 = light_value[0]     

        temp_value = struct.unpack('f',temp_initial)
        temp_value1 = temp_value[0]
        temp_value1 = round(temp_value1, 2)

        humidity_value = struct.unpack('f',humidity_initial)
        humidity_value1 = humidity_value[0]
        humidity_value1 = round(humidity_value1, 2)

        air_value = struct.unpack('i',air_initial)
        air_value1 = air_value[0]

        pressure_value = struct.unpack('i',pressure_initial)
        pressure_value1 = pressure_value[0]

        csvData = [['Sensor','Value','Latitude','Longitude'],['Temperature',temp_value1,lat,lon],['Humidity',humidity_value1,lat,lon],['AirQuality',air_value1,lat,lon],['AmbientLight',light_value1,lat,lon],['Pressure',pressure_value1,lat,lon]]

        with open('data.csv','w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(csvData)
            print "Data stored in csv file successfully"
        csvFile.close()
        
        battery_value = struct.unpack('i',battery_initial)
        battery_value1 = battery_value[0]

        state_value = struct.unpack('i',state_initial)
        state_value1 = state_value[0]
        
        if state_value1 == 1 :      #converting charging state in string
            state = "Charging"
        else:
            state = "Not Charging"

        #Printing the obtained values
        print "--------------- Rapid IoT Sensor Values-------------------------"
        
        print "Ambient Light Value:"+str(light_value1)
        print "Temperature Light Value:"+str(temp_value1)
        print "Humidity Value:"+str(humidity_value1)
        print "Air Quality Value(TVOC):"+str(air_value1)
        print "Pressure Value:"+str(pressure_value1)
        print("Battery Value:",battery_value1)
        print("Charging State :",state)
        print "----------------------------------------------------------------"
        #Sending this data to the Adafruit io feeds for furthur analysis
        aio.send_data(light_feed.key, light_value1)
        aio.send_data(temp_feed.key, temp_value1)
        aio.send_data(humidity_feed.key, humidity_value1)
        aio.send_data(air_feed.key, air_value1)
        aio.send_data(pressure_feed.key, pressure_value1)

        #Send the data to firebase for real time monitoring remotely
        firebase.put('urban-quality-monitor','Temperature',temp_value1)
        firebase.put('urban-quality-monitor','Humidity',humidity_value1)
        firebase.put('urban-quality-monitor','Ambient Light',light_value1)
        firebase.put('urban-quality-monitor','Air Quality',air_value1)
        firebase.put('urban-quality-monitor','Pressure',pressure_value1)
        
        time.sleep(5)      #A time delay of 5 seconds before reading the value
        
    
finally:
    adapter.stop()      #stop the BLE Adapter
