import cv2
import numpy as np
import os
def parse_video_frames(video_path, frame_rate=1):
    """
    Parse a video file and extract frames at 1 Hz rate.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        list: List of frames as numpy arrays
    """
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError("Error: Could not open video file")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate frame interval for 1 Hz sampling
    frame_interval = int(fps)
    frame_sample_interval = frame_interval//frame_rate  # sampled frames every 2 seconds
    
    frames = []
    frame_idx = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
            
        # Sample frame at 1 Hz rate
        if frame_idx % frame_sample_interval == 0:
            frames.append(frame)
            
        frame_idx += 1
    
    # Release the video capture object
    cap.release()
    
    # Save the frames to a directory
    frames_dir = "data/frames"
    os.makedirs(frames_dir, exist_ok=True)
    for i, frame in enumerate(frames):
        cv2.imwrite(os.path.join(frames_dir, f"frame_{i:04d}.jpg"), frame)
    
    return frames
    
if __name__ == "__main__":
    frames = parse_video_frames("data/sport_video_clip.mp4", frame_rate=0.5)
    # save the frames to a directory
    frames_dir = "data/frames"
    os.makedirs(frames_dir, exist_ok=True)
    for i, frame in enumerate(frames):
        cv2.imwrite(os.path.join(frames_dir, f"frame_{i:04d}.jpg"), frame)

