import cv2
from capture_camera import Camera
from pathlib import Path
from pypylon import pylon
import time


def build_camera(autoexposure,contrast_mode,contrast,exposure,gain,width,height,fps):
    cam = (
        Camera()
        .open()
        .set_auto_exposure(autoexposure)
        .set_contrast_mode(contrast_mode)
        .set_contrast(contrast)
        .set_exposure_time(exposure)
        .set_gain(gain)
        .set_image_size(width, height)
        .set_frame_rate(fps)
    )
    return cam

def set_up_writer(cam:Camera, output_path):

    print(f"ACTUAL CAMERA FRAMERATE {cam.get_frame_rate()}")
    print(f"INTERNAL TEMPERATURE {cam.get_temperature()}")
    width = cam.params.get('width')
    height = cam.params.get('height')

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    print(output_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, cam.get_frame_rate(), (width, height), True)
    if not writer.isOpened():
        raise RuntimeError(f"VideoWriter could not be opened: {output_path}")

    return writer

def record_video(cam:Camera, segment_duration, writer):

    cam.cam.StartGrabbing(pylon.GrabStrategy_OneByOne)
    t_0 = time.time()
    try:
        while time.time() - t_0 < segment_duration:
            grabResult = cam.cam.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
            if grabResult.GrabSucceeded():
                frame = grabResult.Array
                if frame.ndim == 2:
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                writer.write(frame)
            grabResult.Release()
            grabResult.Release()

        if cam.cam.IsGrabbing():
            cam.cam.StopGrabbing()
        writer.release()
        cam.close()

    except KeyboardInterrupt:
        video_length = time.time() - t_0
        print(f"Stopped by Interrupt - Video Length: {video_length} s")
        print(f"INTERNAL TEMPERATURE {cam.get_temperature()}")

    """
    finally:
        if cam.cam.IsGrabbing():
            cam.cam.StopGrabbing()
        writer.release()
        cam.close()
        return output_path
    """