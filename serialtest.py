import serial
import subprocess
import os
import sys
from os import listdir
from os.path import isfile, join
from bitstring import BitArray
from time import sleep

'''
free chars
k,4,5,6,7
'''

port = serial.Serial("/dev/ttyUSB0", baudrate=19200, timeout=3.0)

cam = None
address = '11000001'

init = False
video = 0
alarm = 0
x_min = 0
x_max = 1024
y_min = 0
y_max = 768
last_file_date = None


def initialize(received_packet):
    print("In init")
    global init
    init = True
    
    
def video_on(received_packet):
    print("In video_on")
    global video
    video = 1
    
    
def alarm_on(received_packet):
    print("In alarm_on")
    global alarm
    alarm = 1
    
    
def whole_scope(received_packet):
    print("In whole_scope")
    global x_min, x_max, y_min, y_max
    x_min = 0
    x_max = 640
    y_min = 0
    y_max = 480
    
    
def right_scope(received_packet):
    print("In rigt_scope")
    global x_min, x_max, y_min, y_max
    x_min = 320
    x_max = 640
    y_min = 0
    y_max = 480
    
    
def left_scope(received_packet):
    print("In left_scope")
    global x_min, x_max, y_min, y_max
    x_min = 0
    x_max = 320
    y_min = 0
    y_max = 480
    
    
def upper_scope(received_packet):
    print("In upper_scope")
    global x_min, x_max, y_min, y_max
    x_min = 0
    x_max = 640
    y_min = 0
    y_max = 240
    
    
def down_scope(received_packet):
    print("In down_scope")
    global x_min, x_max, y_min, y_max
    x_min = 0
    x_max = 640
    y_min = 240
    y_max = 480
    
'''
def send_coords(received_packet):
    files = [f for f in listdir('./movecords/')]
    files = [f for f in files if f[-5] == 'V']
    
    files = sorted(files)
    packet_to_send = []
    packet_to_send.append(received_packet[0])
    packet_to_send.append(received_packet[1])
    packet_to_send.append(received_packet[2])
    
    file = open('./movecords/' + files[0])
    data = file.read()
    print(data)
    data = data.split()
    length = len(data)
    packet_to_send.append(length)
    packet_to_send.extend(map(int, data))
    
        
    crc = crc8(packet_to_send[1:])
    
    packet_to_send.append(crc)
    
    send_byte(packet_to_send)
'''    
    
    
    
def send_byte(packet):
    
    new_list = []
    new_list.append(packet[0])
    for intt in packet[1:]:
        if intt == 125:
            new_list.append(125)
            new_list.append(93)
        elif intt == 126:
            new_list.append(125)
            new_list.append(94)
        else:new_list.append(intt)
        
    port.write(bytes([int(i) for i in new_list]))
    
    
def start(received_packet):
    global cam, init
    global x_min, x_max, y_min, y_max
    global video, alarm
    if cam != None:
        cam.kill()
    cam = subprocess.Popen(["python3", "record.py", "--fun", "motion-detection", "-x", str(x_min), str(x_max),
                            "-y", str(y_min), str(y_max), "-v", str(video), "-a", str(alarm)])
    init = False
    
    
def quit(received_packet):
    print("In quit")
    global cam, init, video, alarm, x_min, x_max, y_min, y_max
    cam.kill()
    cam = None
    init = False
    video = 0
    alarm = 0
    x_min = 0
    x_max = 640
    y_min = 0
    y_max = 480


def set_roi(received_packet):
    global x_min, x_max, y_min, y_max
    x_min, x_max, y_min, y_max = received_packet[4], received_packet[5], received_packet[6], received_packet[7]
    x_min  =  int(x_min / 255 * 640)
    x_max  =  int(x_max / 255 * 640)
    y_min  =  int(y_min / 255 * 480)
    y_max  =  int(y_max / 255 * 480)
    
    print("X_MIN " + str(x_min))
    print("X_MAX " + str(x_max))
    print("Y_MIN " + str(y_min))
    print("Y_MAX " + str(y_max))
    
