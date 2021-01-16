#!/bin/bash

pip install -r requirements.txt

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Running on Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Running on MacOS"
    brew install selenium-server-standalone
else
        echo "Unsupported OS"
fi

echo "When the Chrome window opens up, please pair WhatsApp from your phone using the QR code"

python3 exporter/reader.py
