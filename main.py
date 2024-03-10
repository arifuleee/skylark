 # Complete project powered by Aurbot                            
import machine
import time
from libs.umqttsimple import MQTTClient
import json
import ubinascii
from libs.wifi_manager import WifiManager
import esp
esp.osdebug(None)
import gc
import network
import re
import socket
gc.collect()


# defining touch screen and rfid reader
dwinSerial = machine.UART(2, 9600)
rfidSerial = machine.UART(1, baudrate=115200, tx = 21 , rx = 4)
# rfidSerial = machine.UART(1, baudrate=115200, tx = 33 , rx = 32)
# rfidSerial = machine.UART(1, baudrate=115200, tx = 21 , rx = 22)

def setDatatoVP(address, pData):
#     print(pData)
    strLen = len(pData)
    strList = list(pData)
    byte_5 = int('0x' + str(address)[:2])
    byte_6 = int('0x' + str(address)[2:])
    data = [0x5A, 0xA5, strLen+3, 0x82, byte_5 , byte_6]
    print(data)
    for xValue in strList:
        data.append(ord(xValue))
        dwinSerial.write(bytes(data))
               
def pageSwitch(pageNO):
    pageSdata = [0x5A, 0xA5, 0x07, 0x82, 0x00, 0x84, 0x5A, 0x01, 0x00, pageNO]
#     print(pageSdata)
    dwinSerial.write(bytes(pageSdata))

pageSwitch(0)
noID = '         '
setDatatoVP(1100, noID)
# Establish wifi connection 
wm = WifiManager()
wm.connect()
# credentials = str(wm.read_credentials())
# wifi_exisSSID = str(credentials.split(":"))
# wifi_SSID = wifi_exisSSID.split(":")
# print(wifi_exisSSID)
# print(wifi_SSID)
with open(wm.wifi_credentials) as file:
    lines = file.readlines()
    print(lines)
    for line in lines:
        print(line)
#       print(type(line))
        ssid, password = line.strip().split(';')
        print(ssid)
        setDatatoVP(3500, (ssid+'           '))


# functional variables
run = 0
recieved = 0
userid_check = None


client_id = ubinascii.hexlify(machine.unique_id())
# print(client_id)
machineId = str(int(client_id,16))
# machineId = '40059844217288'
print(machineId)
setDatatoVP(3700, machineId)

#retreve server and topic
with open('data.json', 'r') as f:
    data = json.load(f)
# mqttServer = data['mqtt_server']
# print(mqttServer)
localTopic = data['topic']
print(localTopic)
setDatatoVP(2500, (localTopic + "           "))

#retreve server and topic
# with open("data.json", 'r') as file:
#     data = json.load(file)
# mqttServer = data['server']
# print(mqttServer)
# localTopic = data['topic']
# print(localTopic)

# topic generation
s = '/'
gen_topic_verify = (localTopic,'Skylark/SW/verified', machineId)
topic_verify = s.join(gen_topic_verify)
# print(topic_verify)
gen_topic_notverify = (localTopic,'Skylark/SW/notverified', machineId)
topic_notverify = s.join(gen_topic_notverify)
# print(topic_notverify)
gen_topic_success = (localTopic,'Skylark/SW/Succ', machineId)
topic_success = s.join(gen_topic_success)
# print(topic_success)
gen_topic_failed = (localTopic,'Skylark/SW/Err', machineId)
topic_failed = s.join(gen_topic_failed)
# print(topic_failed)
gen_topic_message = (localTopic,'Skylark/SW/msg', machineId)
topic_message = s.join(gen_topic_message)
# print(topic_message)
gen_topic_wifi = (localTopic,'Skylark/SW/wifi', machineId)
topic_wifi = s.join(gen_topic_wifi)
# print(topic_wifi)
 
    
def get_address(data):
    if len(str(data).split('\\')) >= 5:
        address = str(data).split('\\')[4][1:] + str(data).split('\\')[5][1:]
        return address
    else:
        return False
    
def connect_and_subscribe():
    global client_id, mqtt_server #, topic_send_verify, topic_setting, topic_success, topic_failed, topic_send_notverify
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_verify)
    client.subscribe(topic_success)
    client.subscribe(topic_failed)
    client.subscribe(topic_notverify)
    client.subscribe(topic_message)
    client.subscribe(topic_wifi)
    print('Connected to %s MQTT broker')
    pageSwitch(1)
    return client

