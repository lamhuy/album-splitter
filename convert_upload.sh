export album='Nhận Thức Về Vô Thường'
export albumKey='NTVVT'
export artist='Thích Pháp Hòa'
export aristKey='TPH'

echo $album
echo $artist

python split.py -yt https://www.youtube.com/watch?v=mJLTuIby3b4 --album "$album" --artist "$artist" -sd "5" 

python upload_s3.py -b "dharmacast" -p "$artist - $album" --album "$album" --artist "$artist" -ak "$aristKey" -bk "$albumKey"