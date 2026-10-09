#! /usr/bin/env python3

from pathlib import Path
import re
from difflib import SequenceMatcher as sm


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

        log(logfile, f"\n-----Matching {name}-----")

        artist_best_ratio = 0.0
        album_best_ratio = 0.0
        name_best_ratio = 0.0
        best_match = "NONE"

        for lib_item in ref_lib:
           artist_match_ratio = sm(None, artist, lib_item["artist"]).ratio()
           if artist_match_ratio > artist_best_ratio:
               log(logfile, f"art_r: {artist_match_ratio}, item: {lib_item["path"]}")
               best_match = lib_item
               artist_best_ratio = artist_match_ratio
        for lib_item in ref_lib:
           album_match_ratio = sm(None, album, lib_item["album"]).ratio()
           if (album_match_ratio > album_best_ratio) and (lib_item["artist"] == best_match["artist"]):
               log(logfile, f"album_r: {album_match_ratio}, item: {lib_item["path"]}")
               best_match = lib_item
               album_best_ratio = album_match_ratio
        for lib_item in ref_lib:
           name_match_ratio = sm(None, name, lib_item["name"]).ratio()
           if (name_match_ratio > name_best_ratio) and (lib_item["artist"] == best_match["artist"]) and (lib_item["album"] == best_match["album"]):
               log(logfile, f"name_r: {name_match_ratio}, item: {lib_item["path"]}")
               best_match = lib_item
               name_best_ratio = name_match_ratio

        new_playlist.append(best_match["path"])
        log(logfile, f"---Best match for \"{item["path"]}\" was \"{best_match}\"---\n")
    log(logfile, "----------END MATCHING----------")
    return new_playlist


def write_export(matched_pl, pl_name, playlist_type = None):
    """ Takes 'matched_pl' object, 'pl_name' string, and optional 'playlist_type' string. Returns None"""
    with open(f"NEW_{pl_name}.m3u", "w") as fh:
        if playlist_type == 'gonic':
            fh.write(f'#GONIC-NAME:"{playlist_name}"\n')
            for i in range(len(matched_pl)):
                matched_pl[i] = f"../..{matched_pl[i]}"
        else:
            fh.write(f"#EXTM3U\n")
            fh.write(f"#PLAYLIST:{playlist_name}\n")

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
    # log(logfilename, f"ref_lib:\n{ref_lib}\n")

    # import playlist to correct format
    formatted_old_playlist = import_m3u(old_file)
    log(logfilename, f"Old Playlist:\n{formatted_old_playlist}\n")

    # match old playlist to library, return new playlist in correct format
    new_pl = match_pl_to_lib(formatted_old_playlist, ref_lib, logfilename)

    # write to m3u file
    write_export(new_pl, playlist_name, convert_type)

