import sys
from socket import *
from packet import *
import _thread
import threading
import time

# global variables
packetList = [] #this is the list of all the packages to be sent
seqNumber = 0 #sequence number starts from 0
nPackets = 0 #counter for the number of packages
N = 10 #window size for GBN
base = 0 #base pointer for which package has been acked
windowSize = 0 #window size that would be updated later in case the number of packets left to send is less than N
mutex = threading.Lock() #lock to update the base
nextPacket = 0 # next packet to be sent
timer = -1 #timer for timeout
eotReceived = False # checks if the EOT received and kills the sender
timeout = 0.2 #timeout value 

#receive the arguments
hostname = sys.argv[1]
emulatorUDP = sys.argv[2]
senderUDP = sys.argv[3]
filename = sys.argv[4]

#open files for logging
seqLog = open('seqnum.log','w')
ackLog = open('ack.log','w')



def receiver(sender):
    #get the global values
    global mutex
    global base
    global timer
    #start receiving the ack
    while True:
        #get the packet
        packetReceived, _ = sender.recvfrom(1024)
        #package received
        packetReceived = packet.parse_udp_data(packetReceived)
        #get the parameters
        typeReceived = packetReceived.type
        seqReceived = packetReceived.seq_num
        dataReceived = packetReceived.data

        if (dataReceived == -1):
            # print("first ack received")
            break

        if (typeReceived == 2):
            # print("eot received")
            eotReceived = True
            break #this avoids writing to ack.log for eot packages
        #write the sequence number
        ackLog.write(str(seqReceived) + '\n')

        #get the package and update the base
        mutex.acquire()

        baseModulo = base % 32
        if seqReceived >= baseModulo and (seqReceived - baseModulo) < windowSize:
            base += seqReceived + 1 - baseModulo
            timer = -1
        elif baseModulo + windowSize >= 32 and seqReceived < baseModulo + windowSize - 32: #this means seqReceived was moduloed 32 but base was not
            base += seqReceived + 1 - baseModulo + 32
            timer = -1
        #stop the timer so it doesn't timeout 
        
        mutex.release()

#this is used when number of packages left to be sent is less than N
def calc_window_size(N, nPackets, base):
    return min(N, nPackets - base)





#read the file and create packets
with open(filename, 'r') as f:
    while True:
        buffer = f.read(packet.MAX_DATA_LENGTH)
        if not buffer:
            break
        packetList.append(packet.create_packet(seqNumber, buffer))
        seqNumber += 1
        nPackets += 1


#start the socket
sender = socket(AF_INET, SOCK_DGRAM)
sender.bind(('0.0.0.0', int(senderUDP)))


#start the thread to receive 
thread = _thread.start_new_thread(receiver, (sender,))

#get the window size and the emulator address
windowSize = calc_window_size(N, nPackets, base)
emulatorAddr = (hostname, int(emulatorUDP))

#start sending messages
while True:
    #end if end of file received already
    if eotReceived or base >= nPackets:
        break


    mutex.acquire()
    while nextPacket < base + windowSize and nextPacket < nPackets:
        sender.sendto(packetList[nextPacket].get_udp_data(), emulatorAddr)
        seqLog.write(str(nextPacket) + '\n')
        # print(nextPacket, base, windowSize, len(packetList), "inside the while loop\n")
        nextPacket += 1

    #start the time out and wait for the package
    if timer == -1:
        # print("timer started")
        timer = time.time()
        
    #timer is running and no timeout happened
    while timer != -1 and ((time.time() - timer) < timeout):
        # print("waiting for timer to stop")
        mutex.release()
        mutex.acquire()
    #the timer has stopped for one the 2 following
    if ((time.time() - timer) >= timeout):
    # if timeout happened
        #print timeout happened, sending everything again
        timer = -1 #stop the timer
        nextPacket = base
    else:
    #timer stopped because all acks were received
        windowSize = calc_window_size(N, nPackets, base)
    mutex.release()

#send the EOT
sender.sendto(packet.create_eot(nPackets).get_udp_data(), emulatorAddr)
seqLog.close()
ackLog.close()