# getting mqtt server ip
with open('data.json', 'r') as f:
    data = json.load(f)
    mqtt_server = data["mqtt_server"]
    print(mqtt_server)
setDatatoVP(3600, mqtt_server)

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

def sub_cb(topic, msg):
    print((topic, msg))
    global recieved, userid_check
    recieved +=1
    if topic == topic_verify.encode('utf-8'):
        empInfo = msg
        empInfo_str = str(empInfo.decode("utf-8"))
        print(empInfo_str)
#         global empName, empID
        global factory_name,employee_name,department_name,designation_name,floor_name,line_name
        factory_name,employee_name,department_name,designation_name,floor_name,line_name = empInfo_str.split(",")
        print(factory_name)
        print(employee_name)
        print(department_name)
        print(designation_name)
        print(floor_name)
        print(line_name)
        setDatatoVP(2300, factory_name+'   ')
        setDatatoVP(2050, employee_name+'   ')
        setDatatoVP(2100, department_name+'         ')
        setDatatoVP(2150, designation_name+'   ')
        setDatatoVP(2200, floor_name)
        setDatatoVP(2250, line_name+'      ')
        print("ID recognized")
        data_wifi = [0x5A, 0xA5, 0x07, 0x82, 0x56 , 0x00, 0x00, 0x01]
        print('data_wifi')
        print(data_wifi)
        dwinSerial.write(bytes(data_wifi))
        time.sleep(1)
        dwinSerial.write(bytes(data_wifi))
        userid_check = True
        global run
        run+=1
    elif topic == topic_notverify.encode('utf-8'):
        print("ID not recognized")
        global permission
#         permission = False
        userid_check = False
        pageSwitch(5)
        main()
        
    elif topic == topic_success.encode('utf-8'):
        tagInfo = msg
        tagInfo_str = str(tagInfo.decode("utf-8"))
        print(tagInfo_str)
        global machine_id,production_qty,hourly_target,hourly_average,total_target,achievement,efficiency
        machine_id,production_qty,hourly_target,total_target,hourly_average,achievement,efficiency = tagInfo_str.split(",")
        production_qty_list = [x for x in production_qty]
        production_qty_1 = production_qty_list[0]
        production_qty_2 = production_qty_list[1]
        production_qty_3 = production_qty_list[2]
        production_qty_4 = production_qty_list[3]
        print(machine_id)
        print(production_qty)
        print(production_qty_1)
        print(production_qty_2)
        print(hourly_target)
        print(hourly_average)
        print(total_target)
        print(achievement)
        print(efficiency)
        print("Success")
        setDatatoVP(2600, production_qty_1)
        setDatatoVP(2601, production_qty_2)
        setDatatoVP(2602, production_qty_3)
        setDatatoVP(2603, production_qty_4)
        setDatatoVP(3000, (' '+hourly_target+'  '))
        setDatatoVP(3010, hourly_average)
        setDatatoVP(3020, total_target)
        achievement_1 = int(achievement)
        efficiency_1 = int(efficiency)
        data1 = [0x5A, 0xA5, 0x07, 0x82, 0x33 , 0x00, 0x00, achievement_1, 0x00, efficiency_1]
#         data1 = [0x5A, 0xA5, 0x05, 0x82, 0x33 , 0x00, 0x00, achievement_1]
        print('data1')
        print(data1)
        dwinSerial.write(bytes(data1))
        pageSwitch(7)
        time.sleep(1)
        pageSwitch(6)
        
    elif topic == topic_failed.encode('utf-8'):
        print("Invalid Card")
        pageSwitch(8)
        time.sleep(0.5)
        pageSwitch(6)
        
    elif topic == topic_message.encode('utf-8'):
        print("Message Received")
        receivedMsgInfo = msg
        global receivedMsgInfo_str
        receivedMsgInfo_str = str(receivedMsgInfo.decode("utf-8"))
        pageSwitch(30)
        setDatatoVP(4900, receivedMsgInfo_str)
    
    elif topic == topic_wifi.encode('utf-8'):
        print("wifi changed")
        wifiInfo = msg
        wifiInfo_str = str(wifiInfo.decode("utf-8"))
        global changed_ssid, changed_pass, wifi_machineID
        changed_ssid, changed_pass, wifi_machineID = wifiInfo_str.split(",")
        print(changed_ssid)
        print(changed_pass)
        profiles = wm.read_credentials()
        profiles = {changed_ssid:changed_pass}
