import json
import io

nonlat = []
nonlat.append(u'Tiếng')
nonlat.append('a32')

#print(json.dumps(nonlat, ensure_ascii=False).encode('utf8'))

#write as json string with nonlatin character into file
with open('nonlat.txt', 'w', encoding='utf8') as f:
    json.dump(nonlat, f, ensure_ascii=False)

#loading nonlat file content
with open('nonlat.txt') as data_file:    
    tracks_titles = json.load(data_file)
print(json.dumps(tracks_titles, ensure_ascii=False).encode('utf8'))

#loading nonlat filename
filename =u'Nhận Thức Về Vô Thường.json'.encode()
#print(filename)
with open(filename, encoding='utf8') as data:  
    #print("nonlatin file content: " + data.read())
    tracks_titles = json.load(data)
    
print(json.dumps(tracks_titles, ensure_ascii=False).encode('utf8'))





import boto3
import botocore

BUCKET_NAME = 'dharmacast'

S3_BUCKET = 'http://'+BUCKET_NAME+'.s3-website-us-east-1.amazonaws.com/'
s3 = boto3.resource('s3')

s3.Object(BUCKET_NAME, 'Tiếng/Tiếng.json').put(Body=open('nonlat.txt', 'rb'))