# WhatsApp Chats Exporter
Export All your WhatsApp chats to CSV files

## Installation

Install Python3, if not already installed.

### Linux
    chmod +x ./start.sh
    ./start.sh

### MacOS
    brew install selenium-server-standalone
    chmod +x ./start.sh
    ./start.sh

### Windows 
    start.bat

## Notes
Currently we output text files (*.json) that cary the raw text of the chats.
A parser into CSV will be implemented shortly. Note we do not extract the media,
just texts and links.        