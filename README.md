# robotSystem
 this is the robot system python library

# Installation

Windows:
```
pip install git+https://github.com/TreexHD/robotSystem.git
```

Linux:
```
pip3 install git+https://github.com/TreexHD/robotSystem.git
```

# Basic Usage
The file [Example1](https://github.com/TreexHD/robotSystem/tree/main/examples/example1.py) shows a simple starting 
script you can just copy. 

# WARNING ⚠️⚠️⚠️
- the 6 pins marked as A_IN are not inputs. ignore them!
- In V5Rev1 and V6Rev1 are two tracks missing. Add cables as shown in the Image:
  ![Version V6 Mistake](https://github.com/TreexHD/robotSystem/blob/main/data/fix_error.png)

# Testing 
## Test connected Devices to I2C
```
sudo apt-get install i2c-tools
```
and run:
```
i2cdetect -y 1
```



# Documentation

## Basic functionality

# PCB
## Solder it
FrontV6
![Version V6 Front](https://github.com/TreexHD/robotSystem/blob/main/data/FrontV6.png)
BackV6
![Version V6 Back](https://github.com/TreexHD/robotSystem/blob/main/data/BackV6.png)
Parts
| PartValue     | PartId        |
| ------------- | ------------- |
| 220 Ohm       | R8-R15     |
| 4K7 Ohm       | R1,R2, |
| 10k Ohm       | R7,R16,R17,R18,R19 |
| 1k Ohm        | R4, R5 |
| 500 Ohm (LED) | R3, R6 | 
| connect       | JP1, JP2, JP4 |
| socket_connector  | PS1, PS2, J6 |
| pin_connector  | J1, J7, J8, J9, J10, J11, J12, J13, J19, J20, J22, J24, J25, J23, J26, J27, J27, J29|
| 100uF         | C1, C5 |
| LED           | D1, D2 |
| ceramic       | C2, C3, C4|
| diode         | D3-D18 |

ICs
| IC            | PartId        |
| ------------- | ------------- |
| MCP3008       | U1            |
| SN74HC4066D   | U2, (U3)      |
| PCA9685PW     | U5            |
| L293D         | (U6), (U7)    |


## Connect it
FrontV6 Connection
![Version V6 Front Connection](https://github.com/TreexHD/robotSystem/blob/main/data/FrontV6_Connection.png)

# Connect a TOF Sensor
![TOF Connection](https://github.com/TreexHD/robotSystem/blob/main/data/TOF_connection.png)




