import requests
from datetime import datetime, timedelta
from PIL import Image
import numpy as np
from io import BytesIO


PREDICTION_HORIZON = 34  # we can download 34 images in the future (thus 34*5 min)
NFRAMES = 4  # number of frames to interpolate


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


def make_grayscale(bytes):
    fp = BytesIO(bytes)
    rgb = np.array(Image.open(fp).convert("RGBA"))
    gray = np.empty(rgb.shape[:2], dtype=np.uint8)

    for y in range(gray.shape[0]):
        for x in range(gray.shape[1]):
            pix = rgb[y][x]
            if pix[3] == 0:  # if the pixel is transparent, rain is 0
                gray[y][x] = 0
            else:
                gray[y][x] = np.linalg.norm(SCALE - pix[:3], axis=1).argmin() * 5

    return Image.fromarray(gray)


def downlaod_picture(instant=None):
    if instant is None:
        instant = get_possible_instants()[0]
    timestr = instant.strftime("%Y%m%d%H%M")
    r = requests.get("http://api.buienradar.nl/image/1.0/webmercatorradarnl/png/?t=%s" % timestr)
    return r.content


def get_possible_instants():
    now = datetime.utcnow()
    delta = timedelta(minutes=(- now.minute % 5))
    frame_time = now + delta

    return [frame_time + (i * timedelta(minutes=5)) for i in range(PREDICTION_HORIZON)]


if __name__ == '__main__':
    for i, instant in enumerate(get_possible_instants()):
        print(".")
        original = downlaod_picture(instant)
        grayscale = make_grayscale(original)

        grayscale.save("gray/%05i.tiff" % i)

    # os.system("ffmpeg -f image2 -r 2 -i gray/%05d.tiff mov/gray.mp4 -y 2> /dev/null")
