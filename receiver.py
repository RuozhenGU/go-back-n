import sys
from socket import *
from packet import *

#global
seqExpected = 0 #track the next expected sequence number

#receive the arguments
hostname = sys.argv[1]
emulatorUDP = sys.argv[2]
receiverUDP = sys.argv[3]
filename = sys.argv[4]

#open files for logging
seqLog = open('arrival.log','w')
receiveData = open(filename,'w')

#start the socket
receiver = socket(AF_INET, SOCK_DGRAM)
receiver.bind(('0.0.0.0', int(receiverUDP)))

emulatorAddress = (hostname, int(emulatorUDP))


#send the first ack = -1
receiver.sendto(packet.create_ack(-1).get_udp_data(), emulatorAddress)

#start receiving packets
while True:
    #get the packet
    packetReceived, _ = receiver.recvfrom(1024)
    # print("packet received")
    packetReceived = packet.parse_udp_data(packetReceived)
    #retrieve the parameters
    typeReceived = packetReceived.type
    seqReceived = packetReceived.seq_num
    dataReceived = packetReceived.data

    #log the sequence number
    seqLog.write(str(seqReceived) + '\n')
    # check if the sequence number received is correct
    if seqReceived == (seqExpected % 32):
        if typeReceived == 1: # data was received
            receiver.sendto(packet.create_ack(seqReceived).get_udp_data(), emulatorAddress)
            receiveData.write(dataReceived)
        elif typeReceived == 2: # EOT was received
            receiver.sendto(packet.create_eot(seqReceived).get_udp_data(), emulatorAddress) 
            break
        seqExpected += 1
    #not the expected sequence number
    else:
        receiver.sendto(packet.create_ack((seqExpected - 1) % 32).get_udp_data(), emulatorAddress)


#close the files 
seqLog.close()
receiveData.close()

#close connections
receiver.close()
