[//]: # (Image References)
[image_overview]: ./misc/radio_rx_tx_overview.png

# Radio Sensor RX/TX and Web API
![tx_rx overview][image_overview]
Environmental data is sensed, transmitted, received, then sent to an online API.

## Requirements and Included Documentation
- SAM4L8 Xplained Pro (AVR/CortexM4 board)
    - [Documentation/Information](http://www.atmel.com/tools/atsam4l8-xpro.aspx?tab=overview)
- I/O1 Xplained pro (environment sensor)
    - [Documentation/Information](http://www.atmel.com/tools/atio1-xpro.aspx)
- Radio
    - [Documentation/Information](http://www.atmel.com/tools/lightweight_mesh.aspx)
- [Atmel Studio](http://www.atmel.com/microsite/atmel-studio/) (Strongly recommended, but maybe not required - [Platformio](https://github.com/platformio) could likely be used as an alternative)

## Directory Structure
- `./API/`
    - `./backend/`
        - `actions/`
            - `methods.js`: API function functionality
        - `config/`
            - `database.js`: Database configuration
        - `models/`
            - `sensor_data.js`: Data scheme
        - `server.js`: API/server functionality
    - `./frontend/`
        - `/*`: Currently only a placeholder for a Angular2 front end
- `./receiver/src/`
    - `main.c`: receive radio, write to USART
- `./parsing/`
    - `send_to_server.py`: post data to API (via url)
    - `serial_reader.py`: Read serial data and use `send_to_sever()`
- `./transmitter/`
    - `src/main.c`: read temp, light, send via radio

## Future Direction
- All progress is currently suspended as I no longer have access to a SAMM4L8 board or peripherals.

NOTE: git doesn't like me trying to rename the receiver directory :,(
