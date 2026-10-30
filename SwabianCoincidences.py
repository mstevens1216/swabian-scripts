# SwabianCoincidences.py
# MLS 8-4-2025
# This script can be used to collect coincidence counts for either one or multiple locations
# Follow the comments to learn how to use each method
# For multiple locations, you will need to start the time tagger server for each remote tagger (ServerStart.py)
# Either on computer (if tagger is attached to computer) or raspberry pi if attached.
# Outputs 2 files, one with information on basis combo, singles, and coincidences, one with just the counts
# Timestamps represent the time the tomography completed, useful for post processing and plotting.
# Use requirements.txt for dependencies, NOTE: DO NOT PIP INSTALL TimeTagger, this is included in the api when you install the swabian
# TimeTagger software

import TimeTagger as TT
import numpy as np, socket, serial, time, datetime
from pathlib import Path
import matplotlib.pyplot as plt

# ─── USER KNOBS ────────────────────────────────────────────
NUM_SWEEPS   = 1         # how many tomography runs
INTEGRATION  = 30         # seconds per projection
# -----------------------------------------------------------

# These are where the Nucrypts are attached when connected to Raspberry Pi's
# Everytime unplugged and replugged should be same port, see instruction doc for troubleshooting tips
HOST, PORT   = "10.0.3.60", 4002 # BOB
HOST1, PORT1 = "10.0.3.40", 7001 # CHARLIE

# If the PA is remote, use socket, if local use serial
PA1 = socket.create_connection((HOST1, PORT1), timeout=5)
PA3 = socket.create_connection((HOST, PORT), timeout=5)

# Time-tagger server, not needed if just using one tagger in local location
# This block follows same format as ServerStart.py
tagger_A = TT.createTimeTagger("22440012WV") # Use the serial number of the TimeTagger to connect to it
tagger_A.setTriggerLevel(-2, -0.480)
tagger_A.setReferenceClock(clock_channel=1,
                           synchronization_channel=6,
                        #    synchronization_offset = -379E9,
                           wait_until_locked=True)
tagger_A.startServer(TT.AccessMode.Control, port=41101)


# To count coincidences across multiple labs, we start a network by calling the servers we started in each lab
# Input the IP of the device the swabian is attached to and the default port (unless you changed the port in ServerStart.py)
servers = ["10.0.3.11:41101", "10.0.3.12:41101"] 
# Create the network
ttn     = TT.createTimeTaggerNetwork(servers)

# ─── Basis projections ─────────────────────────────────
basis = ["H","V","D","A","L","R"]
pairs = [(x, y) for x in basis for y in basis] # for all 36 projection combinations
# If you want less projections change for that combination


# The format of channels for 1 tagger is 1,2,3 etc and negative numbers for falling edge measurements (NIM)
# For a network, the channel numbering convention is N00X where N is the number you entered the server in and X is the channel number
# For that tagger. Example:
# I call servers = [Alice,Bob], so Alice will be 100X and Bob will be 200X, so for
# Channel 2 on Alice and Channel 2 on Bob I will call 1002 and 2002 respectively.
ch1,ch2  = -1002,-2002
binwidth = 1000 # in picoseconds, 1 ns should be adequate but feel free to adjust as needed
n_bins   = 5000 # If the distance to lab is much larger, you may need to increase this.
runtime_ps = int(INTEGRATION * 1e12) # This is set up top in USER KNOBS

Path("./PATHNAME").mkdir(parents=True, exist_ok=True) # Set the path where you want the data to be sent
fname_base = ("./PATHNAME/"
              f"FILENAME"
              f"{INTEGRATION}S_36proj")

# ─── helper to talk to PAs ───────────────
def set_pa(pa, idx, socket_mode=True):
    if socket_mode:
        pa.sendall(b"2\n"); pa.sendall(b"c\n")
        pa.sendall(f"{basis[idx]}\n".encode()); pa.sendall(b"p\n")
        debug = pa.recv(8)
        print(f"PA1: {debug}")
    else:
        pa.write(b"2\n"); pa.write(b"c\n")
        pa.write(f"{basis[idx]}\n".encode()); pa.write(b"p\n")
        debug2 = pa.read(8)
        print(f"PA3: {debug2}")

# The meat and potatoes
def tomography(i,j,fname):
    set_pa(PA1,i)             # Set the PA for basis combos
    set_pa(PA3,j,True)        # Set the PA for basis combos

    coinc   = TT.Correlation(tagger=ttn, # For one location, change to variable you assigned TT.CreateTimeTagger()
                             channel_1=ch1, channel_2=ch2,
                             binwidth=binwidth, n_bins=n_bins)
    singles = TT.Counter(tagger=ttn, # if you want the countrate, counts per second, do TT.Countrate() with same inputs
                         channels=[ch1,ch2], binwidth=runtime_ps)

    coinc.startFor(runtime_ps); singles.startFor(runtime_ps)
    singles.waitUntilFinished(); coinc.waitUntilFinished()

# ──────────────────────────────────────────────────────────────────
# Offset finding helper
# Zoom in on the graph to see the coincidence peak and change the mask to be in between those numbers
# The offset will never change for a given fiber configuration, its based on the length of the fiber

    xx, yy = coinc.getIndex(), coinc.getData() 
    plt.plot(xx,yy) # Comment this out when you find your offset
    plt.show() # Comment this out when you find your offset

    mask   = (xx>=-455_000) & (xx<=-453_000) # Set based on offset
    coincidences = int(np.sum(yy[mask]))


    # write file names
    with open(fname+".txt","a") as f:
        f.write(f"PA Basis {basis[i]}{basis[j]}  Singles {singles.getData()}  "
                f"Coincidences {coincidences}\n")
    with open(fname+"_COUNTSONLY.txt","a") as f2:
        f2.write(f"{coincidences} ")

    return coincidences

# ─── main acquisition loop with timestamp after each sweep ─
for sweep in range(1, NUM_SWEEPS+1):
    print(f"\n=== Sweep {sweep}/{NUM_SWEEPS} ({INTEGRATION}s each) ===")
    t_start = time.time()

    for a,b in pairs:
        last_val = tomography(a,b,fname_base)

    elapsed = time.time()-t_start
    stamp   = datetime.datetime.now().isoformat(' ', 'seconds')
    print(f"Last projection coincidences: {last_val}")
    print(f"Sweep runtime: {elapsed:.1f} s  ({stamp})")

    # append timestamp markers
    with open(fname_base+".txt","a") as f:
        f.write(f"Sweep finished {stamp}  runtime {elapsed:.1f} s\n\n")
    with open(fname_base+"_COUNTSONLY.txt","a") as f2:
        f2.write(f"{stamp}\n")

print("All sweeps complete.")
