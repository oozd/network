import socket
import hashlib
import sys
import os
import time
from random import randint
import subprocess

TCP_IP = "10.10.1.2"	# brokers IP
TCP_PORT = 8080			# brokers port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creates tcp socket
s.connect((TCP_IP, TCP_PORT)) # connect it to broker ip and port


def main():
	file = open("input.txt", "r") # open the given file 
	fileString = file.read() # write the file to a string

	fileSize = sys.getsizeof(fileString) # 5 000 037 bytes
	packetSize = 500 # 500 bytes of packets
	idx = 0 # use while sending file packet by packet
	currentSize = fileSize

	while(currentSize > packetSize): # send file 

		currentSize = currentSize - packetSize 
		
		s.send(fileString[idx*500 : idx*500 + 500]) # Send Packets 500 bytes each

		idx = idx + 1

	s.send("") # indicates finish packet

	s.close()


	print hashlib.md5(fileString).hexdigest() # used to check if the file transferred correctly. 
	# I compared it with the destination file

if __name__ == '__main__':
	main()
	
