import serial
import sys


port = serial.Serial("/dev/ttyUSB0", baudrate=19200, timeout=3.0)
address = '11000001'

def send_packet(data, dest):
    packet_to_send = []
    packet_to_send.append(126)
    packet_to_send.append(int(dest))
    packet_to_send.append(int(address, 2))
    packet_to_send.append(len(data))
    for unit in data:
        packet_to_send.append(int(unit))
        
    crc = crc8(packet_to_send[1:])
    packet_to_send.append(crc)
    
    send_byte(packet_to_send)


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
         
         
def main(argv):
    dest = argv[0]
    data = argv[1:]
    send_packet(data, dest)
         
if __name__ == "__main__":
    main(sys.argv[1:])