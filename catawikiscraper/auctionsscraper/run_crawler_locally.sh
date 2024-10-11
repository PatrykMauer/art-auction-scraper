#!/bin/bash

# Check if the correct number of arguments were provided
if [ "$#" -ne 2 ]; then
    echo "Error: Incorrect number of arguments."
    echo "Usage: $0 <config_file> <category>"
    echo "You provided $# arguments."
    read -p "Press Enter to exit..."
    exit 1
fi

# Assign arguments to variables
CONFIG_FILE=$1
CATEGORY=$2

# Check if the config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file '$CONFIG_FILE' not found."
    read -p "Press Enter to exit..."
    exit 1
fi

# Execute the Python script to generate the Scrapy command
COMMAND=$(python auctionsscraper\\parse_config.py "$CONFIG_FILE" "$CATEGORY" 2>&1)
COMMAND_STATUS=$?

# Check if the command generation was successful
if [ "$COMMAND_STATUS" -eq 0 ]; then
    echo "Running command: $COMMAND"
    eval "$COMMAND"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to execute the Scrapy command."
        echo "Command attempted: $COMMAND"
        read -p "Press Enter to exit..."
        exit 1
    fi
else
    echo "Error: Failed to generate command. Python script exited with status $COMMAND_STATUS"
    echo "Python output (if any): $COMMAND"
    read -p "Press Enter to exit..."
    exit 1
fi

# Prompt to keep the window open at the end, even if it finishes successfully
read -p "Process completed. Press Enter to exit..."
