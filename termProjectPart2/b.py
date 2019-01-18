import socket
import hashlib
import threading
import sys
import time
from threading import Thread, Lock

### Listen IP and Ports ###

#TCP_IP = "127.0.0.1"
TCP_IP = "10.10.1.2"	
TCP_PORT = 8080			

router1ListenIP = "10.10.2.1"
router1ListenPort = 8000

router2ListenIP = "10.10.4.1"
router2ListenPort = 8000

### Send IP and Ports ###

router1SendIP = "10.10.3.2" #dest interface
router1SendPort = 8000

router2SendIP = "10.10.5.2" #dest interface
router2SendPort = 8000

### Listening Sockets ###

sourceListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
sourceListenSocket.bind((TCP_IP, TCP_PORT)) # bind itself
sourceListenSocket.listen(1) # start to listen
conn, addr = sourceListenSocket.accept() # accept connections


router1ListenSocket = socket.socket(socket.AF_INET, # Router1 listen socket 
                     socket.SOCK_DGRAM) # UDP
router1ListenSocket.bind((router1ListenIP, router1ListenPort))


router2ListenSocket = socket.socket(socket.AF_INET, # Router2 listen socket
                     socket.SOCK_DGRAM) # UDP
router2ListenSocket.bind((router2ListenIP, router2ListenPort))

### Sending Sockets ###

router1SendSocket = socket.socket(socket.AF_INET, # Router1 send socket
                     socket.SOCK_DGRAM) # UDP

router2SendSocket = socket.socket(socket.AF_INET, # Router 2 send socket
                     socket.SOCK_DGRAM) # UDP

seq = 0 # sequence number of packets that goes to destination over r1 and r2
windowSize = 5 # window size is 5. never changes
windowPlace = 0 # window place is starts with 0 incremented with coming ack packets later

packetArr = [] # keeps packets that come from source

router1Ack = 0 # router's ack's. first ack will have value of 1. which means I get the 0. seq number packet. I want the next one which is 1.
router2Ack = 0

finish = False # used to finish inner loop of sending packets to destination
fullFinish = False # used to finish the outer loop of sending packets to destination
R1R2Finish = False # used to finish the R1 and R2 threads

windowPlaceLock = Lock() # mutex that used when playing with windowPlaces


def makePacket(packet): #  This function calculates packet's checksum and sequence number and returns the created packet
	global seq
	checksum = hashlib.md5(packet).hexdigest()

	if seq < 10:
		packet = packet + checksum + "0000" + str(seq)
	elif seq < 100:
		packet = packet + checksum + "000" + str(seq)
	elif seq < 1000:
		packet = packet + checksum + "00" + str(seq)
	elif seq < 10000:
		packet = packet + checksum + "0" + str(seq)
	else:
		packet = packet + checksum + "" + str(seq)

	seq = seq + 1

	return packet

def listenSource(): # Listens the source and puts packets to packetArr
	global packetArr
	while 1:
		sourceData = conn.recv(500, socket.MSG_WAITALL) # receive from source 
		if sourceData != "": # continue as long as source sends packets
			newPacket = makePacket(sourceData)
			packetArr.append(newPacket)
		else: # source finished to transfer packets
			packetArr.append("")
			#print "packetArr's Len: ", len(packetArr)
			sourceListenSocket.close() # terminate the connection with source
			break 

def listenR1(): # R1 listener function
	global windowPlace
	global windowSize
	global R1R2Finish
	global finish
	global fullFinish
	global router1Ack
	while R1R2Finish != True: 
		router1AckStr, addr = router1ListenSocket.recvfrom(5) # receive ack from r1
		if router1AckStr == "FINIS": # if finish ac is received terminate the loop
			R1R2Finish = True
			break
		router1Ack = int(router1AckStr) # if not finish cast it to int
		windowPlaceLock.acquire() # playing with windowplace we should use mutex
		if router1Ack > windowPlace + windowSize -1: # if the ack is greater than the last packets index than windowplace should be moved
			windowPlace = windowPlace + windowSize # slide the window place by 5.
		windowPlaceLock.release() #  release the lock.
		

def listenR2(): # R2 listener function
	global windowPlace
	global windowSize
	global R1R2Finish
	global finish
	global fullFinish
	global router2Ack

	while R1R2Finish != True:
		router2AckStr, addr = router2ListenSocket.recvfrom(5) # receive ack from r2
		if router2AckStr == "FINIS": # if finish ac is received terminate the loop
			R1R2Finish = True
			break
		router2Ack = int(router2AckStr) # if not finish cast it to int
		windowPlaceLock.acquire() # playing with windowplace we should use mutex
		if router2Ack > windowPlace + windowSize -1: # if the ack is greater than the last packets index than windowplace should be moved
			windowPlace = windowPlace + windowSize # slide the window place by 5.
		windowPlaceLock.release() # release the lock.

def sendPackets():
	global packetArr
	global windowPlace
	global windowSize
	global router1Ack
	global router2Ack
	global finish
	global fullFinish
	global R1R2Finish

	while fullFinish != True: # wait until enough packets arrived to start sending to destination
		if len(packetArr) > windowSize -1: # start to send at least an amount of window sized packets arrived
			while finish != True: # send packets 
				for packet in packetArr[windowPlace : windowPlace + windowSize]:
					if packet != "": # packet exists
						seq = int(packet[532:537]) 
						if(seq % 2 == 0):
							router1SendSocket.sendto(packet, (router1SendIP, router1SendPort)) # send to r1
						else:
							router2SendSocket.sendto(packet, (router2SendIP, router2SendPort)) # send to r2
					else:
						#print "FINISH PACKET ARRIVED AT BROKER" # finish packet is arrived from packetArr
						finish = True # finish inner loop
						fullFinish = True # finish outer loop
						R1R2Finish  = True # finish R1 and R2 threads
						for i in range (0,5): # send finish packets to r1 and r2. It is sent 5 times for each in case of packet loss happens.
							router1SendSocket.sendto("FINISH", (router1SendIP, router1SendPort)) # send to r1
							router2SendSocket.sendto("FINISH", (router2SendIP, router2SendPort)) # send to r2
						break
				time.sleep(0.05) # some kind of timeout. If an ack is arrived with bigger than the windowplace+windowsize-1 then the windowplace is moved.
				# otherwise the current 5 packets sent again.
							

def main():
	threads = []

	thread0 = threading.Thread(target = sendPackets, args = ())
	thread1 = threading.Thread(target = listenR1, args = ())
	thread2 = threading.Thread(target = listenR2, args = ())

	threads.append(thread0) 
	threads.append(thread1)
	threads.append(thread2)

	
	thread0.start() # start to send packets to desination
	thread1.start() # start to listen R1
	thread2.start() # start to listen R2
	listenSource()
	

	for t in threads:
		t.join() # wait the threads finish

if __name__ == '__main__':
	main()