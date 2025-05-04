import base64
from api_requests import get_text_response, get_audio_response
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import cv2
import os

class CommentaryGenerator:
    
    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def generate_commentary_text(self, images_data, past_commentary):
        """
        Generate commentary based on a list of images and text input.
        
        Args:
            images (list): List of images (numpy arrays)
            text (str): Text input for commentary generation
            
        Returns:
            text (str): Commentary text
        """
        # Process images in batches of 5
        
        # Look at the sequence of images and describe what is happening in each image. \
        # Be specific yet casual and funny as a general sports commentator would be. \
        # The end user is a person with visual impairments \
        # and your commentary will help them understand whats happening in the match. \
        # If a another string is added as input, that is the commentary for the past frames. \
        # Use as that as a reference along with the images to generate the commentary for the current frames. \
        # The whole commentary should be readable by a text-to-speech engine in a natural language within 5 seconds.
        
        user_content = []
        for i in range(0, len(images_data)):
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{images_data[i]}"}
                })

            # [
            #     {
            #         "type": "text",
            #         "text": "You are a sports video commentator AI for a visually impaired audience. I will input 5 sequential frames sampled at the rate of 0.5 Hz from a video. Your goal is to describe what is happening in the frames, as if you are providing commentary for a sports game. \
            #         Output your result in JSON format, where each entry includes a timestamp (in seconds) and a natural-sounding single sentence that can be read by a human in under 2 seconds. \
            #         Example output: \
            #         [ \
            #             {\"t\": 0, \"d\": \"A man walks into the room, looking around curiously.\"}, \
            #             {\"t\": 2, \"d\": \"He notices a cup on the table and starts walking toward it.\"}, \
            #             {\"t\": 4, \"d\": \"The man picks up the cup and examines it closely.\"}, \
            #             {\"t\": 6, \"d\": \"He takes a sip and seems to enjoy the drink.\"}, \
            #             {\"t\": 8, \"d\": \"Smiling, he places the cup back on the table and sits down.\"} \
            #         ] \
            #         Only, provide output in JSON format. In addition, I provide previous commentary. Use the 'previous commentary' as a context for this task. \
            #         Adjust the timestamp number for the output so that it lies after the last entry in the previous commentary. The timestamp value should be in seconds and should be a multiple of 2 starting from.",
            #     }
            # ]

        messages=[
            {
                "role": "system",
                "content": [
                {
                    "type": "text",
                    "text": "You are a sports video commentator AI for a visually impaired audience. I will input 5 sequential frames sampled at the rate of 0.5 Hz from a video. Your goal is to describe what is happening in the frames, as if you are providing commentary for a sports game. \
                    The output is a single text string describing the events in a 2 short sentences that can spoken under 9 seconds. This condition is very important as I will convert the text output to speech and that must to lower than 9 seconds long.\
                    Only, provide description in the output in text string format with no other text. In addition, I provide previous commentary. If present, use the 'previous commentary' as a context for this task. Please be aware of replays in sport broadcas and if you find one, mention it in the output.",
                },
                {
                    "type": "text",
                    "text": f"Previous commentary: {past_commentary}"
                }
            ]
            },
            {
                "role": "user",             
                "content": user_content,
                "max_completion_tokens": 1024,
            }
        ]
            
        response = get_text_response(model="Llama-4-Scout-17B-16E-Instruct-FP8",
                                     messages=messages,
                                     stream=False)
        
        return response


    def generate_commentary_audio(self, text, previous_text="", path="commentary.mp3"):
        audio_bytes = get_audio_response(text, previous_text=previous_text)
        with open(path, "wb") as f:
            for chunk in audio_bytes:
                f.write(chunk)


    def combine_video_and_audio(self, video_path, audio_dir, output_path):

        # --- Load the base video ---
        video_clip = VideoFileClip(video_path)
        video_duration = video_clip.duration

        # --- Load and place audio clips ---
        audio_clips = []
        interval = 10  # seconds between audio inputs

        for t in range(0, int(video_duration), interval):
            audio_file = os.path.join(audio_dir, f"commentary_{t//interval:04d}.mp3")
            if os.path.exists(audio_file):
                audio = AudioFileClip(audio_file).set_start(t)
                audio_clips.append(audio)
            else:
                print(f"[Warning] Missing audio for timestamp {t}s: {audio_file}")

        # --- Combine all audio tracks ---
        composite_audio = CompositeAudioClip(audio_clips)

        # --- Overlay audio on the original video ---
        final_video = video_clip.set_audio(composite_audio)

        # --- Export the final video ---
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")