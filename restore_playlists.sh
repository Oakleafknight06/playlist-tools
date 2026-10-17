#!/bin/bash

# Script by ryogamasaki on Jellyfin forums, reproduced here for archival purposes.
# https://forum.jellyfin.org/t-guide-recoving-lost-playlists
#
# Use as follows:
# Grep the Jellyfin logs for the not-found playlist items:
# grep -l "cannot be found at" jellyfin*.log
# Then run this script with the log redirected to sdtin:
# ./restore_playlists1.sh < jellyfin20250926.log

regex='^.*Item in \"(.+)\" cannot be found at \"(.+)\"$'



while read line; do

        if [[ $line =~ $regex ]]; then

                playlist="${BASH_REMATCH[1]}.m3u"

                item="${BASH_REMATCH[2]}"

                echo "$item" >> "$playlist"

        fi

done
