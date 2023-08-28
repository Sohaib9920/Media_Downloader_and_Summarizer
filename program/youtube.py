from pytube import YouTube
from moviepy.editor import AudioFileClip
import os


class YoutubeDownloader:
    def __init__(self, url):
        self.url = url
        self.streams = YouTube(url).streams

    def download_video(self, download_directory, res="high"):
        # Downloading stream with both audio & video i.e prograssive=True
        if res == "high":
            video_stream = self.streams.get_highest_resolution()
        elif res == "low":
            video_stream = self.streams.get_lowest_resolution()
        else:
            raise Exception("Invalid value")
        print(f"Downloading...", flush=True)
        file_path = video_stream.download(download_directory)
        print("Success!", flush=True)
        return file_path

    def download_audio(self, download_directory, res="high", format=None):
        # Download stream of only audio
        if res == "high":
            audio_stream = self.streams.filter(only_audio=True).desc()[0]
        elif res == "low":
            audio_stream = self.streams.filter(only_audio=True).desc()[-1]
            print(audio_stream.filesize_mb)
        else:
            raise Exception("Invalid value")
        print(f"Downloading...", flush=True)
        file_path = audio_stream.download(download_directory)

        if format == "mp3":
            # Converting to mp3 file
            print("Converting to mp3...", flush=True)
            mp3_file_path = os.path.splitext(file_path)[0] + ".mp3"
            audio_clip = AudioFileClip(file_path)
            audio_clip.write_audiofile(mp3_file_path, codec="mp3")
            audio_clip.close()
            os.remove(file_path)
            return mp3_file_path
            
        print("Success!", flush=True)
        return file_path
        

