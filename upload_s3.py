import argparse
import os
import re
import sys
import json
import urllib.parse
import boto3

from queue import Queue
from threading import Thread
from uuid import uuid4

from urllib.parse import urlparse, parse_qs
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment
from youtube_dl import YoutubeDL

if __name__ == "__main__":
    # arg parsing
    parser = argparse.ArgumentParser(description='create a play list json, upload the tracks and playlist into s3.')
  
    parser.add_argument(
        "-a", "--artist",
        help="Specify the artist that the json is tagged with. Default: no tag",
        default=None
    )
    parser.add_argument(
        "-A",  "--album",
        help="Specify the album that the json is tagged with . Default: no tag",
        default=None
    )
    parser.add_argument(
        "-p", "--path", help="Specify the relative path to tracks folder. Default: tracks.txt", 
        required=True
    )
    parser.add_argument(
        "-ak", "--artistkey", help="Specify the artist key value. Default: UNK", 
        default="UNK"
    )
    parser.add_argument(
        "-bk", "--albumkey", help="Specify the album key value. Default: noalbum", 
        default="noalbum"
    )
    parser.add_argument(
        "-b", "--bucket", help="Specify the S3 bucket name.", 
        required=True        
    )
    parser.add_argument(
        "-t", "--tracks", help="Specify the tracks file. Default: tracks.json", default="tracks.json"
    )

    args = parser.parse_args()
    
    TRACKS_FILE_NAME = args.tracks
    PATH_MP3 = args.path  
    ALBUM = args.album
    ARTIST = args.artist       
    ARTIST_KEY = args.akey
    ALBUM_KEY = args.bkey   
    BUCKET_NAME = args.bucket    
    
    
    BUCKET_PATH = ARTIST_KEY + '/' + ALBUM_KEY + '/'
    S3_BUCKET = 'http://'+BUCKET_NAME+'.s3-website-us-east-1.amazonaws.com/'
    s3 = boto3.resource('s3')
    
    #if found no tracks.json will terminaet
    with open(TRACKS_FILE_NAME) as data_file:    
        tracks_titles = json.load(data_file)
        
    print(tracks_titles)
    
    #tracks_titles=['Đường Xưa Mây Trắng'.encode('utf8'), 'Dogs Eating Dogs', 'Disaster', 'END']
    #tracks_titles=['abc', 'Dogs Eating Dogs', 'Disaster', 'END']

    json = '{ \n\t"title" : "'
    json += ALBUM
    json += '",\n'
    json += '\t"playlist": [ { \n'
    
    for i, track in enumerate(tracks_titles):
      #  track = track.decode('utf-8')
        if(i == len(tracks_titles)-1):
            break;
            
        #print(i)
        #print(len(tracks_titles))
        json += '\t\t"title": "' + track + '",\n'
        if ARTIST:
            json += '\t\t"artist": "' + ARTIST + '",\n'
        json += '\t\t"src": "' + S3_BUCKET + BUCKET_PATH + track + '.mp3"\n'        
        if(i < len(tracks_titles)-2):         
            json += '\t}, { \n'
    
    json += '\t} ] \n }'
    print(json) 
    
    print('Uploading mp3 tracks')
    dirPath = os.path.dirname(os.path.realpath(__file__))  # /home/user/test
    
    for i, track in enumerate(tracks_titles):
        if(i == len(tracks_titles)-1):
            break;
        mp3Filename = dirPath + '/' + PATH_MP3+ '/' + track+'.mp3'
        s3.Object(BUCKET_NAME, BUCKET_PATH + track+'.mp3').put(Body=open(mp3Filename, 'rb'))
    
    
    
    #upload playlist into aws 
    print('Uploading playlist')
    filename = 'playlist_' + ALBUM_KEY + '.json'  
    
    # Uploads the given file using a managed uploader, which will split up large
    # files automatically and upload parts in parallel.
    s3.Object(BUCKET_NAME, BUCKET_PATH +filename).put(Body=json)
    
    #download dhramaCast_ARTIST_KEY.json, append this playlist info, then upload
    
    