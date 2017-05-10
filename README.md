This project bring CNC control for ARM based Linux boards like Raspberry Pi.
Typically there is no way to control stepper motors from Linux runtime
environment due to the lack of real time GPIO control. Even kernel based
modules can not guarantee precise control of pulses for steppers. There is
always way out. DMA(Direct Memory Access) is a separated hardware module which
provides high precision for GPIO outputs. This module can copy bytes which
represent GPIO states from RAM buffer directly to GPIO with some clock based
on main chip internal oscillator without using CPU's cores. Using such approach
this project generates impulses for moving stepper motors and that is very
precise way regardless CPU load and OS time jitter.  
This approach also allows to use Python language for this project. Typically,
Python is not good choice for real time application, but since project just
needs to set up DMA buffers and hardware will do the rest, Python become the
perfect choice for easy development of this project.

Video demo - [YouTube video](https://youtu.be/vcedo59raS4)

#Current command support
G0, G1, G4, G20, G21, G28, G90, G91, G92, M2, M3, M5, M30  
Commands can be easily added, see [gmachine.py](./gmachine.py) file.

#Config
All config is stored in [config.py](./config.py) and contains hardware properties, limitations
and pin names for hardware control.

#Hardware
Currently, this project supports Raspberry Pi 1-3. But there is a way to add new boards.
See [hal.py](./hal.py) file.

#Performance notice
Pure Python interpreter wouldn't provide great performance for high speed machines.
Overspeeding setting causes motors mispulses and probably lose of trajectory. According 
to my tests, Raspberry Pi 2 can handle axises with 400 pulses on mm with top velocity ~800 mm 
per min. There is always way out! :) Use JIT Python implementation like PyPy. RPi2 can handle
up to 18000 mm per minute on the machine with 80 steps per millimeter motors with PyPy.  
_Note: Raspbian has outdated PyPy version in repositories(v4.0). Moreover v4.0 has issue with
`mmap` module implementation. Use PyPy v5.0+, download it for your OS from
[here](https://pypy.org/download.html)._  
PyPy installation:
```bash
wget wget https://bitbucket.org/pypy/pypy/downloads/pypy2-v5.7.1-linux-armhf-raspbian.tar.bz2
sudo mkdir /opt/pypy
sudo tar xvf pypy2-v5.7.1-linux-armhf-raspbian.tar.bz2 --directory /opt/pypy/ --strip-components=1
sudo ln -s /opt/pypy/bin/pypy /usr/local/bin/pypy
```

#Dependencies
Nothing. Just pure Python code.

#GCode simulation
Just a link to a nice web software for gcode files emulation (very helpful for manual creating of
gcode files): [https://nraynaud.github.io/webgcode/](https://nraynaud.github.io/webgcode/)

#License
see [LICENSE](./LICENSE) file.

#Author
Nikolay Khabarov

