[![Build Status](https://travis-ci.org/Nikolay-Kha/PyCNC.svg?branch=master)](https://travis-ci.org/Nikolay-Kha/PyCNC)

# PyCNC
This project bring CNC control for Raspberry Pi or any ARM based Linux boards.
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

# Current command support
G0, G1, G4, G20, G21, G28, G90, G91, G92, M2, M3, M5, M30  
Commands can be easily added, see [gmachine.py](./cnc/gmachine.py) file.

# Config
All configs are stored in [config.py](./cnc/config.py) and contain hardware
properties, limitations and pin names for hardware control.  
Raspberry Pi implementation should be connected to A4988, DRV8825 or any other
stepper motor drivers with DIR and STEP pin inputs.
Default config is created for Raspberry Pi 2-3 and this wiring diagram:
![](https://cloud.githubusercontent.com/assets/8740775/26024664/bc13d5a6-37de-11e7-98ed-9391109fcfd0.jpg)  
So having Raspberry Pi connected this way, there is no need to configure
pin map for project.

# Hardware
Currently, this project supports Raspberry Pi 1-3. Tested with RPI2. But there
is a way to add new boards. See [hal.py](./cnc/hal.py) file.
_Note: Current Raspberry Pi implementation uses the same resources as on board
GPU(memory). So video output will not work with this project. Use ssh
connection to board. And do not connect HDMI cable, otherwise project would not
run. Probably, increasing of GPU dedicated memory(at least to 64 MB) could solve
it and allow to work project and GPU together, but it was never tested._

# Usage
Just clone this repo and run `./pycnc` from repo root. It will start in
interactive terminal mode where gcode commands can be entered manually.  
To run file with gcode commands, just run `./pycnc filename`.  
Optionally, `pycnc` can be installed. Run
```bash
sudo pip install .
```
in repo root directory to install it. After than, `pycnc` command will be added
to system path. To remove installation, just run:
```bash
sudo pip remove pycnc
```

# Performance notice
Pure Python interpreter wouldn't provide great performance for high speed
machines. Overspeeding setting causes motors mispulses and probably lose of
trajectory. According to my tests, Raspberry Pi 2 can handle axises with 400
 pulses on mm with top velocity ~800 mm per min. There is always way out! :)
Use JIT Python implementation like PyPy. RPi2 can handle up to 18000 mm per
minute on the machine with 80 steps per millimeter motors with PyPy.  
_Note: Raspbian has outdated PyPy version in repositories(v4.0). Moreover v4.0
has issue with `mmap` module implementation. Use PyPy v5.0+, download it for
your OS from [here](https://pypy.org/download.html)._  
PyPy installation:
```bash
wget wget https://bitbucket.org/pypy/pypy/downloads/pypy2-v5.7.1-linux-armhf-raspbian.tar.bz2
sudo mkdir /opt/pypy
sudo tar xvf pypy2-v5.7.1-linux-armhf-raspbian.tar.bz2 --directory /opt/pypy/ --strip-components=1
sudo ln -s /opt/pypy/bin/pypy /usr/local/bin/pypy
```

# Project architecture
![](https://cloud.githubusercontent.com/assets/8740775/26027974/38cc80ac-3820-11e7-8fde-9cf106d77db5.png)

# Dependencies
Nothing for runtime. Just pure Python code.
For uploading to PyPi there is a need in `pandoc`:
```bash
sudo dnf install pandoc
sudo pip install pypandoc
```

# GCode simulation
Just a link, mostly for myself :), to a nice web software for gcode files
emulation (very helpful for manual creating of gcode files):
[https://nraynaud.github.io/webgcode/](https://nraynaud.github.io/webgcode/)

# License
see [LICENSE](./LICENSE) file.

# Author
Nikolay Khabarov

