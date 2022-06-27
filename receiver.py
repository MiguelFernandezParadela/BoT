import json
import hashlib
from paho.mqtt import client as mqtt_client


try:
    configFile = open("./config.json", 'r')
    configJSON = json.loads(configFile.read())
except:
    print("Failed to read config json! ")
else:
    iotNumber = configJSON['iotNumber']
    mqttBroker = "192.168.1.210"
    mqttPort = 1883
    clientID = 'python-receiver-' + str(iotNumber)
    mqttTopic = "BoT/brick"
    blockJSON = {"block": [0,0,0,0]}         # INICIALIZAMOS ESTÁTICAMENTE CON 0s E INGRESAREMOS EN ORDEN
    username = configJSON['username']
    password = configJSON['password']
finally:
    configFile.close()

def on_log(client, userdata, level, buf):
    client.publish("BoT/iot/" + str(iotNumber) + "/status", "client online")


def on_message(client, userdata, message):
    brick = message.payload.decode("utf-8").replace("'", '"')   # brick es string
    brickjson = json.loads(brick)
    blockMaker(brickjson, brickjson["iot"])


def blockMaker(brick, user):
    global blockJSON
    index = user
    blockJSON["block"][index] = brick

    if blockVerifier():
        payloadString = str(blockJSON["block"])
        blockJSON["hash"] = hashlib.md5(payloadString.encode()).hexdigest() #hasheo
        blockSender(blockJSON)


def blockSender(block):
    global blockJSON
    result = client.publish("BoT/block", str(block))
    # result: [0, 1]
    if result[0] == 0:
        print("Sent correctly to blockchain ")
        client.publish("BoT/iot/" + str(iotNumber) + "/status", "currently sending...")
        blockJSON = {"block": [0, 0, 0, 0]}
    else:
        print("Failed to send block!")


def blockVerifier():
    for item in blockJSON['block']:
        if item == 0:
            return False
    return True

def subscribeTopic(topic):
    result = client.subscribe(topic, qos=0)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print("Subscribed to " + mqttTopic)
        client.on_message = on_message    # set the daemon
        print("running loop...")
        client.loop_forever()
    else:
        print("Failed to subscribe!")


client = mqtt_client.Client(client_id=clientID)
client.tls_set('/etc/mosquitto/ca_certificates/ca.crt', '/etc/mosquitto/ca_certificates/key.key')
client.username_pw_set(username, password)
client.connect(mqttBroker, mqttPort)
client.publish("BoT/iot/"+str(iotNumber)+"/status", "receiver connected")
subscribeTopic(mqttTopic)