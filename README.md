# go-back-n
## Instructions
- Run `receiver.py`
```
python3 receiver.py -d -p 5555 -n 4 -e 0.1 -o kali.txt
```
- Run `sender.py`
```
python3 sender.py -s [RECEIVER IP ADDRESS] -d -p 5555 -n 4 -l 512 -r 100 -w 3 -f 10 -file kali.txt
```
## Configuration
### receiver.py

- -d or --debug: This argument is optional and does not take any value (action='store_true'). When present, it turns on the debug mode.

- -p or --port: This argument is required and expects an integer value. It represents the port number on which the receiver will listen.

- -n or --maxPkts: This argument is required and expects an integer value. It represents the maximum number of packets the receiver will process.
Packet Error Rate:

- -e or --pktErrRate: This argument is required and expects a float value. It represents the packet error rate or the probability of a packet being dropped.

- -o or --output: This argument is required and expects a string value. It represents the path where the received file will be saved.

### sender.py

- -d or --debug: This argument is optional and does not take any value (action='store_true'). When present, it turns on the debug mode.

- -s or --recIP: This argument is required and expects a string value. It represents the IP address of the receiver.

- -p or --port: This argument is required and expects an integer value. It represents the port number on which the receiver will listen.

- -l or --pktLen: This argument is required and expects an integer value. It represents the length of each packet in bytes.

- -r or --pktGenRate: This argument is required and expects an integer value. It represents the rate at which packets are generated, measured in packets per second.

- -n or --maxPkts: This argument is required and expects an integer value. It represents the maximum number of packets to be sent.

- -w or --winSize: This argument is required and expects an integer value. It represents the size of the sliding window.

- -f or --maxBufSize: This argument is required and expects an integer value. It represents the maximum size of the buffer.

- -file or --file: This argument is required and expects a string value. It represents the path to the file to be sent.