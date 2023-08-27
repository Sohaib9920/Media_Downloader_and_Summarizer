import os
from bs4 import BeautifulSoup
import requests
import re
import dateutil.parser


class Podcast:
    def __init__(self, rss_feed_url, download_directory):
        self.rss_feed_url = rss_feed_url

        self.feed_soup = self.get_feed_soup()
        self.name = self.get_podcast_name()

        self.download_directory = os.path.join(download_directory, self.name)
        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)
        
    def get_feed_soup(self):
        response = requests.get(self.rss_feed_url)
        soup = BeautifulSoup(response.content, "lxml-xml")
        return soup

    def get_podcast_name(self):
        name = self.feed_soup.find("channel").title.text
        serialized_name = re.sub(r'[<>?:\\/"|*]', "_", name)
        return serialized_name

    def get_items(self, limit=None, filter=None):
        items = self.feed_soup.findAll("item")
        if not filter:
            return items[:limit]
        else:
            matched_items = []
            count = 0
            for item in items:
                if count == limit:
                    break
                if re.search(filter, item.title.text + item.description.text, re.I):
                    matched_items.append(item)
                    count += 1
            return matched_items
    
    @staticmethod
    def get_episodes_metadata(items):
        episodes_metadata = []
        for item in items:
            title = item.title.text
            description = item.description.text
            mp3_url = item.enclosure["url"]
            date = dateutil.parser.parse(item.pubDate.text).strftime("%b-%d-%Y")
            item_info = {"title":title, "mp3_url":mp3_url, "date":date, "description":description}
            episodes_metadata.append(item_info)
        return episodes_metadata
    
    def download_episodes(self, episodes_metadata):
        for episode in episodes_metadata:
            mp3_url = episode["mp3_url"]
            title = episode["title"]
            serialized_title = re.sub(r'[<>?:\\/"|*]', "_", title)

            filename = f"{serialized_title}.mp3"
            print(f"Downloading: {filename}", flush=True)

            file_path = os.path.join(self.download_directory, filename)
            mp3_content = requests.get(mp3_url).content

            with open(file_path, "wb") as mp3_f:
                mp3_f.write(mp3_content)
            print("Downloaded successfully :)\n", flush=True)
            

if __name__ == "__main__":
    podcasts = [Podcast("https://lexfridman.com/feed/podcast/", r"C:\Users\dell\Desktop")]
    for podcast in podcasts:
        print("---------------------------------")
        print(f"{podcast.name} podcasts")
        print("---------------------------------")

        items = podcast.get_items(limit=1, filter="deep learning")
        episodes_metadata = Podcast.get_episodes_metadata(items)
        print("\n--- Downloading Podcasts... ---\n")
        podcast.download_episodes(episodes_metadata)