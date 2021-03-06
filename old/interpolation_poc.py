from __future__ import division
from __future__ import print_function
import requests
from datetime import datetime, timedelta
from PIL import Image
import numpy as np
from io import BytesIO
import cv2


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

    return [frame_time + i * timedelta(minutes=5) for i in range(PREDICTION_HORIZON)]




def trans(s,t):
    """reshape an array for faster computing"""
    A = s.astype(int)
    bornes = list(A.shape[::-1])
    bornes[0] -= 1
    bornes[1] -= 1

    T = t.astype(int)

    T = np.minimum(T, bornes)
    T = np.maximum(T, [0, 0])

    S = T.reshape(A.size, 2)
    return (
        A.reshape(A.size)[
            S[:,1] * A.shape[1]  + S[:,0]
        ]
    ).reshape(A.shape)


if __name__ == '__main__':
    for i, instant in enumerate(get_possible_instants()):
        original = downlaod_picture(instant)
        grayscale = make_grayscale(original)

        grayscale.save("gray/%05i.tiff" % i)


    destination = np.array(Image.open("gray/%05i.tiff" % 0))

    absolute_coorindates = np.empty(destination.shape + (2,), int)
    for y in range(absolute_coorindates.shape[0]):
        for x in range(absolute_coorindates.shape[1]):
            absolute_coorindates[y][x][0] = x
            absolute_coorindates[y][x][1] = y

    j = 0

    for i in range(3):
        source = destination
        destination = np.array(Image.open("gray/%05i.tiff" % (i+1)))
        relative_flow = cv2.calcOpticalFlowFarneback(source,destination, 0.0, 1, 3, 15, 3, 5, 1, 0)
        flow = absolute_coorindates + relative_flow

        Image.fromarray(source).save("interpolate/%05i.tiff" % j)
        j += 1

        for ti in np.linspace(0, 1, NFRAMES + 1, endpoint=False)[1:]:
            back = - ti * flow
            forward = (1-ti) * flow
            bf = trans(source,back)
            af = trans(destination, forward)
            frame = (1-ti) * bf + ti * af

            Image.fromarray(frame.astype(np.uint8)).save("interpolate/%05i.tiff" % j)
            j += 1

    Image.fromarray(destination).save("interpolate/%05i.tiff" % j)


    new_frames = []
    for t in range(PREDICTION_HORIZON-1):
        t0 = 0
        t1 = t0 + 1
        flow = flows[t]
        f0 = frames[t][...,1].astype(np.uint16)
        f1 = frames[t+1][...,1].astype(np.uint16)
        new_frames.append(f0)

        for ti in np.linspace(0, 1, NFRAMES + 1, endpoint=False)[1:]:

            back = np.array(coords) - ti * flow
            forward = np.array(coords) + (1-ti) * flow
            bf = trans(f0,back)
            af = trans(f1, forward)
            frame = (1-ti) * bf + ti * af
            new_frames.append(frame)

    new_frames.append(frames[-1][...,1])

    for i,frame in enumerate(new_frames):
        r = Image.fromarray(frame.astype(np.uint8))
        r.save("interpolate/%05i.png" % i)


# ! ffmpeg -f image2 -r 24 -i interpolate/%05d.png mov/int.webm -y 2> /dev/null

# ! ffmpeg -f image2 -r 2 -i gray/%05d.png mov/gray.webm -y 2> /dev/null
# ! ffmpeg -f image2 -r 24 -i interpolate/%05d.png mov/interpolated.webm -y 2> /dev/null

# ! ffmpeg -f image2 -r 2 -i gray/%05d.tiff mov/gray.mp4 -y 2> /dev/null
