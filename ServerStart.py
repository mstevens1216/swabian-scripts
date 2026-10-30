#ServerStart.py
# MLS 8-14-2025
# This code initializes a Swabian TimeTagger server for creating a 
# TimeTagger network in order to gather counts across multiple labs
# ─────────────────────────────────────────────────────────
# HOW TO USE:
# 1. Comment out Sync offset for first startup
# 2. Ensure Swabian is attached, serial number is correct, and GUI is not open
# 3. Run the code, you should expect an error for a sync offset but there is a chance
# no error occurs, in which case your server is started and nothing further is needed
# 4. The error instructs you to enter a value in the sync offset, enter this number
# and uncomment the sync offset, run again
# Congrats you started a TimeTagger server, you can connect and disconnect from it all you want,
# if you restart Alice computer (SB48) you should restart the server as Alice is the central NTP timebase.
# ─────────────────────────────────────────────────────────

import time, sys
import TimeTagger as TT

# ─── CONFIGURATION ─────────────────────────────────────────────────────────
TAG_SERIAL  = "2411001ABF"    # Time-Tagger hardware S/N
TAG_PORT    = 41101           # TCP port for the Time-Tagger server (This is default)
SYNC_OFFSET = 315E9          # your reference-clock offset
# ───────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tagger = TT.createTimeTagger(TAG_SERIAL)

    tagger.setTriggerLevel(-2, -0.640) # Here I specify channel 2 with falling edge measurements
    # and a threshold of -.640 (NIM). positive channel numbers for rising edge measurements
    # This is the channel that your detector is attached to 
    tagger.setReferenceClock(
        clock_channel=1, # Channel your 10 MHz signal is attached to
        synchronization_channel=4, # Channel your PPS signal is attached to 
        #synchronization_offset=SYNC_OFFSET, # Comment this out upon start
        wait_until_locked=True # Won't start the server until the clock is locked
    )

    tagger.startServer(access_mode=TT.AccessMode.Control, port=TAG_PORT)
    print(f"Time-Tagger server running on 0.0.0.0:{TAG_PORT}")

    # keep the process alive so the server stays up
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nShutting down Time-Tagger server")