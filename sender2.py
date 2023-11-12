# sender.py
from socket import *
import time
import os
import _thread
import argparse

class Timerclass(object):
    TIMER_STOP = -1

    def __init__(self):
        self._start_time = self.TIMER_STOP

    def start(self):
        if self._start_time == self.TIMER_STOP:
            self._start_time = time.time()

    def stop(self):
        if self._start_time != self.TIMER_STOP:
            self._start_time = self.TIMER_STOP

    def timeout(self, seq_num, rtt_ave):
        if seq_num <= 10:
            timeout = 0.1  # 100 milliseconds in seconds
        else:
            timeout = 2 * rtt_ave
        return time.time() - self._start_time >= timeout

    def running(self):
        return self._start_time != self.TIMER_STOP

baseNum = 0
mutex = _thread.allocate_lock()
send_timer = Timerclass()
start_time = {}

def gen_packet(seqNum, pktLen, file_data):
    seqBytes = seqNum.to_bytes(4, byteorder='little')
    return seqBytes + file_data[seqNum * (pktLen - 4): (seqNum + 1) * (pktLen - 4)]

def read_file(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
    return data

def send_packet(sock, packet, serverAddressPort):
    sock.sendto(packet, serverAddressPort)

def update_local_state_variables(sequence_number):
    global rtt_ave, num_packets_acknowledged, start_time
    rtt = time.time() - start_time[sequence_number]
    rtt_ave = (rtt_ave * num_packets_acknowledged + rtt) / (num_packets_acknowledged + 1)
    num_packets_acknowledged += 1
    return rtt

def getSeqNum(pkt):
    sequenceNum = int.from_bytes(pkt[0:4], byteorder='little')
    return sequenceNum

def receive(sock):
    global mutex, baseNum, send_timer, start_time, rtt_ave, num_retransmissions

    while True:
        ackPkt, addr = sock.recvfrom(2048)
        ack = getSeqNum(ackPkt)

        if ack >= baseNum:
            mutex.acquire()
            baseNum = ack + 1
            rtt = update_local_state_variables(ack)
            send_timer.stop()
            mutex.release()

def main():
    sendsock = socket(AF_INET, SOCK_DGRAM)

    global mutex, baseNum, send_timer, start_time, rtt_ave, num_packets_acknowledged, num_retransmissions, debugbit

    parser = argparse.ArgumentParser(description='Go-back-N reliable transmission protocol')
    parser.add_argument('-d', '--debug', help='Turn ON Debug Mode(OFF if -d flag not present)', action='store_true')
    parser.add_argument('-s', '--recIP', help='Receiver IP address, string', required=True)
    parser.add_argument('-p', '--port', type=int, help="Receiver's Port Number, integer", required=True)
    parser.add_argument('-l', '--pktLen', type=int, help='PACKET_LENGTH, in bytes, integer', required=True)
    parser.add_argument('-r', '--pktGenRate', type=int, help='PACKET_GEN_RATE, in packets per second, integer', required=True)
    parser.add_argument('-n', '--maxPkts', type=int, help='MAX_PACKETS, integer', required=True)
    parser.add_argument('-w', '--winSize', type=int, help='WINDOW_SIZE, integer', required=True)
    parser.add_argument('-f', '--maxBufSize', type=int, help='MAX_BUFFER_SIZE, integer', required=True)
    parser.add_argument('-file', '--file', help='Path to the image file to be sent', required=True)
    args = vars(parser.parse_args())

    serverIP = args['recIP']
    serverPort = args['port']
    serverAddressPort = (serverIP, serverPort)
    bufferSize = 2048
    rtt_ave = 0
    pktLength = args['pktLen']
    pktGenRate = args['pktGenRate']
    maxPackets = args['maxPkts']
    windowSize = args['winSize']
    maxBufferSize = args['maxBufSize']

    buffer = []
    debugbit = args['debug']
    num_packets_acknowledged = 0
    num_retransmissions = {}
    file_path = args['file']
    file_data = read_file(file_path)

    while 1:
        if len(buffer) >= maxPackets:
            break
        if len(buffer) < maxPackets:
            seqNum = len(buffer)
            num_retransmissions[seqNum] = -1
            pkt = gen_packet(seqNum, pktLength, file_data)
            buffer.append(pkt)
        time.sleep(1 / pktGenRate)

    nextToSend = 0

    _thread.start_new_thread(receive, (sendsock,))
    loopbreak = False

    while True:
        mutex.acquire()
        if baseNum >= len(buffer):
            break

        while nextToSend < windowSize + baseNum:
            if nextToSend >= len(buffer):
                break

            print(f"Sending {nextToSend} sequence number packet")
            send_packet(sendsock, buffer[nextToSend], serverAddressPort)
            num_retransmissions[nextToSend] += 1
            if num_retransmissions[nextToSend] > 5:
                loopbreak = True
            start_time[nextToSend] = time.time()
            nextToSend += 1

        if loopbreak:
            break

        if not send_timer.running():
            send_timer.start()

        while send_timer.running() and not send_timer.timeout(baseNum, rtt_ave):
            mutex.release()
            time.sleep(0.01)
            mutex.acquire()

        if send_timer.running() or send_timer.timeout(baseNum, rtt_ave):
            send_timer.stop()
            nextToSend = baseNum
        else:
            windowSize = min(windowSize, maxPackets - baseNum)
        mutex.release()

    total = 0
    for i in num_retransmissions:
        total += (1 + num_retransmissions[i])

    print(f"Total packets sent: {nextToSend}")
    print(f"Total packets acknowledged: {num_packets_acknowledged}")
    if num_packets_acknowledged != 0:
        print(f"Retransmission Ratio: {total/num_packets_acknowledged}")
    print(f"Average RTT: {rtt_ave * 1000}")
    sendsock.close()

if __name__ == "__main__":
    main()
