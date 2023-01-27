import time
import random
import os
import re
import sys
import subprocess

from os import listdir
from os.path import isfile, join

def extract_duration(string):
    match = re.search(r'Duration: (\d{2}:\d{2}:\d{2}.\d{2})', string)
    if match:
        return match.group(1)
    else:
        return None

string1 = "Duration: 00:00:00.23, bitrate: 707 kb/s"

# usage: python granulate.py [wav.file] [frag_len_ms]

# Check for the correct number of arguments
if len(sys.argv) != 3:
    print("Usage: python script.py input.wav split_time1 split_time2")
    sys.exit(1)

# Assign the arguments to variables
input_file = sys.argv[1]
frag_duration = int(sys.argv[2])

# get the wav file length in miliseconds
time_dirty = subprocess.check_output('ffmpeg -i '+input_file+' 2>&1 | grep Duration', shell=True) * 1000
clip_len = extract_duration(str(time_dirty))
#print('time:'+str(time))
hms, ds = clip_len.split('.')
s = hms.split(':')[2]
ms = (int(s) + int(ds)/100) * 1000
#print("ms:"+str(ms))

# find out how many grans based on gran length in ms
grans = ms / float(frag_duration)
#print("grans:"+str(grans))

# make a temp dir to store grans
if not os.path.exists('grans'): os.mkdir('grans')
if not os.path.exists('output'): os.mkdir('output')

for i in range(int(grans)):
    # get string for start time
    s = round((i * frag_duration) / 1000)
    ds = ((i * frag_duration) / 1000) % 1
    start_time = "00:00:" + str("{:02d}".format(s)) + '.' +  str(ds).split('.')[1][:2]
    clip_time = str(frag_duration/1000)
    fade_time = str(frag_duration/10000)
    fade = "afade=in:st=0:d=0."+fade_time+",afade=out:st=duration-0."+fade_time+":d=A"
    cmd = "ffmpeg -i "+input_file+" -ss "+start_time+" -t "+clip_time + fade +  " -c copy grans/"+str(i)+".wav -loglevel quiet"
    print(cmd)
    subprocess.Popen(["bash","-c", cmd])

    # add fade
#    ffmpeg -i input.wav -af "afade=in:st=0:d=5,afade=out:st=duration-5:d=5" -c:a pcm_s16le output.wav


# Now get a list of all the files we created
wavs = [f for f in listdir('grans') if isfile(join('grans', f))]
random.shuffle(wavs)

# touch filex txt for ffmpeg to ref
subprocess.Popen(["bash","-c", "touch files.txt"])

# rename the new ordered wavs
for i in range(len(wavs)):
    subprocess.Popen(["bash","-c", "echo file grans/"+str(wavs[i])+ " >> files.txt"])
    

# concat them 
cmd = "ffmpeg -f concat -safe 0 -i files.txt -c copy output/stitched_"+str(frag_duration)+"_"+str(int(time.time()))+".wav && rm files.txt && rm -rf grans"

subprocess.Popen(["bash","-c", cmd])

