# playlist-tools
A set of scripts to convert playlists from various places into .m3u with absolute paths for whatever player of your local music library you so choose.
Run `find . > library.txt` in your music directory, and then format that with the library script before using the main script.


## todo/notes:
- omit 'Disc 1', '01' etc from matching. Maybe split on - too?
- further testing on threshold for matching
- Files from directory listing MUST have file extensions, otherwise will not be counted. is probably fine
- implement logging instead of printing everything to terminal
