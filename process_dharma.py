import argparse
import csv
import os
import re
import sys
import json
import urllib.parse
import boto3
import botocore
import codecs

from queue import Queue
from threading import Thread
from uuid import uuid4

from urllib.parse import urlparse, parse_qs
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment
from youtube_dl import YoutubeDL

import module_upload_s3
import module_split

if __name__ == "__main__":
    # arg parsing
    parser = argparse.ArgumentParser(description='read from csv, create a play list json, upload the tracks and playlist into s3.')
  
    parser.add_argument(
        "-f", "--file",
        help="Specify the artist that the json is tagged with. Default: no tag",
        default=None
    )   
    parser.add_argument(
        "--dry-run",
        dest='dry',
        action='store_true',
        help="Don't upload any file.",
        default=False
    )


    args = parser.parse_args()
    
    FILE = args.file
   # PATH_MP3 = args.path  
    DRYRUN = args.dry
    
    

  
    with open('album.csv', encoding='utf8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if(row['active'] == 'x'):
                print("Processing: ", row['artist'].encode() ,row ['album'].encode())
                #                  TRACKS_FILE_NAME, FILENAME, YT_URL, ALBUM, ARTIST, DURATION, THREADED,  NUM_THREADS, SEGMENT_DURATION, DRYRUN):
                module_split.split("", "", row ['albumSrc'], row ['album'], row ['artist'], "", "",  "", "10", "TRUE")
                module_upload_s3.upload_s3(row ['album'],row ['albumKey'], row ['albumDate'], row ['albumSearch'], row ['albumSrc'], row ['albumLoc'], row ['artist'], row ['artistKey'], row ['artistSearch'], row ['Bucket'], "dry-run")
           
    
    
    
   
    