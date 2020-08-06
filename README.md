### Go-Back-N Socket Program For A2/CS456

---

**Run Environment:**

* You must have python3.7 installed. 
* You must include the `emulator` program installed at the top level of directory. (relative to sender.sh). 
* The emulator program is named "nEmulator-linux386" with executable permissions
* You need to have input file (where data sits to be transferred) created.



**How to run:**

You can run sender, receiver, emulator on different machine or run them on the same server. 

1. Start the emulator by passing it the host1 and host2 address for sender and receiver end server. Also specify other parameters below:

```
<emulator's  receiving  UDP  port  number  in  the  forward  (sender) direction>,
<receiver’s network address>,
<receiver’s receiving UDP port number>,
<emulator's  receiving  UDP  port  number  in  the  backward  (receiver) direction>,<sender’s network address>,<sender’s receiving UDP port number>,
<maximum delay of the link in units of millisecond>,
<packet discard probability>,<verbose-mode>
```

2. Execute `receiver.sh` using bash first, and then execute `sender.sh`. Make sure you pass all the parameters needed as below:

* `receiver.sh` requires 4 parameters: 
  * hostname for emulator
  * udp port number used by emulator
  * udp port number used by receiver to receive
  * name of file to save output
* `sender.sh` requires 4 parameters:
  * hostname for emulator
  * udp port number used by emulator
  * udp port number used by sender to send data
  * name of file to read input to packets



