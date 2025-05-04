from flask import Flask, render_template, request, send_file
import os
from pathlib import Path
from main import main
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'video' not in request.files:
            return 'No video file uploaded', 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return 'No selected file', 400

        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Save uploaded video
        upload_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_input_path = os.path.join('videos', f'{upload_time}_uploaded_video.mp4')
        video_file.save(video_input_path)
        
        output_video_path = f"{upload_time}_output_video.mp4"
        # Run the main processing
        main(video_input_path, output_video_path, upload_time)
        
        # Return the processed video
        return render_template('result.html', video_path=output_video_path)
    
    return render_template('index.html')

@app.route('/video/<path:filename>')
def serve_video(filename):
    return send_file(filename)

if __name__ == '__main__':
    app.run(debug=True)