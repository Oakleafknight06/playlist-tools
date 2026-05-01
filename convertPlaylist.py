#! /usr/bin/env python3

from pathlib import Path
import re
from difflib import SequenceMatcher as sm

def convert_navi_playlist(input_file):
    # TODO refactor so one can input strings to replace
    with open(input_file, "r") as fh:
        newfile = ""
        for line in fh:
            if line[0] == "/":
                if line[7:14] == "Youtube":
                    # Delete that, and replace with "from-yt"
                    line = line[0:7] + "from-yt" + line[14:]
                if line[7:9] == "CD":
                    line = line[0:7] + "owned" + line[9:]
            newfile += line
    with open(input_file, "w") as fh:
        fh.write(newfile)

def format_lib_list(file) -> list:
    """takes in a file assumed to be 'find . > file.txt' and returns a formatted list"""
    new_file = []
    with open(file, "r") as fh:
        filelines = fh.readlines()
        for line in filelines:
            filename = line.split("/")[-1]
            if filename.find(".") != -1:
                new_file.append(line[1:])

    return new_file

def convert_yt_playlist(library_list, old_playlist_file):
    print("Reading music library listing")

    # Create dictionary of songs to compare against, with key=PATH and value=songname
    ref_lib = {}
    for item in library_list:
        # takes item ('./path/to/file.ext'), splits on / and takes the last element 
        songname = item.split("/")[-1]
        # splits on '.' and takes the first element, leaving only the filename without the path or extension.
        songname = songname.split(".")[0]
        # remove 'disc 01' etc from songname
        songname = re.sub(r'(?i)^\s*Disc\s*\d+\s*-*\s*', '', songname)
        # remove track number at beginning of songname
        songname = re.sub(r'^\d+[\s|-]-*\s*', '', songname)
        # put songname in dictionary
        ref_lib[item] = songname

    print("Opening old playlist")
    with open(old_playlist_file, "r") as fh:
        # Get list from file
        pl_data = fh.readlines()

        # Remove playlist m3u metadata, save name to variable
        playlist_name = pl_data.pop(1)
        pl_data.pop(0)

        # Initialize new playlist list object
        new_playlist = []

        # Matching
        for line in pl_data:
            f_line = line.split(".")[0]
            print(f"matching {f_line} ...")
            # fuzzy match that to path from list we saved to a variable from file
            # note that we have no artist data
            best_key = "NOT FOUND"
            best_ratio = 0.0
            for (key, value) in ref_lib.items():
                # compare with difflib
                # set fuzzyness to be okay
                # return unmatched values at end of script
                # see if we can set None to all types of spaces
                matchyness = sm(None, f_line, value).ratio()
                # find the highest matchyness, and append the key for that into new_playlist
                if matchyness > best_ratio:
                    best_ratio = matchyness
                    best_key = key

            if best_ratio < 0.7:
                best_key = f"COULD NOT FIND {line}"
                print(f"No match found for {line}")
            else:
                print(f"Best match for {line} was {best_key}, with ratio {best_ratio}")
            # appends the path of the matched song to the playlist list (to later be written to file)
            new_playlist.append(best_key)
            print("\n") # more readable logs

    # NOTE requires script to be run in same directory as old_playlist_file, and file supplied with no leading ./
    with open(f"CONVERTED_{old_playlist_file}", "w") as fh:
        # Write playlist metadata
        fh.write(f"#EXTM3U\n{playlist_name}")
        # write each line of new_playlist to file
        for entry in new_playlist:
            fh.write(entry)
    print(f"Done! Saved to CONVERTED_{old_playlist_file}")

def convert_spot_playlist():
    # same as above, but use spotify export format, parse json
    pass

# add missing file handling

if __name__ == "__main__":
    dir = Path("./")

    # get input, and use if tree to decide which function to apply to given playlist(s) or directory

    choice = input("Navidrome[1] YouTube[2] Spotify[3] > ")
    if choice == "1":
        for m3u_file in dir.glob("*.m3u"):
            print(f"converting {m3u_file}...")
            convert_playlist(m3u_file)
    elif choice == "2":
        in_library = input("Path to library list file: ")
        library = format_lib_list(in_library)
        old_playlist = input("Path to playlist to convert: ")
        convert_yt_playlist(library, old_playlist)
    elif choice == "3":
        convert_spot_playlist()
    else:
        print("Invalid choice")
        exit()



