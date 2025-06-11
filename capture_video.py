import cv2
from capture_camera import Camera
from pathlib import Path
from pypylon import pylon
import time

def record_video(cam:Camera, output_path: str) -> str:

    print(f"ACTUAL CAMERA FRAMERATE {cam.get_frame_rate()}")
    print(f"INTERNAL TEMPERATURE {cam.get_temperature()}")
    width = cam.params.get('width')
    height = cam.params.get('height')

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    if not output_path.lower().endswith('.mp4'):
        output_path = f"{Path(output_path).stem}.mp4"
    writer = cv2.VideoWriter(output_path, fourcc, cam.get_frame_rate(), (width, height), True)
    if not writer.isOpened():
        raise RuntimeError(f"VideoWriter could not be opened: {output_path}")

    cam.cam.StartGrabbing(pylon.GrabStrategy_OneByOne)
    t_0 = time.time()
    try:
        while True:
            grabResult = cam.cam.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
            if grabResult.GrabSucceeded():
                frame = grabResult.Array
                if frame.ndim == 2:
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                writer.write(frame)
            grabResult.Release()
            grabResult.Release()
    except KeyboardInterrupt:
        video_length = time.time() - t_0
        print(f"Stopped by Interrupt - Video Length: {video_length} s")
        print(f"INTERNAL TEMPERATURE {cam.get_temperature()}")

    finally:
        if cam.cam.IsGrabbing():
            cam.cam.StopGrabbing()
        writer.release()
        cam.close()
        return output_path