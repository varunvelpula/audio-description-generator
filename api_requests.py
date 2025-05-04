import requests
import json
import os
from elevenlabs.client import ElevenLabs

from llama_api_client import LlamaAPIClient


def get_text_response(model, messages, stream=False):
    completion = client_llama.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
    )
    return completion.completion_message.content.text   

def get_audio_response(text, previous_text="", model_id="eleven_flash_v2", voice_id="CwhRBWXzGAHq8TQ4Fs17", output_format="mp3_44100_128"):
    response = client_elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        voice_settings={"stability": 0.3, "similarity_boost": 0.5, "speed": 1.2},
        previous_text=previous_text,
        output_format=output_format
    )
    print(response)
    return response