from pypylon import pylon


class Camera:
    def __init__(self):
        tl_factory = pylon.TlFactory.GetInstance()
        self.cam = pylon.InstantCamera()
        self.cam.Attach(tl_factory.CreateFirstDevice())
        self.params = {}

    def open(self):
        if not self.cam.IsOpen():
            self.cam.Open()
        return self

    def close(self):
        if self.cam.IsOpen():
            self.cam.Close()
        return self

    # Configuration

    def set_auto_exposure(self, mode: str):
        self.cam.ExposureAuto.SetValue(mode)
        self.params['auto_exposure'] = mode
        return self

    def set_exposure_time(self, micro_sec: int):
        auto_mode = self.params.get('auto_exposure', 'Off')
        if auto_mode == 'Off':
            self.cam.ExposureAuto.SetValue('Off')
            self.cam.ExposureTime.SetValue(micro_sec)
            self.params['exposure_time'] = micro_sec
        return self

    def set_gain(self, gain: float):
        self.cam.Gain.SetValue(gain)
        self.params["gain"] = gain
        return self

    def set_image_size(self, width: int, height: int):
        self.cam.Width.SetValue(width)
        self.cam.Height.SetValue(height)
        self.params['width'], self.params['height'] = width, height
        return self

    def set_frame_rate(self, fps: float):
        self.cam.AcquisitionFrameRateEnable.SetValue(True)
        self.cam.AcquisitionFrameRate.SetValue(fps)
        self.params['fps'] = fps
        return self

    def set_contrast_mode(self, mode: str):
        self.cam.BslContrastMode.SetValue(mode)
        self.params['contrast_mode'] = mode
        return self

    def set_contrast(self, value: int):
        self.cam.BslContrast.SetValue(value)
        self.params['contrast'] = value
        return self


    def get_frame_rate(self):
        return self.cam.ResultingFrameRate.GetValue()

    def get_temperature(self):
        return self.cam.BslTemperatureMax.Value

    #Grabbing

    def grab_frame(self,timeout_ms = 1000):
        return self.cam.GrabOne(timeout_ms).Array

    def get_config(self):
        return dict(self.params)