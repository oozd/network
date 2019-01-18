import socket
import hashlib
import sys
import time
import threading
from threading import Thread, Lock

### Listen IP and Ports ###

router1ListenIP = "10.10.3.2" 
router1ListenPort = 8000

router2ListenIP = "10.10.5.2"
router2ListenPort = 8000


### Send IP and Ports ###

router1SendIP = "10.10.2.1"
router1SendPort = 8000

router2SendIP = "10.10.4.1"
router2SendPort = 8000


### Listening Sockets ###

router1ListenSocket = socket.socket(socket.AF_INET, # socket to listen R1
                     socket.SOCK_DGRAM) # UDP
router1ListenSocket.bind((router1ListenIP, router1ListenPort))


router2ListenSocket = socket.socket(socket.AF_INET, # socket to listen R2
                     socket.SOCK_DGRAM) # UDP
router2ListenSocket.bind((router2ListenIP, router2ListenPort))


### Sending Sockets ###

router1SendSocket = socket.socket(socket.AF_INET, # socket to send R1
                     socket.SOCK_DGRAM) # UDP

router2SendSocket = socket.socket(socket.AF_INET, # socket to send R2
                     socket.SOCK_DGRAM) # UDP

window = [-1] * 1000000 # it will hold ack values that is sent to the broker. If 5 (windowsize) ack is ready
						# then the next ack sent. it is blocking the destination to send too much ack to broker.
windowSize = 5 # window size is used for the case mentioned one line above.
windowPlace = 1 # ack values starts with 1.
windowLock = Lock() # used to lock window when windowplace is moved
fileLock = Lock() # used when writing to file. If router1 router2 both writes, it allows us to escape from data corruption
fileList = [""] * 1000000 # empty file array
finish = False # used to terminate router1 and router2 listening threads


def checksumR1(packet): # gets packet from r1, calculate it's data part's checksum and compares it with the checksum field.
	if packet[500:532] == hashlib.md5(packet[0:500]).hexdigest():
		return True
	else:
		return False # return true if checksum is correct otherwise false for router1's data

def checksumR2(packet): # gets packet from r1, calculate it's data part's checksum and compares it with the checksum field.
	if packet[500:532] == hashlib.md5(packet[0:500]).hexdigest():
		return True
	else:
		return False # return true if checksum is correct otherwise false for router2's data

def calcAck(ACK): # calculate ack string to send

	if ACK < 10:
		ACK = "0000" + str(ACK)
	elif ACK < 100:
		ACK = "000" + str(ACK)
	elif ACK < 1000:
		ACK = "00" + str(ACK)
	elif ACK < 10000:
		ACK = "0" + str(ACK)
	else:
		ACK = "" + str(ACK)

	return  ACK 

def isWindowFilled(): # checks if 5 packets arrived. If so windowplace is moved. New ack will be send.
	global window
	global windowSize
	for val in window[ windowPlace : windowPlace + windowSize ]: # loop 5 packets
		if val == -1: # if not filled with an ack then it is -1. 
			return False
	return True # window is filled return true.

def listenR1(): # listen r1 function until a "FINISH" packet arrives
	global window
	global windowSize
	global windowPlace 
	global router1ListenSocket
	global router1SendSocket
	global fileList
	global finish
	while finish != True:
		router1Data, addr = router1ListenSocket.recvfrom(537) # receive from r1
		if(router1Data[0:6] == "FINISH"): # check if it is finish packet.
			for i in range (0,5): # send finish received as "FINIS" text. 5 times. so packet loss can be fixed for finishing cases.
				router1SendSocket.sendto("FINIS", (router1SendIP, router1SendPort)) # 
			finish = True
		else:
			if checksumR1(router1Data): # checksum of packet is true
				router1Ack = int(router1Data[532:537]) + 1 # get sequence number and increment to find the ack
				window[router1Ack] = router1Ack #  write the ack to the window
				fileLock.acquire() # lock the file for escaping from data corruption
				fileList[router1Ack - 1] = router1Data[0:500] # gathering file It allows us to escape from reordering situations
				fileLock.release() # release the file.
				#print "Router1 ACK: ", router1Ack
				windowLock.acquire() # lock the window
				if isWindowFilled(): # if window is filled with 5 acks
					newACK = calcAck(windowPlace + windowSize -1) # then the new ack can be send to the broker.
					# print "newACK R1: ", newACK
					router1SendSocket.sendto(newACK, (router1SendIP, router1SendPort)) # send ack through r1
					windowPlace = windowPlace + windowSize # move the window.
				windowLock.release() # release the window

def listenR2(): # listen r2 function until a "FINISH" packet arrives
	global window
	global windowSize
	global windowPlace 
	global router2ListenSocket
	global router2SendSocket
	global fileList 
	global finish
	while finish != True:
		router2Data, addr = router2ListenSocket.recvfrom(537) # receive from r2
		if(router2Data[0:6] == "FINISH"): # check if it is finish packet.
			for i in range (0,5): # send finish received as "FINIS" text. 5 times. so packet loss can be fixed for finishing cases.
				router2SendSocket.sendto("FINIS", (router2SendIP, router2SendPort)) # increase the ackR1
			finish = True
		else:
			if checksumR2(router2Data): # checksum of packet is true
				router2Ack = int(router2Data[532:537]) + 1 # get sequence number and increment to find the ack
				window[router2Ack] = router2Ack #  write the ack to the window
				fileLock.acquire() # lock the file for escaping from data corruption
				fileList[router2Ack - 1] = router2Data[0:500] # gathering file It allows us to escape from reordering situations
				fileLock.release() # release the file.
				# print "Router1 ACK: ", router1Ack
				windowLock.acquire() # lock the window
				if isWindowFilled(): # if window is filled with 5 acks
					#print "Window is Filled R1" 
					newACK = calcAck(windowPlace + windowSize -1) # then the new ack can be send to the broker.
					# print "newACK R2: ", newACK
					router2SendSocket.sendto(newACK, (router2SendIP, router2SendPort)) # send ack through r2
					windowPlace = windowPlace + windowSize # move the window.
				windowLock.release() # release the window

def main():
	file = ""
	global fileList

	threads = []
	thread1 = threading.Thread(target = listenR1, args = ())
	thread2 = threading.Thread(target = listenR2, args = ())

	thread1.start()
	thread2.start()

	threads.append(thread1)
	threads.append(thread2)

	for t in threads:
		t.join() # wait until threads finish.

	print "END OF DEST"
	for part in fileList:
		if part != "":
			file = file + part # gather the file parts.


	print hashlib.md5(file).hexdigest() # used to compare the file with source.

if __name__ == '__main__':
	main()