import requests, linecache, os, subprocess, feedparser, argparse
from bs4 import BeautifulSoup

owd = os.getcwd()

class YouTubeDL_Current_Video_Archiver:

    def __init__(self, feed_file, additional_urls, output, current_videos_cache_file, video_depth, downloader, downloader_args):
        print("-Initialized.-")
        self.feed_file = feed_file
        self.additional_urls = additional_urls.split() #Break up the URLs into a list.
        self.parse_file = None
        self.output = output
        self.video_depth = video_depth
        self.downloader = downloader
        self.downloader_args = downloader_args
        self.current_videos_cache_file = current_videos_cache_file
        self.current_videos_cache = []
        self.feed_list = []
        self.download_list = []

    def rss_getter(self, url):
        if '/feeds/' in url:
            #If it's already an RSS feed, do nothing.
            rss_feed = url
        elif '/channel/' in url:
            #No RSS feed to be scraped, but the channel ID is included in the url, so that can be used to make one manually.
            channel_id = url.strip('https://www.youtube.com/channel/')
            rss_feed = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
        else:
            try:
                #Scrape the RSS feed from the YouTube channel's landing page. Used for detecting and downloading videos and their metadata.
                request = requests.get(url)
                soup = BeautifulSoup(request.text, 'lxml')
                rss_feed = soup.find(title="RSS").get("href")
            except TypeError:
                print(f"RSS feed not found from {url}. Skipping...")
                return
        rss_feed = rss_feed.rstrip(); url = url.rstrip() #Annoying newlines.
        self.feed_list.append(rss_feed)
        print(f"Got feed {rss_feed} from {url}.")

    def import_current_video_cache(self):
        print("-Importing current video cache...-")
        for line in self.parse_file:
            self.current_videos_cache.append(line.rstrip())

    def get_rss_feeds(self):
        print("-Getting RSS feeds...-")
        if self.feed_file.lower() != "none":
            for line in self.parse_file:
                self.rss_getter(line)
        if self.additional_urls != "":
            for url in self.additional_urls:
                self.rss_getter(url)

    def check_current_video_cache(self):
        print("-Checking current video cache...-")
        for item in self.feed_list:
            feed = feedparser.parse(item)
            print(f"Parsing feed {item.rstrip()}...")

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
        print("-Updating current videos cache file..-")
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
            if self.downloader_args != '':
                os.system(f'{self.downloader} {self.downloader_args} {link}')
            else:
                os.system(f'youtube-dl {link}')
        if self.output != os.getcwd():
            os.chdir(owd)

    def do_cycle(self):
        if self.current_videos_cache_file.lower() != "none":
            try:
                with open(self.current_videos_cache_file, 'r') as self.parse_file:
                    self.import_current_video_cache()
            except IOError:
                print("-The current video cache file doesn't exist. It will be recreated.-")
        if self.feed_file.lower() != "none":
            try:
                with open(self.feed_file, 'r') as self.parse_file:
                    self.get_rss_feeds()
            except IOError:
                print("-The feeds file doesn't exist. Skipping...-")
        else:
            self.get_rss_feeds()
        self.check_current_video_cache()
        if self.current_videos_cache_file.lower() != "none":
            with open(self.current_videos_cache_file, 'w') as self.parse_file:
                self.update_current_videos_cache()
        if self.download_list != []:
            self.download_new_videos()
        else:
            print("-No new videos were found.")
        print("-Completed.-")

argparser = argparse.ArgumentParser()
argparser.add_argument('-f', '--feeds-file',
                    default='feeds.txt',
                    dest='feed_file',
                    help="File containing YouTube channel or YouTube RSS feed URLS, one URL per line. 'None' skips scanning this file. Defaults to feeds.txt in the script's directory.",
                    type=str
                    )
argparser.add_argument('-l', '--links',
                    default='',
                    dest='additional_urls',
                    help='Additional channel URLs to be parsed for videos. Must be a "string," surrounded by quotation marks, and URLs must be separated by a space. Defaults to "".',
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
                    dest='current_videos_cache_file',
                    help="File containing the video IDs of downloaded videos, one ID per line. 'None' skips scanning this file. Defaults to current_videos.txt in the script's directory.",
                    type=str
                    )
argparser.add_argument('-v', '--video-depth',
                    default=1,
                    dest='video_depth',
                    help="How many of a channel's current videos should be checked for and stored in the current videos cache. -1 downloads everything the channel's RSS feed can detect. Defaults to 1, the newest video only.",
                    type=int
                    )
argparser.add_argument('-d', '--downloader',
                    default='youtube-dl',
                    dest='downloader',
                    help='Command-line utility used for downloading videos. Defaults to youtube-dl.',
                    type=str
                    )
argparser.add_argument('-a', '--downloader-args',
                    default='',
                    dest='downloader_args',
                    help='Arguments to be run with Youtube-dl, or whatever downloader you choose. Must be a "string," surrounded by quotation marks. Defaults to "".',
                    type=str
                    )
arg = argparser.parse_args()
YouTubeDL_Current_Video_Archiver(arg.feed_file, arg.additional_urls, arg.output, arg.current_videos_cache_file, arg.video_depth, arg.downloader, arg.downloader_args).do_cycle()
