import serial
import os

port = serial.Serial("/dev/ttyUSB0", baudrate=19200, timeout=3.0)
send_port = serial.Serial("/dev/ttyAMA0", baudrate=19200, timeout=3.0)

def proccess_packet(packet):
    packet[1], packet[2] = packet[2], packet[1]
    asstring = ''
    for data in packet:
        asstring = asstring + data
        port.write(str.encode(data))
    print(asstring)
    port.write(str.encode(asstring))
    os.system("record.py --fun motion-detection -x 0 1024 -y 0 768")
    
index = 0

while True:
    rcv = (port.read())
    comp_str = b''
    
    received = False;
    if rcv == comp_str:
        if index > 0:
            proccess_packet(received_signal)
        index = 0
        rcv = ' ';
    
    else:
        received = True
        if index == 0:
            received_signal = []
    if received:
        if index == 0:
            print("Start received bin data")

        print("It is part number: " + str(index + 1))
        index = index + 1
        print(bin(ord(rcv))[2:].zfill(8))
        print(hex(ord(rcv))[2:].zfill(2))
        received_signal.append(bin(ord(rcv))[2:].zfill(8))
    
        
    else:
        print("No data received")
    