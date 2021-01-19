# nanocosm

Nanocosm experiment with Daphnia Magna and Culex Pipiens

## installation procedure

+ install python
+ create virtual environment named 'env':  python -m venv env
+ activate environment ./env/Scripts/activate (on Linux: source ./env/bin/activate)
+ upgrade pip:   python -m pip install --upgrade pip
+ install requirements: pip install -r requirements.txt

## priorities

1. [ ] write functions to plot the timeseries (Then I have at least the performance of Daphnia)
2. [ ] Important: Write detector for Culex
3. [ ] write code that moves all images out of subfolders (for first sessions)
4. [ ] Control QR codes
5. [ ] manually label QR codes which could not be read
6. [ ] what about zero sized images?
7. [ ] Address memory problems when six images were taken from one nanocosm (need 1.2 GB memory)
8. [ ] write cluster script to process images
