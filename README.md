# playlist-tools
A set of scripts to convert playlists from various formats to .m3u files for whatever player of your local music library you so choose.

## Usage
* Run `find ./music > library.txt` on your music directory
* Get the old playlist (currently only .m3u format input supported)
* Run the script with ./convertPlaylist.py
* Script will output the new playlist and log file

## Future Plans
* Implement a threshold to prefer 'NO MATCH FOUND' to erroneous matches
    * Configurable with cli flag and default value
* Better handling of input filenames
* Accept Spotify account data export as an input method
* Slugify playlist name for filename creation

## How it works
* Takes input to a generic dictionary format, and matches the input playlist to the input library in that format. Translates matched output (same format) to specified output format (currently gonic or generic .m3u)

