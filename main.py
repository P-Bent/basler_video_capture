import sys
from capture_video import record_video
from capture_camera import Camera
from pathlib import Path
import yaml

def load_config(config_path: str = "config.yaml") -> dict:
    if not Path(config_path).is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    try:
        cfg = load_config()
        video_cfg = cfg.get('video', {})


        output_path = video_cfg.get('out', 'data/video/output.mp4')
        fps = video_cfg.get('fps', 30)
        width = video_cfg.get('width', 1280)
        height = video_cfg.get('height', 720)
        exposure = video_cfg.get('exposure', 20000)
        gain = video_cfg.get('gain', 0.0)
        autoexposure = video_cfg.get('auto_exposure', 'Continuous')
        contrast_mode = video_cfg.get('contrast_mode', 'Linear')
        contrast = video_cfg.get('contrast',1.1)

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


        output = record_video(cam,output_path)
        print(f"Video saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)