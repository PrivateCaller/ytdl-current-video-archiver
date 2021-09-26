# ytdl-current-video-archiver
A Python 3 script that reads YouTube channel URLs from a file, scrapes their RSS feeds, then downloads their latest video(s) with youtube-dl and saves the video IDs to a cache file. Intended for to be run regularly, for continuous video archiving.
# Options
| Command | Description |
| --- | --- |
| -i, --input | File containing YouTube channel or YouTube RSS feed URLS, one URL per line. Defaults to feeds.txt in the script's directory. |
| -o, --output | Directory downloaded videos are sent to. Defaults to the script's directory. |
| -c, --curent-videos-cache | File containing the video IDs of downloaded videos, one ID per line. Defaults to current_videos.txt in the script's directory. |
| -v, --video-depth | How many of a channel's current videos should be checked for and stored in the current videos cache. -1 downloads everything the channel's RSS feed can detect. Defaults to 1, the newest video only. |
| -y, --ytdl-args | Arguments to be run with Youtube-dl. Must be a "string," surrounded by quotation marks. Defaults to "". |
