import cv2
import numpy as np
import pyaudio
import struct
import wave

# Audio settings
CHUNK = 1024  # Number of samples per frame
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels
RATE = 44100  # Sample rate (Hz)

# Initialize audio input
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Start video capture
cap = cv2.VideoCapture(0)

# Get the video capture frame width and height
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object to save the video (initially not recording)
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec
out = None  # Initialize as None, meaning no recording at first
is_recording = False  # Flag to toggle recording

# Initialize audio recording variables
audio_frames = []  # List to store audio frames
is_audio_recording = True  # Flag for audio recording

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert to grayscale for contour detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 100)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Read audio data
    data = stream.read(CHUNK, exception_on_overflow=False)
    audio_data = np.array(struct.unpack(str(CHUNK) + 'h', data))
    volume = np.abs(audio_data).mean() / 1000  # Normalize volume
    
    # Map volume to a contour thickness range (e.g., 1 to 10)
    min_thickness = 1
    max_thickness = 10
    thickness = int(min_thickness + ((volume / 4) * (max_thickness - min_thickness)))
    
    for cnt in contours:
        if cv2.contourArea(cnt) > 1000:  # Filter small contours
            # Random color for each contour
            r = np.random.randint(0, 256)
            g = np.random.randint(0, 100)
            b = np.random.randint(0, 256)
            cv2.drawContours(frame, [cnt], -1, (255, g, b), thickness)
    
    # Draw volume bar (same as your original code)
    bar_height = int(volume * 150)
    cv2.rectangle(frame, (50, 800 - bar_height), (100, 800), (0, 0, 255), -1)
    
    # Add text to the top-right corner
    text = "Recording" if is_recording else "Not Recording"
    cv2.putText(frame, text, (frame_width - 500, 50), cv2.FONT_HERSHEY_PLAIN  , 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "harper_guitar_visualizer", (frame_width - 500, 150), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Display the frame
    cv2.imshow("Guitar Detection & Audio Visualization", frame)
    
    # Toggle recording based on `is_recording`
    if is_recording:
        if out is None:
            # Create VideoWriter object when starting to record
            out = cv2.VideoWriter('output_video.avi', fourcc, 20.0, (frame_width, frame_height))
        out.write(frame)
        if is_audio_recording:
            # Save audio frames
            audio_frames.append(data)
    
    # Check for key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('r'):  # Press 'r' to toggle recording
        is_recording = not is_recording  # Toggle the recording state
        print(f"Recording: {is_recording}")
        if not is_recording and out is not None:
            out.release()  # Release the VideoWriter when stopping
            out = None  # Set it back to None
            if is_audio_recording:
                # Save audio to file when stopped
                with wave.open('output_audio.wav', 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(audio_frames))
                print("Audio saved to output_audio.wav")
                audio_frames.clear()  # Clear the stored audio frames
                is_audio_recording = False
    
    if key == ord('q'):  # Press 'q' to quit
        break

# Cleanup
cap.release()
if out is not None:
    out.release()  # Ensure VideoWriter is released if it was recording
cv2.destroyAllWindows()
stream.stop_stream()
stream.close()
p.terminate()