import numpy as np

WIDTH = 1058
HEIGHT = 915


def make_scale():
    scale_base = {
        0: np.array([0xff, 0xff, 0xff]),
        1: np.array([0xe4, 0xe5, 0xff]),
        11: np.array([0x4d, 0x5d, 0xff]),
        21: np.array([0x00, 0x07, 0x70]),
        25: np.array([0x00, 0x07, 0x70]),
        26: np.array([0xfe, 0x16, 0x00]),
        31: np.array([0xfe, 0x16, 0x00]),
        41: np.array([0xc0, 0x1c, 0xc4]),
    }

    scale = np.empty((42, 3), dtype=int)
    for i in range(42):
        start_pos = max([j for j in scale_base.keys() if j <= i])
        start = scale_base[start_pos]
        stop_pos = min([j for j in scale_base.keys() if j >= i])
        stop = scale_base[stop_pos]

        delta = stop_pos - start_pos
        if delta == 0:
            scale[i] = start
            continue
        ti = i - start_pos
        dist = ti / delta
        color = np.array(np.sqrt((1 - dist) * start ** 2 + dist * stop ** 2), dtype=int)
        scale[i] = color

    return scale


SCALE = make_scale()
FULL_SCALE = np.array([[SCALE.T for x in range(WIDTH)] for y in range(HEIGHT)])
MULTIPLIER = 256 / len(SCALE)


def make_grayscale(rgba):
    """
    Input is an RGBA numpy array
    Output is a grayscale numpy array scaled to 0-255
    (divide it by MULTIPLIER to get centimeters)
    """
    # split RGBA to RGB and A
    alpha = rgba[:, :, 3]
    rgb = rgba[:, :, :3]

    gray = np.linalg.norm(FULL_SCALE - np.expand_dims(rgb, 3), axis=2).argmin(axis=2) * MULTIPLIER
    gray[alpha == 0] = 0

    return gray.astype(np.uint8)
