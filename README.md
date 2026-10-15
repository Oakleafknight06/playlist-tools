# playlist-tools
A set of scripts to convert playlists from various places into .m3u with absolute paths for whatever player of your local music library you so choose.
Run `find ./music > library.txt` on your music directory, and then format that with the library script before using the main script.


## todo/notes:
- omit 'Disc 1', '01' etc from matching. Maybe split on - too?
- further testing on threshold for matching
- Files from directory listing MUST have file extensions, otherwise will not be counted. is probably fine
- implement logging instead of printing everything to terminal

maybe write same old version of match name return best match, but do thrice. once for name, once for artist, once for album. then match other criteria if the things aren't the same??

# BRAINSTORMING COMMENTS
# Intermediary list of dicts with various attributes should be abstracted out. Import function outputs that, export function exports to whatever. That way export function can be shared with Spotify import function
# I'll want to do this with both the new library and the playlist items. Playlist items will need to store index in playlist?
# How do I handle no album, no artist, eg singles without folder? For library can decide based on mine and make some assumptions about folder structure. Playlists.. can make some assumptions too but the youtube converter would have to be different. Collection data from YT, spotify, and navidrome/generic .m3u from a sorted music library will be three different ways. Leads me to not abstract that out of the specific from X to generic .m3u of your library type. NOTE: converting to absolute paths a la navidrome and relative paths the way gonic operates is different. NOTE: does the find . command give me enough info to even do absolute paths? Perhaps allow specifying a thing to go in front of the music/asdf/asdf, as that's defined by the find. so ../.. for gonic, /home/user/path/to/music/.....


new todo:
validate input to some extent
have a way for it to get files like shell does... maybe pass as args?
slugify the playlist name so any character can be in file but filename is not any extras

some chinese songs didn't work, may be because changed filename from roman to character or vice versa. Can fix by having threshold at all three layers, and log but do not write if not above 85% or whatever (can configure cli flag?)
