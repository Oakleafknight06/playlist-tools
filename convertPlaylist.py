#! /usr/bin/env python3

from pathlib import Path
import re
from difflib import SequenceMatcher as sm

# BRAINSTORMING COMMENTS
# Intermediary list of dicts with various attributes should be abstracted out. Import function outputs that, export function exports to whatever. That way export function can be shared with Spotify import function
# I'll want to do this with both the new library and the playlist items. Playlist items will need to store index in playlist?
# How do I handle no album, no artist, eg singles without folder? For library can decide based on mine and make some assumptions about folder structure. Playlists.. can make some assumptions too but the youtube converter would have to be different. Collection data from YT, spotify, and navidrome/generic .m3u from a sorted music library will be three different ways. Leads me to not abstract that out of the specific from X to generic .m3u of your library type. NOTE: converting to absolute paths a la navidrome and relative paths the way gonic operates is different. NOTE: does the find . command give me enough info to even do absolute paths? Perhaps allow specifying a thing to go in front of the music/asdf/asdf, as that's defined by the find. so ../.. for gonic, /home/user/path/to/music/.....


def log(logfile, message):
    """Takes 'logfile' and 'message' strings. Appends 'message' to the specified 'logfile' filename"""
    with open(logfile, "a") as fh:
        fh.write(f"{message}\n")


def format_lib_list(file) -> list:
    """takes in a file assumed created by 'find . > file.txt' and returns a formatted list of filepaths"""
    lib_list = []
    with open(file, "r") as fh:
        filelines = fh.readlines()
        for line in filelines:
            filename = line.split("/")[-1]
            if filename.find(".") != -1:
                lib_list.append(line[1:].strip())

    return lib_list


def create_struct_lib(library_list: list[str, str]) -> list[dict, dict]:
    """Takes in a list generated from the library filepaths and returns a dict"""
    # Create dictionary of songs to compare against, with key=PATH and value=songname
    struct_lib = []
    # List of dictionaries? ie list = [dict {path: thing, songname: name, artist: hey, album: hey}]

    # each <item> is a string containing the path of the music file
    for item in library_list:
        # Initialize dictionary for <item>'s attributes
        item_dict = {}

        # Add path, removing \n from the end
        item_dict["path"] = item.strip()

        # takes item ('./path/to/file.ext'), splits on / and takes the last element 
        songname = item.split("/")[-1]
        # splits on '.' and takes the first element, leaving only the filename without the path or extension.
        songname = songname.split(".")[-2]
        # remove 'disc 01' etc from songname
        songname = re.sub(r'(?i)^\s*Disc\s*\d+\s*-*\s*', '', songname)
        # remove track number at beginning of songname
        songname = re.sub(r'^\d+[\s|-]-*\s*', '', songname)
        # Add songname to dict
        item_dict["name"] = songname


        # ditto for album
        album = item.split("/")[-2]
        item_dict["album"] = album


        # and artist
        artist = item.split("/")[-3]
        item_dict["artist"] = artist

        # NOTE: the above assumes /path/to/collection/<artist>/<album>/<track> folder structure

        # Add to list
        struct_lib.append(item_dict)

    return struct_lib


def import_m3u(old_pl_file):
    with open (old_pl_file, "r") as fh:
        # Get list from file
        pl_data = fh.readlines()
        # Removes M3U metadata
        pl_nometa = []
        for line in pl_data:
            if line[0] != '#':
                pl_nometa.append(line)
        # Formats into the list/dict structure for comparison    
        formatted_pl_data = create_struct_lib(pl_nometa)
    return formatted_pl_data


def match_pl_to_lib(old_pl, ref_lib, logfile):
    # Ideal is no false positives in playlist, prefer missing entries. Look in logs for things instead

    # A list where each line is a path, i.e. the line we will write to the output file
    new_playlist = []

    # I should probably do a better search algorithm rather than just going through every single item
    # oh well computer go brr
    log(logfile, "----------MATCHING PLAYLIST ITEMS----------")
    for item in old_pl:
        name = item["name"]
        album = item["album"]
        artist = item["artist"]

        name_best_ratio = 0.0
        album_best_ratio = 0.0
        artist_best_ratio = 0.0

        best_match = ""

        for lib_item in ref_lib:
            lib_name = lib_item["name"]
            lib_album = lib_item["album"]
            lib_artist = lib_item["artist"]

            name_match_ratio = sm(None, name, lib_name).ratio()
            album_match_ratio = sm(None, album, lib_album).ratio()
            artist_match_ratio = sm(None, artist, lib_artist).ratio()

            if name_match_ratio > name_best_ratio:
                # THIS CURRENTLY ONLY MATCHES WITH NAME. HAVE NOT YET DONE MATH TO REQUIRE ALL THREE TO MATCH
                name_best_ratio = name_match_ratio
                best_match = lib_item["path"]

        new_playlist.append(best_match)
        log(logfile, f"Best match for \"{item["path"]}\" was \"{best_match}\"")
    log(logfile, "----------END MATCHING----------")
    return new_playlist


