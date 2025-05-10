# Superstar Racing Installer

A Python-based installer for Superstar Racing with a graphical interface, featuring a progress bar and automatic game download.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Installer

To run the installer in development mode:
```bash
python installer.py
```

## Compiling to EXE

To compile the installer into a standalone executable:
```bash
pyinstaller installer.spec --clean
```

The compiled executable will be available in the `dist` directory.