# #       profiles['Aurjon_new'] = '01072008' 
        wm.write_credentials(profiles)
        wm.disconnect()
        wm.connect()
        profiles = wm.read_credentials()
        machine.reset()
#         pageSwitch(30)

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()


def main():
    global run, recieved
    recieved = 0
    run = 0
    card_login = 0
    while run == 0:
        try:
            if dwinSerial.any():
                check = dwinSerial.read()
                print(check)
                address = get_address(check)
                print(address)
#                 if get_address(check) == '1200':
#                     edit()
                if get_address(check) == '1000':
                    card_login = 1
                    while True:
                        if dwinSerial.any():
                            userid_read = str(dwinSerial.read()).split('\\')[6][3:]
                            print(userid_read)
                            if not userid_read:
                                print("The user id is empty.")
                                userid_read = ""
                                pageSwitch(5)
                                break
                            else:
                                print("The user id have values.")
                                global pub_empID, userid_check
                                pageSwitch(4)
                                pub_empID = f"{userid_read}"
                                pub_empID_MID = f"{userid_read},{machineId}"
                                gen_topic_login = (localTopic,'Skylark/SW/Login', machineId)
                                s = '/'
                                topic_login = s.join(gen_topic_login)
                                client.publish(topic_login.encode('utf-8'), pub_empID_MID)
                                global recieved
                                while recieved == 0:
                                    recieved = 0
                                    client.check_msg()
                            break
                        
#                 if get_address(check) == '1001':
#                     while True:
#                         if dwinSerial.any():
#                             sent = dwinSerial.read()
#                             print(sent)
# #                             address = get_address(sent)
#                             if len(str(sent).split('\\')) >= 5:
#                                 addressNew = str(sent).split('\\')[4]
#                                 print(addressNew)
#                                 if addressNew == 'x10P':
#                                     global ssid_new, password_new
#                                     passCode_entry = str(sent).split('\\')[5][3:]
#                                     print('New passCode_entry',passCode_entry)
#     #                                 password = ''
#                                     if not passCode_entry:
#                                         print("The passCode_entry is empty.")
#                                         passCode_entry = ""
#                                         pageSwitch(1)
#                                         break
#                                     else:
#     #                                     with open("data.json", 'r') as f:
#     #                                         data = json.load(f)
#     #                                         data["passCode"] = passCode
#                                         passCode = '4444'
#                                         if passCode_entry == passCode:
#                                             print("Enter Settings")
#                                             pageSwitch(39)
#                                             main()
        
#                                             break

            if card_login == 0:
                card_read = rfidSerial.read()
                if card_read:
                    global userid_check
                    userid_check = None
                    pageSwitch(4)
                    card_read_hex = card_read.split()[0].decode('utf-8')[-7:]
                    userid_read = str(int(card_read_hex, 16))
                    global pub_empID
                    pub_empID = f"{userid_read}"
                    pub_empID_MID = f"{userid_read},{machineId}"
                    gen_topic_login = (localTopic,'Skylark/SW/Login', machineId)
                    s = '/'
                    topic_login = s.join(gen_topic_login)
                    client.publish(topic_login.encode('utf-8'), pub_empID_MID)
                    global recieved
                    while recieved == 0:
                        recieved = 0
                        client.check_msg()
        except OSError as e:
            restart_and_reconnect()
    if userid_check:
        userid = userid_read
        pageSwitch(6)
        with open("data.json", 'r') as f:
            data = json.load(f)
        data["user_id"] = userid
        with open("data.json", 'w') as f:
            json.dump(data, f)
        print("The device is now in operating state")
        print("Type 'exit' to shut the device down")
        userid_check = False
        

main()


