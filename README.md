# Introduction

This script synchronizes gameplay feeds from two seperate StepManiaX sessions by automatically adding source delays in
OBS. Use clean gameplay sources at 1080p for the best result. The script can use a seperate scene from your stream
feeds.

# Prerequisites

1. Install [Python 3](https://www.python.org/downloads/)
2. Install
   [OBS Dynamic Delay](https://obsproject.com/forum/resources/dynamic-delay.1035/version/4615/download?file=89293)
   plugin

# OBS setup

1. Open *Tools -> Websocket Server* and enable it. Copy the password for later
2. Create a new scene
3. Add both players as sources in the new scene, place them vertically so the top half of both are visible
4. Add a dynamic delay filter to both sources, keep the default name
5. Open  *File -> Settings -> Hotkeys*:
    1. Add F6 as *Skip Begin*, F7 as *Skip End* for the player 1 source
    2. Add F8 as *Skip Begin*, F9 as *Skip End* for the player 2 source
6. Configure the OBS Virtual Camera to always output this scene

# Script setup

Install dependencies:

```
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

1. Copy *config.example* to *config.py*
2. Edit *config.py* with your configuration

# Run the script

```
.venv\Scripts\activate.bat
python smx-obs-sync.py
```
