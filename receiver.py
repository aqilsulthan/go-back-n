# receiver.py
from socket import *
import random
import argparse
import time
import os

def gen_packet(seqNum, pktLen):
    seqBytes = seqNum.to_bytes(4, byteorder='little')
    data = os.urandom(pktLen - 4)
    return seqBytes + data

def getSeqNum(pkt):
    sequenceNum = int.from_bytes(pkt[0:4], byteorder='little')
    return sequenceNum

def write_file(file_path, data):
    with open(file_path, 'ab') as file:
        file.write(data)

def main():
    parser = argparse.ArgumentParser(description='Go-back-N reliable transmission protocol')
    parser.add_argument('-d', '--debug', help='Turn ON Debug Mode(OFF if -d flag not present)', action='store_true')
    parser.add_argument('-p', '--port', type=int, help="Receiver's Port Number, integer", required=True)
    parser.add_argument('-n', '--maxPkts', type=int, help='MAX_PACKETS, integer', required=True)
    parser.add_argument('-e', '--pktErrRate', type=float, help='Packet Error Rate (RANDOM_DROP_PROB), float', required=True)
    parser.add_argument('-o', '--output', help='Path to save the received file', required=True)
    args = vars(parser.parse_args())

    localIP = "0.0.0.0"  # Listen on all available interfaces
    localPort = args['port']
    bufferSize = 2048
    debugbit = args['debug']
    recsock = socket(AF_INET, SOCK_DGRAM)
    recsock.bind((localIP, localPort))
    maxPkts = args['maxPkts']
    randomDropProb = args['pktErrRate']
    nextFrameExpected = 0
    totalExpectedPackets = maxPkts

    output_file_path = args['output']

    while nextFrameExpected < totalExpectedPackets:
        data, addr = recsock.recvfrom(2048)
        seq_num = getSeqNum(data)
        if randomDropProb > 0.9:
            break
        if random.uniform(0, 1) < randomDropProb and seq_num != 0:
            continue
        if seq_num == nextFrameExpected:
            ackPkt = gen_packet(seq_num, 4)
            if debugbit:
                print(f"Seq #:{seq_num % 255} Time Received: {time.time()} Packet dropped: false")
            recsock.sendto(ackPkt, addr)
            nextFrameExpected += 1
            file_data = data[4:]
            write_file(output_file_path, file_data)
        else:
            sent_seq_num = nextFrameExpected - 1
            if debugbit:
                print(f"Seq #:{seq_num % 255} Time Received: {time.time()} Packet dropped: true")
            if sent_seq_num >= 0:
                ackPkt = gen_packet(sent_seq_num, 4)
                recsock.sendto(ackPkt, addr)

    print(f"Random Probability for dropping {randomDropProb}")
    print("Receiver terminated")
    recsock.close()

if __name__ == "__main__":
    main()
