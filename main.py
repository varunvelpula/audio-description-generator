from parse_frames import parse_video_frames
from generate_commentary import CommentaryGenerator
from pathlib import Path
import glob
import json

FORCE_REGENERATE = False
def main(video_path, output_video_path, upload_time_str):
    # Initialize the commentary generator
    commentary_gen = CommentaryGenerator()
    
    # Create data directory
    data_dir = f"{upload_time_str}_data"
    if not Path(f"{data_dir}").exists():
        Path(f"{data_dir}").mkdir(parents=True, exist_ok=True)
    
    # Parse video frames
    print("Parsing video frames")
    if not Path(f"{data_dir}/frames").exists() or len(glob.glob(f"{data_dir}/frames/*.jpg")) == 0:
        ret = parse_video_frames(video_path, frame_rate=0.5)
        if ret is False:
            print("Error: Failed to parse video frames")
        return

    # List of saved frames
    frame_paths = sorted(Path(f"{data_dir}/frames").glob("*.jpg"))
    
    # Generate commentary text
    print("Generating commentary text")
    past_commentary = ""  # Initialize empty past commentary
    batch_size = 5
    if not Path(f"{data_dir}/commentary.json").exists() or FORCE_REGENERATE:
        commentary_text_list = None
        for i in range(0, len(frame_paths), batch_size):
            batch = frame_paths[i:i + batch_size]
            image_batch_data = [commentary_gen.encode_image(image) for image in batch]
            commentary_text = commentary_gen.generate_commentary_text(image_batch_data, past_commentary)
            commentary_dict = commentary_text
            if commentary_text_list is None:
                if type(commentary_dict) == list:
                    commentary_text_list = commentary_dict
                else:
                    commentary_text_list = [commentary_dict]
            else:
                if type(commentary_dict) == list:
                    commentary_text_list.extend(commentary_dict)
                else:
                    commentary_text_list.append(commentary_dict)
            past_commentary = commentary_text
        # Save commentary text list to a JSON file
        with open(f"{data_dir}/commentary.json", "w") as f:
            json.dump(commentary_text_list, f, indent=4)
    
    # Load commentary text list from a JSON file
    with open(f"{data_dir}/commentary.json", "r") as f:
        commentary_text_list = json.load(f)
    
    # Generate audio from commentary
    print("Generating audio from commentary")
    previous_text = ""
    if not Path(f"{data_dir}/output_audio").exists() or len(glob.glob("{data_dir}/output_audio/*.mp3")) == 0 or FORCE_REGENERATE:
        Path(f"{data_dir}/output_audio").mkdir(parents=True, exist_ok=True)
        for i in range(len(commentary_text_list)):
            audio_save_path = f"{data_dir}/output_audio/commentary_{i:04d}.mp3"
            text = commentary_text_list[i]
            commentary_gen.generate_commentary_audio(text,
                                                     previous_text,
                                                     audio_save_path)
            previous_text = text
    
    # Combine video and audio
    print("Combining video and audio")
    commentary_gen.combine_video_and_audio(video_path, f"{data_dir}/output_audio", output_video_path)