
A real-time video and audio visualizer built with OpenCV and PyAudio. This program captures your webcam feed and microphone input simultaneously, detects contours in the video, and maps audio volume to contour thickness. Press `r` to start/stop recording the visualized video and audio. Press `q` to quit.

## Features

- Live webcam feed with edge and contour detection  
- Real-time microphone input and volume detection  
- Visual representation of audio volume (volume bar)  
- Contour thickness varies with audio volume  
- Record synchronized video and audio by pressing `r`  
- Save output as `output_video.avi` and `output_audio.wav`

## Requirements

- Python 3.x  
- OpenCV (`cv2`)  
- PyAudio  
- NumPy

### Install Dependencies

```bash
pip install opencv-python numpy pyaudio