def write_export(matched_pl, pl_name, playlist_type = None):
    """ Takes 'matched_pl' object, 'pl_name' string, and optional 'playlist_type' string. Returns None"""
    with open(f"NEW_{pl_name}.m3u", "w") as fh:
        fh.write(f"#EXTM3U\n")
        fh.write(f"#PLAYLIST:{playlist_name}\n")
        if playlist_type == 'gonic':
            fh.write(f'#GONIC-NAME:"{playlist_name}"\n')
            for i in range(len(matched_pl)):
                matched_pl[i] = f"../..{matched_pl[i]}"

        for entry in matched_pl:
            fh.write(f"{entry}\n")
    print(f"Done! Saved to NEW_{pl_name}.m3u, logs saved to NEW_{pl_name}.log")


if __name__ == "__main__":
    old_file = input("Enter the filename of the playlist to convert: ")
    library = input("Enter the filename of the library list thing you made with `find`: ")
    playlist_name = input("Enter the name of the playlist: ")
    convert_type = input("Enter the type to convert to: [gonic|...] ")
    logfilename = f"NEW_{playlist_name}.log"

    # this will be used for new_playlist.m3u, new_playlist.log, etc
    ref_lib = create_struct_lib(format_lib_list(library))
    log(logfilename, f"ref_lib:\n{ref_lib}\n")

    # import playlist to correct format
    formatted_old_playlist = import_m3u(old_file)
    log(logfilename, f"Old Playlist:\n{formatted_old_playlist}\n")

    # match old playlist to library, return new playlist in correct format
    new_pl = match_pl_to_lib(formatted_old_playlist, ref_lib, logfilename)

    # write to m3u file
    write_export(new_pl, playlist_name, convert_type)



# def convert_yt_playlist(library_list, old_playlist_file):
#     print("Reading music library listing")
# 
#     # Create dictionary of songs to compare against, with key=PATH and value=songname
#     ref_lib = {}
#     for item in library_list:
#         # takes item ('./path/to/file.ext'), splits on / and takes the last element 
#         songname = item.split("/")[-1]
#         # splits on '.' and takes the first element, leaving only the filename without the path or extension.
#         songname = songname.split(".")[0]
#         # remove 'disc 01' etc from songname
#         songname = re.sub(r'(?i)^\s*Disc\s*\d+\s*-*\s*', '', songname)
#         # remove track number at beginning of songname
#         songname = re.sub(r'^\d+[\s|-]-*\s*', '', songname)
#         # put songname in dictionary
#         ref_lib[item] = songname
# 
#     print("Opening old playlist")
#     with open(old_playlist_file, "r") as fh:
#         # Get list from file
#         pl_data = fh.readlines()
# 
#         # Remove playlist m3u metadata, save name to variable
#         playlist_name = pl_data.pop(1)
#         pl_data.pop(0)
# 
#         # Initialize new playlist list object
#         new_playlist = []
# 
#         # Matching
#         for line in pl_data:
#             f_line = line.split(".")[0]
#             print(f"matching {f_line} ...")
#             # fuzzy match that to path from list we saved to a variable from file
#             # note that we have no artist data
#             best_key = "NOT FOUND"
#             best_ratio = 0.0
#             for (key, value) in ref_lib.items():
#                 # compare with difflib
#                 # set fuzzyness to be okay
#                 # return unmatched values at end of script
#                 # see if we can set None to all types of spaces
#                 matchyness = sm(None, f_line, value).ratio()
#                 # find the highest matchyness, and append the key for that into new_playlist
#                 if matchyness > best_ratio:
#                     best_ratio = matchyness
#                     best_key = key
# 
#             if best_ratio < 0.8:
#                 #best_key = f"COULD NOT FIND {line}"
#                 best_key = "CHECK THIS LINE" + best_key
#             #    print(f"No match found for {line}")
#             #else:
#             print(f"Best match for {line} was {best_key}, with ratio {best_ratio}")
#             # appends the path of the matched song to the playlist list (to later be written to file)
#             new_playlist.append(best_key)
#             print("\n") # more readable logs
# 
#     # NOTE requires script to be run in same directory as old_playlist_file, and file supplied with no leading ./
#     with open(f"CONVERTED_{old_playlist_file}", "w") as fh:
#         # Write playlist metadata
#         fh.write(f"#EXTM3U\n{playlist_name}")
#         # write each line of new_playlist to file
#         for entry in new_playlist:
#             fh.write(entry)
#     print(f"Done! Saved to CONVERTED_{old_playlist_file}")

# Deprecated
# def convert_navi_playlist(input_file):
#     # TODO refactor so one can input strings to replace and rename generically
#     with open(input_file, "r") as fh:
#         newfile = ""
#         for line in fh:
#             if line[0] == "/":
#                 if line[7:14] == "Youtube":
#                     # Delete that, and replace with "from-yt"
#                     line = line[0:7] + "from-yt" + line[14:]
#                 if line[7:9] == "CD":
#                     line = line[0:7] + "owned" + line[9:]
#             newfile += line
#     with open(input_file, "w") as fh:
#         fh.write(newfile)

