import requests
import shutil
import os
import random
import sys
import math
import subprocess
import ffmpeg
file = open("queue.txt", "r")
queue = file.read().split("\n")
to_write = queue.copy()
file.close()
session = requests.Session()
session.headers.update({'Accept-Encoding': 'gzip'})
if not queue:
    print("no files in queue, please add them to queue.txt seperated by a new line")
    sys. exit()
    
output_dir = os.getcwd() + "/segments/"
video_output_dir = os.getcwd() + "/output/"

if not os.path.exists(output_dir):
    os.mkdir(output_dir)
if not os.path.exists(video_output_dir):
    os.mkdir(video_output_dir)
    
def progress_bar(percent=0, width=30):
    """display a updating progress bar with static position in cmd prompt"""
    left = width * percent // 100
    right = width - left
    print('\r[', '#' * left, ' ' * right, ']',
        f' {percent:.0f}%',
        sep='', end='', flush=True)
    
def overwrite_data(file):
    """write a file with random bytemaps to prevent data recovery"""
    for i in range(5):
        with open(file, 'wb') as f:
            f.write(os.urandom(os.path.getsize(file)))

            f.close()
for video_url in queue:
    output_file = ''.join(chr(random.randint(128, 512)) for _ in range(7)) + ".mp4"

    output_file_path = video_output_dir + output_file
    
    r = requests.get(video_url)
    playlist = r.text
    segment_urls = []
    lines = playlist.split("\n")
    for line in lines:
        if ".ts" in line:
            line = line.strip()
            if "https" not in line:
                url_soup = video_url.split("/")
                url_soup.pop() #remove end url
                line = "/".join(url_soup) + "/" + line #add base url to packet id
            segment_urls.append(line)
    
    num_segments = len(segment_urls)

    exisiting_segments = []
    for existing in os.listdir(output_dir):
        exisiting_segments.append(existing[:4])
    should_resume = False
    if exisiting_segments:
        if input(f"resume at {max(exisiting_segments)}? y/n //:").lower() == "y":
            should_resume = True
    print("downloading segments")
    try:
        for i, segment_url in enumerate(segment_urls):
            if (f"{i:04d}" in exisiting_segments) and should_resume:
                progress_bar(math.ceil(i/num_segments * 100))
                continue
            segment_file = output_dir + f"{i:04d}.ts"
            r = session.get(segment_url, stream=True)
            with open(segment_file, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            del r
            progress_bar(math.ceil(i/num_segments * 100))
    except Exception as e:
        print(e)
        input()

    print("\nappending segments to mp4 format...",end="")
    try:
        # RETIRED METHOD
        #with open(output_file, "wb") as f:
        #    for i, segment_url in enumerate(segment_urls):
        #        segment_file = output_dir + f"{i:04d}.ts"
        #        with open(segment_file, "rb") as s:
        #            shutil.copyfileobj(s, f)
        if len(segment_urls) > 1200: #slow method, looking for a better method
            segment_register = []
            for i, segment_url in enumerate(segment_urls):
                segment_file = output_dir + f"{i:04d}.ts"
                segment_register.append(segment_file)

            max_args_per_run = 800  # Adjust this value as needed
            segment_chunks = [segment_register[i:i + max_args_per_run] for i in range(0, len(segment_register), max_args_per_run)]

            output_chunks = []
            for chunk in segment_chunks:
                output_chunk = f"{chunk[0]}_output.ts"
                command = ['ffmpeg', '-i', 'concat:' + '|'.join(chunk), '-c', 'copy', output_chunk]
                open_process = subprocess.Popen(command)
                open_process.wait()
                output_chunks.append(output_chunk)
                
            command = ['ffmpeg', '-i', 'concat:' + '|'.join(output_chunks), '-c', 'copy', output_file]
            open_process = subprocess.Popen(command)
            open_process.wait()
            #video_clips = [VideoFileClip(file_name) for file_name in output_chunks]
            #final_clip = concatenate_videoclips(video_clips)
            #final_clip.write_videofile(output_file)
            
        else: #very fast
            segment_register = []
            for i, segment_url in enumerate(segment_urls):
                segment_file = output_dir + f"{i:04d}.ts"
                segment_register.append(segment_file)
            command = ['ffmpeg', '-i', 'concat:' + '|'.join(segment_register), '-c', 'copy', output_file_path]
            open_process = subprocess.Popen(command)
            open_process.wait()
            
    except Exception as e:
        print(e)
        input()
    print("ffmpeg finished creating mp4 files")
    print("cleaning up segment and chunk files...",end="")
    try:
        for ts_file in os.listdir(output_dir):
            if ts_file.endswith(".ts") or ts_file.endswith(".mp4"):
                ts_path = os.path.join(output_dir, ts_file)
                overwrite_data(ts_path)
                os.remove(ts_path)
    except Exception as e:
        print(e)
        input()
    print(" done")

    print(f"removing {video_url} from queue...",end = "")
    try:
        with open("queue.txt", "w") as q:
            to_write.remove(video_url)
            q.write('\n'.join(to_write))
            q.close()
    except Exception as e:
        print(e)
        input()
    print(" done")
input()
