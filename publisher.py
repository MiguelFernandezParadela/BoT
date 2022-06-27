import math
import time
from datetime import datetime
from paho.mqtt import client as mqtt_client
import json

try:
    configFile = open("./config.json", 'r')
    configJSON = json.loads(configFile.read())
except:
    print("Failed to read config json! ")
else:
    iotNumber = configJSON['iotNumber']
    mqttBroker = "192.168.1.210"
    mqttTopic = "BoT/brick"
    mqttPort = 1883
    client_id = 'python-sender-' + str(iotNumber)
    nameVar1 = configJSON['vars'][0]
    nameVar2 = configJSON['vars'][1]
    averageVar1 = configJSON['averages'][0]
    averageVar2 = configJSON['averages'][1]
    username = configJSON['username']
    password = configJSON['password']
finally:
    configFile.close()

def function(t, height):
    #  y(t)=A * {sen(\omega t+\varphi ) + height}
    return 10 * math.sin(4 * t + 1) + height

def start():
    timer = 1
    direccion = 1

    while True:
        if 1 > timer > 40:
            direccion = direccion * (-1)

        var1 = round(function(timer, averageVar1), 2)
        var2 = round(function(timer, averageVar2), 2)
        brickMaker(var1, var2)
        timer += direccion
        time.sleep(configJSON['sleeper'])


def brickMaker(var1, var2):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    brick = {"iot": iotNumber, nameVar1: var1, nameVar2: var2, "timestamp": current_time}
    brickSender(brick)

def brickSender(brick):
    client = mqttClient
    result = client.publish(mqttTopic, str(brick).replace("'", '"'))
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print("Sent: " + str(brick))
    else:
        print("Failed to send message!")


def connect_mqtt():
    client = mqtt_client.Client(client_id)
    client.tls_set('/home/pi/client1/ca.crt', '/home/pi/client1/client1.crt', '/home/pi/client1/client1.key')
    client.tls_insecure_set(1) # because server name and common name mismatch. Otherwise, set to 0
    client.username_pw_set(username, password)
    client.connect(mqttBroker, mqttPort)
    client.publish("BoT/iot/"+str(iotNumber)+"/status", "Sender Connected")
    return client


def main():
    print("Sending on topic: " + str(mqttTopic) + " on port: " + str(mqttPort))
    print("---------------------------------------------------------------------")
    time.sleep(1)
    start()

mqttClient = connect_mqtt()
main()
