import argparse
import os
import re
import sys
import json
from queue import Queue
from threading import Thread
from uuid import uuid4

from urllib.parse import urlparse, parse_qs
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment
from youtube_dl import YoutubeDL

from utils import (time_to_seconds, track_parser, update_time_change)


metadata_providers = []
for module in os.listdir("MetaDataProviders"):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    metadata_providers.append(__import__("MetaDataProviders." + module[:-3], fromlist=[""]))


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def thread_func(album, tracks_start, queue, FOLDER):
    while not queue.empty():
        song_tuple = queue.get()
        split_song(album, tracks_start, song_tuple[0], song_tuple[1], FOLDER)


def split_song(album, tracks_start, index, track, FOLDER):
    #print(json.dumps(nonlat, ensure_ascii=False).encode('utf8'))
    print("\t{}) {}".format(str(index+1), track.encode()))
    start = tracks_start[index]
    end = tracks_start[index+1]
    duration = end-start
    track_path = '{}/{}.mp3'.format(FOLDER, track)
    album[start:][:duration].export(track_path, bitrate='64k', format="mp3")

    print("\t\tTagging")
    song = EasyID3(track_path)
    if ARTIST:
            song['artist'] = ARTIST
    if ALBUM:
            song['album'] = ALBUM
    song['title'] = track
    song['tracknumber'] = str(index+1)
    song.save()


def my_hook(d):
    if d['status'] == 'downloading':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownloading video | ETA: {} seconds'.format(str(d["eta"])))
        sys.stdout.flush()
    elif d['status'] == 'finished':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownload complete\n\tConverting video to mp3')
        sys.stdout.flush()


# youtube_dl configuration
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '0',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}


def split( TRACKS_FILE_NAME, FILENAME, YT_URL, ALBUM, ARTIST, DURATION, THREADED,  NUM_THREADS, SEGMENT_DURATION, DRYRUN):
    # input validation
    if SEGMENT_DURATION is not None:
        try:
            val = int(SEGMENT_DURATION)
            print("split by segment of ", SEGMENT_DURATION, " min")
        except ValueError:
            print("That's not an int!")
            exit()

    if DRYRUN:
        print("**** DRY RUN ****")

   
    if ALBUM and ARTIST:
        FOLDER = "{} - {}".format(ARTIST, ALBUM)
    else:
        if YT_URL:
            url_data = urlparse(YT_URL)
            query = parse_qs(url_data.query)
            video_id = query["v"][0]
            FOLDER = "./splits/{}".format(video_id)
        else:
            FOLDER = "./splits/{}".format(str(uuid4())[:16])
    

    # create destination folder
    if not os.path.exists(FOLDER) and not DRYRUN:
        os.makedirs(FOLDER)

 
    tracks_start = []
    tracks_titles = []

    
    if SEGMENT_DURATION is None:
        print("Parsing " + TRACKS_FILE_NAME)
        with open(TRACKS_FILE_NAME) as tracks_file:
            time_elapsed = '0:00:00'
            for i, line in enumerate(tracks_file):
                curr_start, curr_title = track_parser(line)

                if DRYRUN:
                    print(curr_title + " *** " + curr_start)

                if DURATION:
                    t_start = time_to_seconds(time_elapsed)
                    time_elapsed = update_time_change(time_elapsed, curr_start)
                else:
                    t_start = time_to_seconds(curr_start)

                tracks_start.append(t_start*1000)
                tracks_titles.append(curr_title)
            
    if DRYRUN:
        exit()


    album = None
    if YT_URL:
        url_data = urlparse(YT_URL)
        query = parse_qs(url_data.query)
        video_id = query["v"][0]
        FILENAME = video_id + ".wav"
        if not os.path.isfile(FILENAME):
                print("Downloading video from YouTube")
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download(['http://www.youtube.com/watch?v=' + video_id])
                print("\nConversion complete")
        else:
                print("Found matching file")
        print("Loading audio file")
        album = AudioSegment.from_file(FILENAME, 'wav')
    else:
        print("Loading audio file")
        album = AudioSegment.from_file(FILENAME, 'mp3')
    print("Audio file loaded")

    #given the length of the album, determine the split size, for 5 min segment each
    albumLen = len(album)
    print("Album Len: ", albumLen)

    if SEGMENT_DURATION is not None:
        # 5 mins
        segmentLen = int(SEGMENT_DURATION)*60*1000 
        numTracks = int(round(albumLen/segmentLen))

        for i in range(0, numTracks):           
            tracks_start.append(i*segmentLen)
            if ALBUM:
                tracks_titles.append('{:02d} - {}'.format(i+1, ALBUM)) #continue work here, split append the number, mismatch with tracks.json
                
            else:
                tracks_titles.append('{:02d} - {} {}'.format(i+1, "Track", i+1))

    tracks_start.append(len(album))  # we need this for the last track/split

    # ['When I Was Young', 'Dogs Eating Dogs', 'Disaster', 'END']
    # [0, 28000, 60000, 117818]

    print("Starting to split")
    if THREADED and NUM_THREADS > 1:
        # Create our queue of indexes and track titles
        queue = Queue()
        for index, track in enumerate(tracks_titles):
            queue.put((index, track))
        # initialize/start threads
        threads = []
        for i in range(NUM_THREADS):
            new_thread = Thread(target=thread_func, args=(album, tracks_start, queue, FOLDER))
            new_thread.start()
            threads.append(new_thread)
        # wait for them to finish
        for thread in threads:
            thread.join()
    # Non threaded execution
    else:
        tracks_titles.append("END")
        #print(tracks_titles)
        print(json.dumps(tracks_titles, ensure_ascii=False).encode('utf8'))
        for i, track in enumerate(tracks_titles):
            if i != len(tracks_titles)-1:
                split_song(album, tracks_start, i, track, FOLDER)
    
    
    #output track.json
    with open(ALBUM+'.json', 'w', encoding='utf8') as trackFile:
        json.dump(tracks_titles, trackFile, ensure_ascii=False)
        
    
    print("All Done")
