import cv2
import os
import wave
import numpy as np
import matplotlib
import random

from random import randint
import matplotlib.pyplot as plt
from scipy.fftpack import fft


def load_config(path): # loads the configuration

    with open(path, 'r') as f: # opens file with read permissions

        data = f.read() # reads the data out of it

    data = data.split('\n') # splits after every new line

    argvals = [] # make a new list

    for z in data: # iterate through the data list

        if z != '': # if z isn't empty

            argvals.append(z) # add z to the list of values

    output = {} # make an output dictionary

    for z in argvals: # iterate through the argvalues list

        tmp = z.split('=') # split from equals sign

        output.update({tmp[0]: tmp[1]}) # add the new values to the dict

    return output # return the dict

def create_video_stream(path): # creates a video stream

    cap = cv2.VideoCapture(path) # creates the video capture

    return cap # return the video capture

def read_frame(cap, desired_size=(0,0)): # gets the desired size for the frame

    ret, frame = cap.read() # read the next frame

    if desired_size != (0,0): # if the user specified a desired size

        frame = cv2.resize(frame, desired_size) # resizes the image

    return frame # return the frame

def jump_cut(cap, nframes=20): # runs a jump cut

    for z in range(nframes): # skip the set number of rames

        read_frame(cap) # skip the frame

def create_video_writer(fname, resolution=(1920,1080), frate=30): # creates a videowriter instance

    fourcc = cv2.VideoWriter_fourcc(*'XVID') # create a videowriter codec instance

    out = cv2.VideoWriter(fname, fourcc, frate, resolution) # create the videowriter with specified params

    return out # return the videowriter

def writeframe(frame, out): # writes a video frame

    out.write(frame) # writes the frame

def Average(lst): # determines the avg of a list
    
    return sum(lst) / len(lst) # return the avg

def beatdetect(audiopath, thresh = 3000, chunk = 1024, steps = 10): # detects bass beats

    wf = wave.open(audiopath, 'rb') # open the wav file

    cnum = 0 # start at chunk 0

    output = {} # make a dictionary for time and trigger

    data = '' # set inital value

    while True:

        try: # attempt

            data = np.fromstring(wf.readframes(chunk),dtype=np.int16) # read the data

            cnum += 1 # incriment the chunk number

            currentframe = cnum * chunk # gets the current frame we're on
            
            N = 600 # set number of sample points
            
            T = 1.0 / 800.0 # sample spacing
            
            x = np.linspace(0.0, N*T, N) # do some stuff i copied from github
            
            y = data #np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
            
            yf = fft(y) # get the fft
            
            xf = np.linspace(0.0, 1.0/(2.0*T), N//2) # calc the linspace?

            bass = Average((2.0/N * np.abs(yf[0:N//2]))[:steps]) # find the average

            time = currentframe / wf.getframerate() # get the time

            if bass > thresh: # if it is past the threashold

                output.update({time: 1}) # return a 1

            else: # if not

                output.update({time: 0}) # return a 0

        except: # if it fails

            break # exit the loop
        
    return output # return the time indexes

def gencuts(beatpeaks): # generates the cuts from the beatpeaks dict

    output = [] # make the final splice index

    trigstate = 0 # make a latching variable

    for z in beatpeaks: # iterate through the beatpeaks list

        x = beatpeaks.get(z) # get the beatpeaks value

        if (x and not trigstate): # if its high and the triggerstate var is low

            trigstate = 1 # set it high

            output.append(z) # add it to the dict

        elif not x: # if x is low

            trigstate = 0 # reset trigstate

    return output # return the output dict

def clean(cuts, minstep = 0.2): # this function cleans the cuts list

    output = [] # make a new output var

    last_cut = -minstep # set the last cut to where it won't interfere

    for z in cuts: # iterate through the cuts list

        if (z - last_cut) >= minstep: # if its not too close

            output.append(z) # add it to the output

            last_cut = z # reset it

    return output # return the output list

def main(outputfname = 'output.mp4', resolution = (1920,1080), framerate = 30): # this runs the main algorithm

    config = load_config('Prefrences/config.ini') # loads the prefrences

    print('Loaded Settings') # info stuff

    out = create_video_writer(outputfname, resolution, framerate) # creates an output videowriter instance

    print('Generated Output VideoStream') # info stuff

    cap = create_video_stream(config.get('video_path')) # create a video capture

    print('Created read-only VideoStream') # info stuff

    print('Generating Audio "Beatpeaks", This will take some time') # info stuff

    beatpeaks = beatdetect(config.get('audio_path'), int(config.get('threshold')), int(config.get('chunksize')), int(config.get('steps'))) # get the beat peaks

    print('Done generating beatpeaks, Calculating Cuts.') # info stuff

    cuts = gencuts(beatpeaks) # generate the cuts based upon the beatpeaks

    print('Done generating cuts, cleaning.') # info stuff

    cuts = clean(cuts, float(config.get('minstep'))) # cleans the cuts so they're not too close together

    print('Done cleaning cuts, Rendering.') # info stuff

    time = 0 # start at 0 seconds

    while (cap.isOpened()): # loop until cap closes

        time += 1 / framerate # add the per-frame time to the clock
        
        try: # attempt to read another frame

            frame = read_frame(cap, resolution) # reads the next frame

        except: # if it fails

            break # exit the loop, and clean up

        cv2.imshow('Auto-Timelapse', frame) # shows the frame

        if cv2.waitKey(1) & 0xFF == ord('q'): # if the user pressed 'q'

            pass # do nothing

        try: # attempt

            if abs(cuts[0] - time) < 1 / framerate: # if it is to be triggered

                del cuts[0] # remove the old cuts

                print('Generated Cut at {} seconds.'.format(str(time))) # info stuff

                jump_cut(cap, randint(int(config.get('skip_frames_min')), int(config.get('skip_frames_max')))) # jump cut 20 frames

            else: # if not

                writeframe(frame, out) # writes the frame

        except: # if it fails

            break # exit the loop

    print('Done rendering, Cleaning up...') # info stuff

    cap.release() # release the videostream

    cv2.destroyAllWindows() # close the view window

    print('Done.') # info stuff


if __name__ == '__main__': # if its running as a standalone

    main() # start the main function

