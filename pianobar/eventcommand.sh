#!/bin/bash

# from http://raspberrypiserver.no-ip.org/pianobar_pandora_remote_control.html
# http://raspberrypiserver.no-ip.org/eventcommand.sh 

fold="$HOME/.config/pianobar"
stl="$fold/stationlist"
ctlf="$fold/ctl"
nowplaying="$fold/nowplaying"
status="$fold/status"
rm -f "$status"
while read L; do
        k="`echo "$L" | cut -d '=' -f 1`"
        v="`echo "$L" | cut -d '=' -f 2`"
        export "$k=$v"
        echo "$L" >> "$status-$1"
done < <(grep -e '^\(title\|artist\|album\|stationName\|pRet\|pRetStr\|wRet\|wRetStr\|songDuration\|songPlayed\|rating\|songDuration\|songPlayed\|coverArt\|stationCount\|station[0-9]\+\)=' /dev/stdin)

case "$1" in
        songstart)
        echo -e "artist:$artist\ntitle:$title\nstationName:$stationName\nrating:$rating\ncoverArt:$coverArt\nalbum:$album" > "$nowplaying"
;;
	songlove)
        echo -e "artist:$artist\ntitle:$title\nstationName:$stationName\nrating:$rating\ncoverArt:$coverArt\nalbum:$album" > "$nowplaying"
;;
	songban)
	echo -e "" > "$nowplaying"
;;
	
	 usergetstations)
	   if [[ $stationCount -gt 0 ]]; then
		  rm -f "$stl"
		  for stnum in $(seq 0 $(($stationCount-1))); do
			 echo "$stnum) "$(eval "echo \$station$stnum") >> "$stl"
		  done
	   fi

	   ;;
	   stationcreate)
           if [[ $stationCount -gt 0 ]]; then
                  rm -f "$stl"
                  for stnum in $(seq 0 $(($stationCount-1))); do
                         echo "$stnum) "$(eval "echo \$station$stnum") >> "$stl"
                  done
           fi

           ;;
	stationaddgenre)
         if [[ $stationCount -gt 0 ]]; then
                  rm -f "$stl"
                  for stnum in $(seq 0 $(($stationCount-1))); do
                         echo "$stnum) "$(eval "echo \$station$stnum") >> "$stl"
                  done
           fi

           ;;
	songexplain)
          if [[ $stationCount -gt 0 ]]; then
                  rm -f "$stl"
                  for stnum in $(seq 0 $(($stationCount-1))); do
                         echo "$stnum) "$(eval "echo \$station$stnum") >> "$stl"
                  done
           fi

           ;;
           stationaddshared)
          if [[ $stationCount -gt 0 ]]; then
                  rm -f "$stl"
                  for stnum in $(seq 0 $(($stationCount-1))); do
                         echo "$stnum) "$(eval "echo \$station$stnum") >> "$stl"
                  done
           fi

           ;;
        stationdelete)
           if [[ $stationCount -gt 0 ]]; then
                  rm -f "$stl"
                  for stnum in $(seq 0 $(($stationCount-1))); do
                         echo "$stnum) "$(eval "echo \$station$stnum") >> "$stl"
                  done
           fi
		echo -e "" > "$nowplaying"
           ;;
esac
