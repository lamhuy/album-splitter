


export album='Người Nào Nghiệp Nấy'
export albumKey='NNNN'
export albumSearch='Nguoi Nao Nghiep Nay'
export albumDate='12/11/2015'
export albumLoc='Perth Australia'
export albumSrc='https://www.youtube.com/watch?v=-IHpwKa0E2Q'
export artist='Thích Pháp Hòa'
export aristKey='TPH'
export artistSearch='Phap Hoa PH'




export album='Lecture on Happiness'
export albumKey='LOH'
export albumSearch='Lecture on Happiness'
export albumDate='04/10/2013'
export albumLoc='Georgetown District of Colombia'
export albumSrc='https://www.youtube.com/watch?v=-IHpwKa0E2Q'
export artist='Venerable Ajahn Jayasaro Bhikkhu'
export aristKey='AJB'
export artistSearch='Ajahn Jayasaro Bhikkhu'



export album='Practicing positive emotion'
export albumKey='PPE'
export albumSearch='Practicing positive emotion'
export albumDate='08/04/2013'
export albumLoc='Bahn Boon, Rai Thawsi, Pakchong, Nakong'
export albumSrc='https://www.youtube.com/watch?v=Js7VVJK5SX0'
export artist='Ajahn Jayasaro Bhikkhu'
export aristKey='AJB'
export artistSearch='Ajahn Jayasaro Bhikkhu'


export album='Change your Mind Change your Brain'
export albumKey='CMCB'
export albumSearch='Change your Mind Change your Brain'
export albumDate='03/15/2007'
export albumLoc='Google Campus CA'
export albumSrc='https://www.youtube.com/watch?v=L_30JzRGDHI'
export artist='Matthieu Richard'
export aristKey='MR'
export artistSearch='Matthieu Richard'


export album='The habits of happiness'
export albumKey='HH'
export albumSearch='The habits of happiness'
export albumDate='04/15/2008'
export albumLoc='TED'
export albumSrc='https://www.youtube.com/watch?v=vbLEf4HR74E'
export artist='Matthieu Richard'
export aristKey='MR'
export artistSearch='Matthieu Richard'

echo $album


python split.py -yt $albumSrc --album "$album" --artist "$artist" -sd "10" 

python upload_s3.py -b 'dharmacast' -p "$artist - $album" --album "$album" --artist "$artist" -ak "$aristKey" -Ak "$albumKey" -Ad "$albumDate" -As "$albumSearch" -as "$artistSearch" -Asc "$albumSrc" -Al "$albumLoc"