while True:
    wlan = network.WLAN(network.STA_IF) # create station interface
    wlan.active(True)       # activate the interface
    if not wlan.isconnected():
        data_wifi = [0x5A, 0xA5, 0x07, 0x82, 0x56 , 0x00, 0x00, 0x00]
        dwinSerial.write(bytes(data_wifi))
        time.sleep(5)
        pageSwitch(15)
        machine.reset()
    client.check_msg()
    if dwinSerial.any():
        check = dwinSerial.read()
        print(check)
        print(get_address(check))
        if len(str(check).split('\\')) >= 5:
            if get_address(check) == '1200':
                pageSwitch(38)
                setDatatoVP(1001, '**********')
                # back button needs a return keycode
                while True:
                    if dwinSerial.any():
                        sent = dwinSerial.read()
                        print(sent)
                        address = get_address(sent)
                        print(address)
#                         setDatatoVP(1001, '*****')
#                         if dwinSerial.any():
#                             sent = dwinSerial.read()
#                             print(sent)
# #                             address = get_address(sent)
#                             if len(str(sent).split('\\')) >= 5:
#                                 addressNew = str(sent).split('\\')[4]
#                                 print(addressNew)
                        if address == '1001':
                            global ssid_new, password_new
                            passCode_entry = str(sent).split('\\')[6][3:]
                            print('New passCode_entry',passCode_entry)
#                             setDatatoVP(1001, '*****')
#                                 password = ''
                            if not passCode_entry:
                                print("The passCode_entry is empty.")
                                passCode_entry = ""
                                pageSwitch(40)
                                time.sleep(1)
                                pageSwitch(6)
                                break
                            else:
