In this assignment, you are expected to examine TCP packages using Wireshark environment and exercising the basics of transport layer concepts on TCP protocol.
Specifications

You are expected to visit Assignment Webpage, (without https) observe the related TCP packets and answer some questions related to that query. The instructions are similar to the ones in the first Wireshark assignment. This time determine IP of the webpage server and filter the package list related to that IP.

After that follow the instructions and answer the questions below:

    What are the packet numbers (which appear in Wireshark program) of the packets used for 3-way handshake protocol that initiates the first TCP connection? What are the segment numbers of those packages and the port numbers used on client and server sides?
    What are the first 5 packet numbers and segment numbers of all TCP packets transferring the "wireshark_assignment2.png" image data? What are the packet numbers of corresponding ACK segments and the data amount they acknowledged? Draw a table which have packet number, segment number, ACK packet number, and ACKed data columns and fill the table with the required information.
    How long does it take to transfer "wireshark_assignment2.png" image data (from the time the first TCP data packet sent to the time the last acknowledgement received at the server side)? Show your work. Plot Round Trip Time - Time graph of related TCP packets. (Hint: Select one of those TCP segment in the "listing of captured packets" window that is being sent from the server to the client. Then select: Statistics->TCP Stream Graph- >Round Trip Time Graph.)
    Are there any retransmitted segments in your trace file? Justify your answer with respect to your Wireshark output monitoring.

Deliverables
You are expected to submit your answers as softcopy solution to "Wireshark Turnitin Assignment #2: Transport Layer" section and your filtered packet capture file (.pcap) to "Wireshark Assignment #2: Transport Layer - PCAP Submission" section before deadline. Please refer to the course syllabus for late submission terms and follow Odtuclass system for further announcements.