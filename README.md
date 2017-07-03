## Radio Sensor RX/TX and Web API
Environmental data is sensed, transmitted, received, then sent to an online API.

## Requirements and Included Documentation
- SAM4L8 Xplained Pro (AVR/CortexM4 board)
    - [Documentation/Information](http://www.atmel.com/tools/atsam4l8-xpro.aspx?tab=overview)
- I/O1 Xplained pro (environment sensor)
    - [Documentation/Information](http://www.atmel.com/tools/atio1-xpro.aspx)
- Radio
    - [Documentation/Information](http://www.atmel.com/tools/lightweight_mesh.aspx)
- [Atmel Studio](http://www.atmel.com/microsite/atmel-studio/) (Strongly recommended, but maybe not required - [Platformio](https://github.com/platformio) could likely be used as an alternative)

## Overview
[tx sensor micro] --> [rx micro] --usb--> [parse] --> [server] <||> web

## Directory Structure
- `./backend/`
- `./frontend/`


## Future Direction
- All progress is currently suspended as I no longer have access to a SAMM4L8 board or peripherals.
