from pathlib import Path
import re
from difflib import SequenceMatcher as sm

def convert_navi_playlist(input_file):
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

def get_lib_list():
    pass
    # either run find in a directory, or just process a file I put in
    # need to remove . from start, and remove all entries that aren't full paths to music files

def convert_yt_playlist(dirlisting, old_playlist_file):
    print("Reading directory listing")
    with open(dirlisting, "r") as fh:
        dirlist = fh.readlines()
        # type ref_lib = dict[str, str] 
        # key is filepath, value is songname
        ref_lib = {}
        # for item in list, extract the bit between the last slash and the . for the filename
        for item in dirlist:
            # takes item ('./path/to/file.ext'), splits on / and takes the last element, and then splits on . and takes the first element, leaving only the filename without the path or extension.
            songname = item.split("/")[-1].split(".")[-2]
            ref_lib[item] = songname

    print("Opening old playlist")
    with open(old_playlist_file, "r") as fh:
        pl_data = fh.readlines()
        new_playlist = []
        for line in pl_data:
            print(f"matching {line} ...")
            # fuzzy match that to path from list we saved to a variable from file
            # note that we have no artist data
            best_key = "NOT FOUND"
            best_ratio = 0.0
            for (key, value) in ref_lib.items():
                # compare with difflib
                # set fuzzyness to be okay
                # return unmatched values at end of script
                # see if we can set None to all types of spaces
                matchyness = sm(None, line, value).ratio()
                # find the highest matchyness, and append the key for that into new_playlist
                if matchyness > best_ratio:
                    best_ratio = matchyness
                    best_key = key

            #if best_ratio < 0.6:
            #    best_key = f"COULD NOT FIND {line}"
            #    print(f"No match found for {line}")
            #else:
            print(f"Best match for {line} was {best_key}, with ratio {best_ratio}")
            # appends the path of the matched song to the playlist list (to later be written to file)
            new_playlist.append(best_key)
            print("\n") # more readable logs

    with open(f"CONVERTED_{old_playlist_file}", "w") as fh:
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
        library = input("Path to library list file: ")
        old_playlist = input("Path to playlist to convert: ")
        convert_yt_playlist(library, old_playlist)
    elif choice == "3":
        convert_spot_playlist()
    else:
        print("Invalid choice")
        exit()



