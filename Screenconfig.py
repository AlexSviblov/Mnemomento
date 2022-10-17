import ctypes


def monitor_info() -> tuple[tuple[int, int], float]:
    screenSize = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)

    scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    return screenSize, scaleFactor


