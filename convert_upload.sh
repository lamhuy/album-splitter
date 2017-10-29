
export album='Cần Quên - Nên Nhớ'
export albumKey='CQCN'
export albumSearch='Can Quan Nho CQCN'
export artist='Thích Pháp Hòa'
export aristKey='TPH'
export artistSearch='Phap Hoa TPH PH'
export albumDate='09/25/2016'
export ytlink='https://www.youtube.com/watch?v=Dd5qO3o2tKc'

echo $album


python3 split.py -yt $ytlink --album "$album" --artist "$artist" -sd "10" 

python3 upload_s3.py -b 'dharmacast' -p "$artist - $album" --album "$album" --artist "$artist" -ak "$aristKey" -Ak "$albumKey" -Ad "$albumDate" -As "$albumSearch" -as "$artistSearch"