#we want to:
touch log.txt
#touch error_log.txt
#redirect the collector logger output to the file
    #python3 script.py 2>log.txt #redirect to file
#open another terminal window / tab in which we call tail --follow:
    #gnome-terminal -- /bin/sh -c 'tail log.txt --follow'

gnome-terminal -- /bin/sh -c 'tail log.txt --follow'
python3 script.py #2>error_log.txt