#                                     with open("data.json", 'r') as f:
#                                         data = json.load(f)
#                                         data["passCode"] = passCode
                                passCode = '3011'
                                if passCode_entry == passCode:
                                    print("Enter Settings")
                                    pageSwitch(11)
                                else:
                                    print('wrong passcode')
                                    pageSwitch(40)
                                    time.sleep(1)
                                    pageSwitch(6)
                                    break
                                    
                        if address == '1400':
                            global ssid_new, password_new
                            ssid_new = str(sent).split('\\')[6][3:]
                            print('New ssid',ssid_new)
                            password = ''
                            if not ssid_new:
                                print("The ssid is empty.")
                                ssid_new = ""
                                pageSwitch(6)
                                break
                            else:
                                while True:
                                    if dwinSerial.any():
                                        data = dwinSerial.read()
                                        print(data)
                                        if get_address(data) == '1500':
                                            global password_new
                                            password_new = str(data).split('\\')[6][3:]
                                            print('1500 password',password_new)
                                            if not password_new:
                                                print("The password is empty.")
                                                password_new = ""
                                                pageSwitch(6)
                                                break
                                            else:
                                                print('New ssid',ssid_new)
                                                pub_newWifi = f"{ssid_new},{password_new},{machineId}"
                                                print(pub_newWifi)
                                                gen_topic_newWifi = (localTopic,'Skylark/SW/newWifi', machineId)
                                                s = '/'
                                                topic_newWifi = s.join(gen_topic_newWifi)
                                                print(topic_newWifi)
                                                client.publish(topic_newWifi.encode('utf-8'), pub_newWifi)
                                                time.sleep(2)
                                                pageSwitch(32)
                                                client.check_msg()
                                break

                        if address == '1700':
                            with open("data.json", "r") as f:
                                data = json.load(f)
                            del data["mqtt_server"]
                            data["mqtt_server"] = str(sent).split('\\')[6][3:]
                            if not data["mqtt_server"]:
                                print("The mqtt_server is empty.")
                                data["mqtt_server"] = ""
                                pageSwitch(6)
                                break
                            else:
                                with open("data.json", "w") as f:
                                    json.dump(data, f)
                                
                                with open("data.json", "r") as f:
                                    data = json.load(f)
                                    mqtt_server = data["mqtt_server"]
    #                             try:
    #                                 client = connect_and_subscribe()
    #                             except OSError as e:
    #                               restart_and_reconnect()
                                pageSwitch(33)
                                machine.reset()
                            
                        if address == '1900':
                            with open("data.json", "r") as f:
                                data = json.load(f)
                            del data['topic']
                            data['topic'] = str(sent).split('\\')[6][3:]
                            if not data['topic']:
                                print("The topic is empty.")
                                data['topic'] = ""
                                pageSwitch(6)
                                break
                            else:
                                with open("data.json", "w") as f:
                                    json.dump(data, f)
                                
                                with open("data.json", "r") as f:
                                    data = json.load(f)
                                    topic = data['topic']
    #                             try:
    #                                 client = connect_and_subscribe()
    #                             except OSError as e:
    #                               restart_and_reconnect()
                                pageSwitch(37)
                                machine.reset()
                            break
                        if address == '1600':
                            break
            if get_address(check) == '1800':
                print('Broken Needle')
                pub_brokenNeedle_MID = f"{pub_empID},{'Broken Needle'},{machineId}"
                gen_topic_help = (localTopic,'Skylark/SW/help', machineId)
                s = '/'
                topic_help = s.join(gen_topic_help)
                client.publish(topic_help.encode('utf-8'), pub_brokenNeedle_MID)
                time.sleep(1)
                pageSwitch(6)
            if get_address(check) == '1801':
                print('Machine Malfunction')
                pub_machineMalfunction_MID = f"{pub_empID},{'Machine Malfunction'},{machineId}"
                gen_topic_help = (localTopic,'Skylark/SW/help', machineId)
                s = '/'
                topic_help = s.join(gen_topic_help)
                client.publish(topic_help.encode('utf-8'), pub_machineMalfunction_MID)
                time.sleep(1)
                pageSwitch(6)
            if get_address(check) == '1802':
                print('Feeling Unwell')
                pub_feelingUnwell_MID = f"{pub_empID},{'Feeling Unwell'},{machineId}"
                gen_topic_help = (localTopic,'Skylark/SW/help', machineId)
                s = '/'
                topic_help = s.join(gen_topic_help)
                client.publish(topic_help.encode('utf-8'), pub_feelingUnwell_MID)
                time.sleep(1)
                pageSwitch(6)
            if get_address(check) == '1803':
                print('Need Expert Assistance')
                pub_needExpertAssistance_MID = f"{pub_empID},{'Need Expert Assistance'},{machineId}"
                gen_topic_help = (localTopic,'Skylark/SW/help', machineId)
                s = '/'
                topic_help = s.join(gen_topic_help)
                client.publish(topic_help.encode('utf-8'), pub_needExpertAssistance_MID)
                time.sleep(1)
                pageSwitch(6)
            if get_address(check) == '1804':
                print('Other')
                pub_other_MID = f"{pub_empID},{'Other'},{machineId}"
                gen_topic_help = (localTopic,'Skylark/SW/help', machineId)
                s = '/'
                topic_help = s.join(gen_topic_help)
                client.publish(topic_help.encode('utf-8'), pub_other_MID)
                time.sleep(1)
                pageSwitch(6)
            if get_address(check) == '1300':
                print("logged out")
                pageSwitch(1)
                gen_topic_logout = (localTopic,'Skylark/SW/Logout', machineId)
                s = '/'
                topic_logout = s.join(gen_topic_logout)
                pub_msg_logOut = "loggedOut"
                client.publish(topic_logout.encode('utf-8'), pub_msg_logOut)
                with open("data.json", 'r') as f:
                    data = json.load(f)
                del data["user_id"]
                with open("data.json", 'w') as w:
                    json.dump(data, w)
                pageSwitch(1)
                main()
    card_read = rfidSerial.read()
    if card_read:
        card_read_hex = card_read.split()[0].decode('utf-8')[-7:]
        userid_read = int(card_read_hex, 16)
        user_query = userid_read
        with open("data.json", 'r') as f:
            data = json.load(f)
        if int(userid_read) == int(data["user_id"]):
            print("logged out")
            pageSwitch(1)
            gen_topic_logout = (localTopic,'Skylark/SW/Logout', machineId)
            s = '/'
            topic_logout = s.join(gen_topic_logout)
            pub_msg_logOut = "loggedOut"
            client.publish(topic_logout.encode('utf-8'), pub_msg_logOut)
            with open("data.json", 'r') as f:
                data = json.load(f)
            del data["user_id"]
            with open("data.json", 'w') as w:
                json.dump(data, w)
            main()
        else:
            pub_msg = f"{pub_empID}, {user_query}, {machineId}"
            gen_topic_tag = (localTopic,'Skylark/tag', machineId)
            s = '/'
            topic_tag = s.join(gen_topic_tag)
            print(topic_tag)
            client.publish(topic_tag.encode('utf-8'), pub_msg)
    


