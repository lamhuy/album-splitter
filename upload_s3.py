import argparse
import os
import re
import sys
import json
import urllib.parse
import boto3
import botocore

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
    ALBUM_NAME = args.album
    ARTIST_NAME = args.artist       
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
    json = {}
    json["title"] = ALBUM_NAME
    json["playlist"] = []
    for i, track in enumerate(tracks_titles):
      #  track = track.decode('utf-8')
        if(i == len(tracks_titles)-1):
            break;
            
        #print(i)
        #print(len(tracks_titles))
        data = {}
        data["title"] = track
        if ARTIST_NAME:
            data["artist"] = ARTIST_NAME
        data["src"] = S3_BUCKET _ BUCKET_PATH + track + '.mp3'
        
        json["playlist"].append(data)
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
    PLAYLIST_FILE = 'playlist_' + ALBUM_KEY + '.json'  
    
    # Uploads the given file using a managed uploader, which will split up large
    # files automatically and upload parts in parallel.
    s3.Object(BUCKET_NAME, BUCKET_PATH +PLAYLIST_FILE).put(Body=json)
    
    
    
    #download dhramaCast_ARTIST_KEY.json, append this dharmaCast_ARTIST_KEY.json info, then upload
    ARTIST_JSON_FILE = ARTIST_KEY + '/dharmaCast_'+ARTIST_KEY +'.json'
    S3_BUCKET = 'http://'+BUCKET_NAME+'.s3-website-us-east-1.amazonaws.com/'
    s3 = boto3.resource('s3')


    #adding album into into artist dharma cast list
    try:
        artist_json = s3.Object(BUCKET_NAME, ARTIST_JSON_FILE).get()["Body"]
        artist_json = json.load(artist_json)
    except botocore.exceptions.ClientError as e:
        print(e.response['Error']['Code'])
        if e.response['Error']['Code'] == "NoSuchKey":
            print("The object does not exist. creating ARTIST_JSON_FILE")
            artist_json = {}
            artist_json['title'] = ARTIST_NAME
            data = {}
            data['title'] = ALBUM_NAME
            data['listName'] = ALBUM_KEY
            data['id'] = 1
            artist_json['playlists'] = []
            artist_json['playlists'].append(data)
        else:
            raise

    print(artist_json)
    print(artist_json["playlists"])
    albumExist = False

    for i, playlist in enumerate(artist_json["playlists"]):
        print(playlist["listName"])
        if(ARTIST_KEY == playlist["listName"]):
            albumExist = True
            break;


    if(not albumExist):
        print("adding album to artist_json")
        #build json object, append it
        data = {}
        data['title'] = ALBUM_NAME
        data['listName'] = ALBUM_KEY
        data['id'] = len(artist_json["playlists"])+1
        artist_json["playlists"].append(data)
        print(artist_json["playlists"])
        #upload new file into S3
        #s3.Object(BUCKET_NAME, ARTIST_JSON_FILE).put(Body=artist_json)

    else:
        print("ALBUM EXIST")


    #adding artist into dharma cast.json list
    DHARMA_JSON_FILE = 'dharmaCast.json'
    dharma_json = s3.Object(BUCKET_NAME, DHARMA_JSON_FILE).get()["Body"]
    artistExist = False

    dharma_json = json.load(dharma_json)
    print(dharma_json)

    for i, artist in enumerate(dharma_json):
        print(artist["listName"])
        if(ARTIST_KEY == artist["listName"]):
            artistExist = True
            break;


    if(not artistExist):
        print("adding artist to dharma_json")
        #build json object, append it
        data = {}
        data['title'] = ARTIST_NAME
        data['listName'] = ARTIST_KEY
        data['id'] = len(dharma_json)+1
        dharma_json.append(data)
        print(dharma_json)
        #upload new file into S3
        #s3.Object(BUCKET_NAME, ARTIST_JSON_FILE).put(Body=artist_json)

    else:
        print("ARTIST EXIST")
    