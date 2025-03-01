"""
RCA Radio Telescope - Pluto SDR Filter Control Script
    Sponsor(s): Rose City Astronomers
    Team: PSU Capstone Team 11 2025     

    Version: 1.1
    Author(s): Truong Le
    Date: 2/28/2025

    Description: This script configures and sets the Pluto SDR
    to utilize its GPO pins located on the board. The script
    communicates configuration changes through AD's pyadi-iio
    library. This allows for the script to configure the SDR
    to drive a GPO pin if its in a certain state (such as RX). 
    GPO0 and GPO1 will drive the control circuitry on the filter
    board.

    This script takes in user input for 5 total states:
        - OFF: Disconnects the LNA/SDR from the antenna and filter board
        - A: Filter A is selected
        - B: Filter B is selected
        - C: Filter C is selected
        - RST: Reset configurations to default
        - EXIT: Exit program with no changes (good for checking state of SDR) 

    Dependencies: 
        - Python
            - Installation Page: https://www.python.org/downloads/
        - pyadi-iio (Available using pip installer)
            - Wiki: https://analogdevicesinc.github.io/pyadi-iio/index.html
        - libiio (Not available from pip, need to go to repo to install)
            - GitHub Releases: https://github.com/analogdevicesinc/libiio/releases
"""
# Import Libraries
import adi
from enum import Enum

### Class Enumerations
# Define Used Commands
# V1: Control Signal 1
# V2: Control Signal 2
# FTDD: FDD and TDD Selection
class cmd(Enum):
    V1 = "adi,gpo0-slave-rx-enable"
    V2 = "adi,gpo1-slave-rx-enable"
    FTDD = "adi,frequency-division-duplex-mode-enable"

# Define States
class state(Enum):
    OFF = "OFF"
    A = "A"
    B = "B"
    C = "C"
    RST = "RST"
    EXIT = "EXIT"

###  Functions
def debugCtrl(ctrl_attr, val):
    sdr._ctrl.debug_attrs[ctrl_attr].value = val # type: ignore

def printCtrl(attr):
    return sdr._ctrl.attrs[attr].value # type: ignore

def printDebugCtrl(attr):
    return sdr._ctrl.debug_attrs[attr].value # type: ignore

def updateGPO():
    match curr_state:
        # Shutdown
        case state.OFF:
            debugCtrl(cmd.V1.value, "0")
            debugCtrl(cmd.V2.value, "0")
        # J1
        case state.A:
            debugCtrl(cmd.V1.value, "0")
            debugCtrl(cmd.V2.value, "1")
        # J2
        case state.B:
            debugCtrl(cmd.V1.value, "1")
            debugCtrl(cmd.V2.value, "0")
        # J3
        case state.C:
            debugCtrl(cmd.V1.value, "1")
            debugCtrl(cmd.V2.value, "1") 
        # Default (Shutdown) 
        case _:
            debugCtrl(cmd.V1.value, "0")
            debugCtrl(cmd.V2.value, "0")
    debugCtrl("initialize", "1")
    print("Filter Selected: Filter " + curr_state.name)

def checkState(arr):
    match arr:
        case ["0","0"]:
            print("Currently selected: OFF")
        case ["0","1"]:
            print("Currently selected: Filter A")
        case ["1","0"]:
            print("Currently selected: Filter B")
        case ["1","1"]:
            print("Currently selected: Filter C")
        case _:
            print("Invalid State!")

def checkInput(userInput):
    try:
        testState = state(userInput)
        return True
    except ValueError:
        return False

### Start Program 

# Instantiate Pluto SDR
print("Instantiating SDR...")
sdr = adi.Pluto(uri="ip:192.168.0.20")

# Check current filter selection
checkState([printDebugCtrl(cmd.V1.value), printDebugCtrl(cmd.V2.value)])

# Take user input for option selection
entry = input("Enter filter to select (OFF, A, B, C) or to exit enter (RST, EXIT): ")
if checkInput(entry):
    curr_state = state(entry)
else:
    print(f"'{entry}' is a not valid selection. Exiting...")
    exit()

# Exit Options
if (curr_state == state.RST):
    # Switch to FDD mode and Disable GPO
    debugCtrl(cmd.FTDD.value, "1")
    debugCtrl(cmd.V1.value, "0")
    debugCtrl(cmd.V2.value, "0")
    debugCtrl("initialize", "1")
    print("SDR has been reset to default, exiting...")
    exit()
elif (curr_state == state.EXIT):
    print("Exiting with no changes")
    exit()

#print("Current ENSM mode:", printCtrl("ensm_mode"))

# Set to TDD mode (Has RX and TX states)
debugCtrl(cmd.FTDD.value, "0")
debugCtrl("initialize", "1")

#print("ensm_mode_available:", printCtrl("ensm_mode_available"))
#print("Final ENSM:", printCtrl("ensm_mode"))

# Update GPO config attributes using current state
updateGPO()
