export album='What Kind of Man'
export artist='uTiếng Viễt'
echo $album
echo $artist

#python split.py -yt https://www.youtube.com/watch?v=v489sYYjtHI --album "$album" --artist "$artist" -sd "5" 

python upload_s3.py -b "dharmacast" -p "$artist - $album" --album "$album" --artist "$artist" -ak "JC" -bk "WKM" --dry-run