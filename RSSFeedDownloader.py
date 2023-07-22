import sys
import os
import requests
import feedparser
import json
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import TIT2

USER_DIRECTORY = "\\Desktop\\"


class Episode:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, pod_name, num, title, mp3):
        self.podcast_name = pod_name
        self.file_name = pod_name + "_" + num + ".mp3"
        self.file_dir = str(Path.home()) + USER_DIRECTORY + pod_name + "\\"
        self.num = num
        self.title = title
        self.mp3 = mp3


def download(pod_episode: Episode):
    url = pod_episode.mp3
    dest_folder = pod_episode.file_dir
    if not os.path.exists(dest_folder):  # if it does not exist
        os.makedirs(dest_folder)  # create folder

    file_path = os.path.join(dest_folder, pod_episode.file_name)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving ", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))


def make_podcast(podcast_episode):
    enclosure = podcast_episode.enclosures
    embeds = json.loads(str(enclosure[0]).replace("'", "\""))
    sode = Episode(feed.feed.title, ep.itunes_episode, ep.itunes_title, dict(embeds)['href'])
    return sode


def set_pod_title(podcast_episode: Episode):
    audio = MP3(podcast_episode.file_dir + "\\" + podcast_episode.file_name)
    audio["TIT2"] = TIT2(text=["" + podcast_episode.num + ": " + podcast_episode.title])
    audio.save()


rss_url = sys.argv[1]
print("downloading entries from " + rss_url)
feed = feedparser.parse(rss_url)
for i in range(0, len(feed.entries)):
    ep = feed.entries[i]
    episode = make_podcast(ep)
    download(episode)
    set_pod_title(episode)
