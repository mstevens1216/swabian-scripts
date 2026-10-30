# Swabian Coincidence Acquisition

Python script for automated polarization tomography and coincidence counting using Swabian Instruments Time Taggers and NuCrypt polarization analyzers.

## Overview

`SwabianCoincidences.py` automates coincidence measurements across polarization projection combinations.

Features include:
- Support for local and networked Swabian Time Taggers
- Automated polarization analyzer control
- Configurable integration times and tomography sweeps
- All 36 combinations of H, V, D, A, L, and R polarization projections
- Coincidence histogram visualization for timing-offset calibration
- Automatic saving of singles, coincidences, and completion timestamps

## Requirements

**Hardware:**
- Swabian Instruments Time Tagger(s)
- NuCrypt polarization analyzers
- Network connectivity between instruments when using multiple locations
- Proper synchronization between Time Taggers for distributed measurements

**Software:**
- Python 3
- Dependencies listed in `requirements.txt`
- Swabian Instruments Time Tagger software and Python API

**Important:** Do not install `TimeTagger` using pip. The TimeTagger Python API is provided with the official Swabian Instruments software installation.

Install the remaining Python dependencies using:

`python -m pip install -r requirements.txt`

## Configuration

Before running, modify the following parameters in `SwabianCoincidences.py`:

| Parameter | Description |
|---|---|
| `NUM_SWEEPS` | Number of complete tomography sweeps |
| `INTEGRATION` | Acquisition duration per projection, in seconds |
| `HOST`, `PORT` | Network connection to polarization analyzer |
| `servers` | Addresses of remote Time Tagger servers |
| `ch1`, `ch2` | Detector input channels |
| `binwidth`, `n_bins` | Correlation histogram settings |
| `mask` | Integration window around the coincidence peak |
| `fname_base` | Output file location and filename |

For distributed measurements, start `ServerStart.py` on the relevant remote systems before executing the acquisition script.

Update the Time Tagger serial number and reference-clock configuration to match your hardware.

## Running the Script

Run:

`python SwabianCoincidences.py`

The script automatically cycles through the configured polarization projections and records coincidence measurements.

For 36 projections with 30 seconds of integration per projection, acquisition takes approximately 18 minutes per sweep, excluding instrument communication and plotting overhead.

## Output Files

Two text files are generated:

- **Main data file:** Projection basis, singles measurements, coincidence counts, and sweep completion information.
- **COUNTSONLY file:** Coincidence counts in projection order, followed by a timestamp after each sweep.

Output files are opened in append mode. Reusing a filename will append measurements to existing files rather than overwrite them.

## Notes

- The coincidence timing-offset window must be calibrated for the experimental setup.
- The correlation plots are intended for finding this window. Disable interactive plotting for unattended acquisitions.
- Time Tagger channel assignments and clock synchronization must be verified before measurement.
- Network addresses, serial numbers, and output paths are installation-specific.
- Local analyzer connections may require modification of the provided socket configuration.

## Author

Matthew L. Stevens  
August 4, 2025
