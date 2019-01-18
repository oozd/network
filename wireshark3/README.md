In this assignment, you are expected to examine ICMP packages using Wireshark environment and exercising the basics of network layer concepts.

Specifications

This assignment requires to work on GENI Environment. Please follow the steps below in order to generate the .pcap file for this assignment:

    Log in to GENI system and create new slice under the current project named as "Wireshark_e1234567" with your 7-digit student id number.
    Add resources in http://mountrouidoux.people.cofc.edu/CyberPaths/files/denialOfServiceLevel1.txt with url option. 
    Right click on Site and Select one of aggregates that is available and then reserve the resources.
    After reservation is completed in a while, connect each machine with ssh and run the following ping commands specified below:

    On attacker machine: ping victim
    On user machine: ping ovs
    Lastly, on ovs machine: sudo tcpdump -i any -s0 -w ws3.pcap

Download pcap file created in ovs machine with a command line file transfer program of your choice (scp, sftp ...). Open ws3.pcap file with Wireshark, filter captured list with protocol ICMP, and  follow the instructions and answer the questions below:

    What are the IP numbers of attacker, victim, user and ovs machines, respectively?
    Why an ICMP message does not need to have source and destination port numbers?
    List the wireshark sequence numbers of the first 5 request packets with their corresponding reply packets (if any).
    Examine the first ping request packet with its corresponding reply packet. What are the ICMP type and code numbers of each (request and reply) packets? How many bytes are the checksum, sequence number and identifier fields?
    Specify the TTL values of packets by means of source - destination address pairs and comment on the similarities and differences among TTL values.
    Put the screenshot of graphical illustration of resources and Details page (which opens by clicking "Details" at the bottom) in GENI Platform.

Deliverables
You are expected to submit your answers as softcopy solution to "Wireshark Turnitin Assignment #3: Network Layer" section and your filtered packet capture file (.pcap) to "Wireshark Assignment #3: Network Layer - PCAP Submission" section before deadline. Please refer to the course syllabus for late submission terms and follow Odtuclass system for further announcements.
