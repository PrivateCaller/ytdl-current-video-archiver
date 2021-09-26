import requests, linecache, os, subprocess, feedparser, argparse
from bs4 import BeautifulSoup

owd = os.getcwd()

class YouTubeDL_Current_Video_Archiver:

    def __init__(self, input, output, current_videos_cache_file, video_depth, ytdl_args):
        print("-Initialized.-")
        self.input = input
        self.output = output
        self.video_depth = video_depth
        self.youtube_dl_args = ytdl_args
        self.parse_file = None
        self.current_videos_cache_file = current_videos_cache_file
        self.current_videos_cache = []
        self.feed_list = []
        self.download_list = []

    def import_current_video_cache(self):
        print("-Importing current video cache...-")
        try:
            for line in self.parse_file:
                self.current_videos_cache.append(line.rstrip())
        except IOError:
            print("The current video cache file doesn't exist. It will be recreated.")

    def get_rss_feeds(self):
        print("-Getting RSS feeds...-")
        for line in self.parse_file:
            if 'feeds/videos.xml' in line:
                #If it's an RSS feed, skip this step.
                self.feed_list.append(line)
                continue
            #Scrape the RSS feed from the YouTube channel's landing page. Used for detecting and downloading videos and their metadata.
            request = requests.get(line)
            soup = BeautifulSoup(request.text, 'lxml')
            rss_feed = soup.find(title="RSS").get("href")
            print(f"Got feed {rss_feed}.")
            self.feed_list.append(rss_feed)

    def check_current_video_cache(self):
        print("-Checking current video cache...-")
        for item in self.feed_list:
            feed = feedparser.parse(item)
            print(f"Parsing feed {item}...")

            if self.video_depth != -1:
                for video in range(0, self.video_depth):
                    video = feed.entries[video]
                    video_id = video.yt_videoid

                    if not video_id in self.current_videos_cache:
                        self.current_videos_cache.append(video_id)
                        self.download_list.append(video)
            else:
                #If self.video_depth is set to -1, download everything the channel's RSS feed can detect.
                for item in feed.entries:
                    video_id = item.yt_videoid

                    if not video_id in self.current_videos_cache:
                        self.current_videos_cache.append(video_id)
                        self.download_list.append(item)

    def update_current_videos_cache(self):
        print("-Updating Current Videos Cache File-")
        for item in self.current_videos_cache:
            self.parse_file.write(item + '\n')

    def download_new_videos(self):
        print("-Downloading New Videos-")
        if self.output != os.getcwd():
            os.chdir(self.output)
        for video in self.download_list:
            link = video.link
            title = video.title
            author = video.author

            print(f"Downloading {title} by {author}...")
            if self.youtube_dl_args != '':
                os.system(f'youtube-dl {self.youtube_dl_args} {link}')
            else:
                os.system(f'youtube-dl {link}')
        if self.output != os.getcwd():
            os.chdir(owd)

    def do_cycle(self):
        with open(self.current_videos_cache_file, 'r') as self.parse_file:
            self.import_current_video_cache()
        with open(self.input, 'r') as self.parse_file:
            self.get_rss_feeds()
        self.check_current_video_cache()
        with open(self.current_videos_cache_file, 'w') as self.parse_file:
            self.update_current_videos_cache()
        if self.download_list != []:
            self.download_new_videos()
        print("-Completed.-")

argparser = argparse.ArgumentParser()
argparser.add_argument('-i', '--input',
                    default='feeds.txt',
                    dest='input',
                    help="File containing YouTube channel or YouTube RSS feed URLS, one URL per line. Defaults to feeds.txt in the script's directory.",
                    type=str
                    )
argparser.add_argument('-o', '--output',
                    default=os.getcwd(),
                    dest='output',
                    help="Directory downloaded videos are sent to. Defaults to the script's directory.",
                    type=str
                    )
argparser.add_argument('-c', '--current-videos-cache',
                    default='current_videos.txt',
                    dest='current_videos_cache',
                    help="File containing the video IDs of downloaded videos, one ID per line. Defaults to current_videos.txt in the script's directory.",
                    type=str
                    )
argparser.add_argument('-v', '--video-depth',
                    default=1,
                    dest='video_depth',
                    help="How many of a channel's current videos should be checked for and stored in the current videos cache. -1 downloads everything the channel's RSS feed can detect. Defaults to 1, the newest video only.",
                    type=int
                    )
argparser.add_argument('-y', '--ytdl-args',
                    default='',
                    dest='ytdl_args',
                    help='Arguments to be run with Youtube-dl. Must be a "string," surrounded by quotation marks. Defaults to "".',
                    type=str
                    )
arg = argparser.parse_args()
YouTubeDL_Current_Video_Archiver(arg.input, arg.output, arg.current_videos_cache, arg.video_depth, arg.ytdl_args).do_cycle()
