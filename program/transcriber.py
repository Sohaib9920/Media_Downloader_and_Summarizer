import os
import requests
import time           


class Transcriber:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.assemblyai.com/v2"

    def upload_file(self, file_path):
        # Upload local media file to Assembly AI API
        print("Uploading...", flush=True)
        headers = {"authorization": self.api_key}
        with open(file_path, "rb") as f:
            response = requests.post(self.base_url + "/upload", 
                                    headers=headers, 
                                    data=f)
        error = response.json().get("error")
        if error:
            raise Exception(error)
        upload_url = response.json()["upload_url"]
        return upload_url
    
    def send_transcribe_request(self, audio_url, **kwargs):
        # Sending transcript request to Assembly AI API
        print("Sending transcibe request...", flush=True)
        json = {"audio_url": audio_url}
        json.update(kwargs)
        headers = {"authorization": self.api_key}
        response = requests.post(self.base_url + "/transcript", json = json, headers=headers)
        error = response.json().get("error")
        if error:
            raise Exception(error)
        transcript_id = response.json()["id"]
        return transcript_id

    def get_output(self, transcript_id):
        print("Fetching output...", flush=True)
        # Use transcript ID to poll the API every few seconds for transcript output
        polling_endpoint = f"{self.base_url}/transcript/{transcript_id}"
        headers = {"authorization": self.api_key}
        while True:
            transcription_result = requests.get(polling_endpoint, headers=headers).json()
            if transcription_result['status'] == 'completed':
                print("Success!\n", flush=True)
                return transcription_result
            elif transcription_result["status"] == "error":
                raise RuntimeError(f"Transcription failed: {transcription_result['error']}")
            else:
                time.sleep(3)
    
    def transcribe(self, file_path, **kwargs):
        # Overall transcribe function
        print(f"Transcribing: {os.path.basename(file_path).split('.')[0]}", flush=True)
        audio_url = self.upload_file(file_path)
        transcript_id = self.send_transcribe_request(audio_url, **kwargs)
        transcription_result = self.get_output(transcript_id)
        return transcription_result

    @staticmethod
    def save_output(output_directory, filename, transcription_result):
        # Saving output into local txt file
        output_filename = filename + ".txt"
        output_path = os.path.join(output_directory, output_filename)
        with open(output_path, "w") as f:
            if transcription_result.get("auto_chapters") == True:
                for chapter in transcription_result["chapters"]:
                    f.write(f"Chapter Start Time: {chapter['start']}\n")
                    f.write(f"Chapter End Time: {chapter['end']}\n")
                    f.write(f"Chapter Gist: {chapter['gist']}\n")
                    f.write(f"Chapter Headline: {chapter['headline']}\n")
                    f.write(f"Chapter Summary: {chapter['summary']}\n\n")
            elif transcription_result.get("summarization") == True:
                f.write(transcription_result.get("summary", ""))


