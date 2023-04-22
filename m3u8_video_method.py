import requests
import shutil
import os
import random
import sys
import math
import subprocess
import ffmpeg
from tqdm import tqdm
def overwrite_data(file):
    """write a file with random bytemaps to prevent data recovery"""
    with open(file, 'wb') as f:
        f.write(os.urandom(os.path.getsize(file)))
        f.close()
            
def cleanup_segs(dir_to_cleanup):
    try:
        for ts_file in os.listdir(dir_to_cleanup):
            if ts_file.endswith(".ts") or ts_file.endswith(".mp4"):
                ts_path = os.path.join(dir_to_cleanup, ts_file)
                overwrite_data(ts_path)
                os.remove(ts_path)
    except Exception as e:
        print(e)
        input()
        
def compile_mp4(segs,output_path):
    try:
        # RETIRED METHOD
        #with open(output_file, "wb") as f:
        #    for i, segment_url in enumerate(segment_urls):
        #        segment_file = output_dir + f"{i:04d}.ts"
        #        with open(segment_file, "rb") as s:
        #            shutil.copyfileobj(s, f)
        if len(segs) > 1200: #slow method, looking for a better method
            segment_register = []
            for i, segment_url in enumerate(segs):
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
                
            command = ['ffmpeg', '-i', 'concat:' + '|'.join(output_chunks), '-c', 'copy', output_path ]
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
            command = ['ffmpeg', '-i', 'concat:' + '|'.join(segment_register), '-c', 'copy', output_path]
            open_process = subprocess.Popen(command)
            open_process.wait()
    except Exception as e:
        print(e)
        input()
def download_segs(segs,dir_to_output,existing_segs,resume_from_last):
    try:
        for i, segment_url in enumerate(tqdm(segs)):
            if (f"{i:04d}" in existing_segs) and resume_from_last:
                continue
            segment_file = dir_to_output + f"{i:04d}.ts"
            r = session.get(segment_url, stream=True)
            with open(segment_file, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            del r
    except Exception as e:
        print(e)
        input()
        
if __name__ == "__main__":
    if not os.path.exists(os.getcwd() + "/queue.txt"):
        open("queue.txt","a")
    file = open("queue.txt", "r")
    queue = [link for link in (file.read().split("\n")) if 'http' in link]

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
        download_segs(segment_urls,output_dir,exisiting_segments,should_resume)
        print("\nappending segments to mp4 format...",end="")
        compile_mp4(segment_urls,output_file_path)
        print("ffmpeg finished creating mp4 files")
        print("cleaning up segment and chunk files...",end="")
        cleanup_segs(output_dir)
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
