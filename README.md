# go-back-n
## Instructions
- Run `receiver.py`
```
python3 receiver.py -d -p 5555 -n 100 -e 0 -o kali.txt
```
- Run `sender.py`
```
python3 sender.py -s [RECEIVER IP ADDRESS] -d -p 5555 -n 400 -l 512 -r 100 -w 3 -f 10 -file kali.txt
```