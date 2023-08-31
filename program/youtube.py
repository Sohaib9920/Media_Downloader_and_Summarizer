from pytube import YouTube
import subprocess
import os


class YoutubeDownloader:
    def __init__(self, url):
        self.url = url
        self.streams = YouTube(url).streams

    def availabe_resolutions(self):
        resolutions = set()
        for stream in self.streams.filter(type="video"):
            resolutions.add(stream.resolution)
        resolutions = sorted(resolutions, key=lambda x: int(x.split("p")[0]))
        return resolutions
    
    def get_stream_by_resolution(self, res):
        # Check if progressive stream is avialable
        stream = self.streams.get_by_resolution(res)
        if not stream:
            # Otherwise check if mp4 stream is avialable
            video_stream = self.streams.filter(type="video", subtype="mp4", res=res).order_by("fps").last()
            audio_stream = self.streams.filter(type="audio", subtype="mp4").order_by("abr").last()
            stream = (video_stream, audio_stream)
            if not video_stream or not audio_stream:
                # Otherwise check if webm stream is available
                video_stream = self.streams.filter(type="video", subtype="webm", res=res).order_by("fps").last()
                audio_stream = self.streams.filter(type="audio", subtype="webm").order_by("abr").last()
                stream = (video_stream, audio_stream)
            
            size_mb = video_stream.filesize_mb + audio_stream.filesize_mb
        else:
            size_mb = stream.filesize_mb
            stream = (stream,None)
            
        return stream, size_mb

    def download_stream(self, stream, download_directory):
        video_stream = stream[0]
        audio_stream = stream[1]
        print("Donwloading video...", flush=True)
        if audio_stream: # i.e stream is not progressive
            video_filepath = video_stream.download(output_path=download_directory, filename="video")
            print("Downloading audio...", flush=True)
            audio_filepath = audio_stream.download(output_path=download_directory, filename="audio")
            print("Merging audio and video...", flush=True)
            output_filepath = os.path.join(download_directory, f"{video_stream.default_filename.split('.')[0]}.mp4")
            
            # Run FFmpeg command to merge video and audio
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', video_filepath,
                '-i', audio_filepath,
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-y',
                output_filepath
            ]
        
            subprocess.run(ffmpeg_cmd, check=True)
            
            os.remove(video_filepath)
            os.remove(audio_filepath)
        else:
            output_filepath = video_stream.download(output_path=download_directory)

        print(f"Downloaded successfully: {output_filepath}", flush=True)

    def download_mp3(self, download_directory):
        audio_stream = self.streams.get_audio_only()
        print("Donwloading audio...", flush=True)
        audio_filepath = audio_stream.download(output_path=download_directory, filename="audio")
        print("Converting to mp3 (320kbps)...", flush=True)
        output_filepath = os.path.join(download_directory, f"{audio_stream.default_filename.split('.')[0]}.mp3")
            
        # Run FFmpeg command to merge video and audio
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', audio_filepath,
            '-b:a', '320k',
            '-y',
            output_filepath
        ]
            
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.remove(audio_filepath)
        print(f"Downloaded successfully: {output_filepath}", flush=True)


if __name__ == "__main__":
    yt = YoutubeDownloader("https://www.youtube.com/watch?v=38NQU8yCxvs")
    stream, size_mb = yt.get_stream_by_resolution("720p")
    yt.download_stream(stream, r"C:\Users\dell\Desktop\New folder")