def delete_sent_cords(received_packet):
    files = [f for f in listdir('./movecords/')]
    files = [f for f in files if f[-5] != 'V']
    for file in files:
        file_path = os.path.join('./movecords', file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
            

'''
TODO
len(str_packet) > 1 byte
'''
def switch_fun(str_packet, received_packet):
    
    if len(received_packet) > 6:
        set_roi(received_packet)
        return
    
    func = {
        '00000001' : initialize,
        '00000100' : video_on,
        '00000101' : alarm_on,
        '00001000' : whole_scope,
        '00001001' : left_scope,
        '00001010' : right_scope,
        '00001011' : upper_scope,
        '00001100' : down_scope,
        '00000000' : quit,
        '00000110' : start,
        '11100001' : send_cords,
        '11100010' : delete_sent_cords,
        }
    
    func[str_packet](received_packet)

    

def send_cords(received_packet):
    files = [f for f in listdir('./movecords/')]
    files = [f for f in files if f[-5] == 'V']
    files = sorted(files, reverse=True)
    for file in files:
        packet_to_send = []
        packet_to_send.append(received_packet[0])
        packet_to_send.append(received_packet[1])
        packet_to_send.append(received_packet[2])
        
        file_contest = open('./movecords/' + file)
        os.rename('./movecords/'+ file, './movecords/'+ file[:-5] + "S.txt")
        data = file_contest.read()
        print(data)
        data = data.split()
        length = len(data)
        packet_to_send.append(length)
        packet_to_send.extend(map(int, data))
        
            
        crc = crc8(packet_to_send[1:])
        
        packet_to_send.append(crc)

        #print(bytes([int(i) for i in new_list]))
        
        send_byte(packet_to_send)
        
        sleep(0.5)
        
        
        

def receive_packet():
    index = 0
    
    while True:
        rcv = (port.read())
        
        comp_str = b''
        received = False;
        if rcv == comp_str:
            if index > 0:
                proccess_packet(received_signal, received_hex)
            index = 0
            rcv = ' ';
        
        else:
            received = True
            if index == 0:
                received_signal = []
                received_hex = []
        if received:
            print(rcv)
            if index == 0:
                print("Start received bin data")

            print("It is part number: " + str(index + 1))
            index = index + 1
            print(bin(ord(rcv))[2:].zfill(8))
            print(hex(ord(rcv))[2:].zfill(2))
            received_hex.append(int.from_bytes(rcv, byteorder=sys.byteorder))
            received_signal.append(bin(ord(rcv))[2:].zfill(8))
         
        else:
           print("No data received")
    

def crc8(data):
    crc = 0
    for i in range(len(data)):
        byte = data[i]
        for b in range(8):
            fb_bit = (crc ^ byte) & 0x01
            if fb_bit == 0x01:
                crc = crc ^ 0x18
            crc = (crc >> 1) & 0x7f
            if fb_bit == 0x01:
                crc = crc | 0x80
            byte = byte >> 1
    return crc


def proccess_packet(packet, received_hex):
    global address
    global cam
    global init
    print(packet)
    crc_packet = packet[:-1]
    crc_packet = crc_packet[1:]

    received_hex = received_hex[:-1]
    received_hex[1], received_hex[2] = received_hex[2], received_hex[1]
    crc = crc8(received_hex[1:])

    received_hex.append(crc)

    send_array = []
    for byte in received_hex:
        send_array.append("{0:b}".format(byte).zfill(8))
        
    print(str(received_hex))
    print(bytes([int(i) for i in received_hex]))
    ##port.write(bytes([int(i) for i in received_hex]))
    
    print("{0:b}".format(crc))
    crc = crc.to_bytes((crc.bit_length() + 7) // 8, 'big')

    #print(hex(received_hex[5])[2:].zfill(2))
    

    
    #print("Address: " + str(address))
    #print("Packet[1]: " + packet[1])
    if address != packet[1]: return
    
    #for sending
    #packet[1], packet[2] = packet[2], packet[1]
    as_string = ''
    
    #TODO encode to dec
    len = packet[3]
    data_as_string = packet[4]
    
    if init == True:
        switch_fun(data_as_string, received_hex)
    else:
        if data_as_string == '00000001':
            initialize(received_hex)
            
        elif data_as_string == '00000000':
            if cam != None:
                quit(received_hex)
                
    #choose mode
            
    #port.write(str.encode(asstring))
    
        
        
receive_packet()
    
    