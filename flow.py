import numpy as np
from PIL import Image
import time
import pyflow


im1 = np.array(Image.open('gray/00000.tiff'))
im2 = np.array(Image.open('gray/00001.tiff'))
im1 = im1.astype(float) / 255.
im2 = im2.astype(float) / 255.

im1 = np.reshape(im1, list(im1.shape) + [1])
im2 = np.reshape(im2, list(im2.shape) + [1])


# Flow Options:
alpha = 0.012
ratio = 0.75
minWidth = 20
nOuterFPIterations = 3
nInnerFPIterations = 1
nSORIterations = 20
colType = 1  # 0 or default:RGB, 1:GRAY (but pass gray image with shape (h,w,1))

# s = time.time()
# u, v, im2W = pyflow.coarse2fine_flow(
#     im1, im2, alpha, ratio, minWidth, nOuterFPIterations, nInnerFPIterations,
#     nSORIterations, colType)
# e = time.time()
# print('Time Taken: %.2f seconds for image of size (%d, %d, %d)' % (
#     e - s, im1.shape[0], im1.shape[1], im1.shape[2]))
# flow = np.concatenate((u[..., None], v[..., None]), axis=2)

# import matplotlib.pyplot as plt

# plt.figure(figsize=(50, 50))
# plt.gca().invert_yaxis()
# f = flow[::20, ::20]
# plt.quiver(f[..., 0], f[..., 1])#, angles='xy')
# plt.savefig("a.png")


def trans(s, t):
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
            S[:, 1] * A.shape[1] + S[:, 0]
        ]
    ).reshape(A.shape)


PREDICTION_HORIZON = 34  # we can download 34 images in the future (thus 34*5 min)
NFRAMES = 4  # number of frames to interpolate

destination = np.array(Image.open("gray/%05i.tiff" % 0))

absolute_coorindates = np.empty(destination.shape + (2,), int)
for y in range(absolute_coorindates.shape[0]):
    for x in range(absolute_coorindates.shape[1]):
        absolute_coorindates[y][x][0] = x
        absolute_coorindates[y][x][1] = y

j = 0

for i in range(10):
    source = destination
    destination = np.array(Image.open("gray/%05i.tiff" % (i + 1)))

    im1 = source.astype(float) / 255.
    im2 = destination.astype(float) / 255.
    im1 = np.reshape(im1, list(im1.shape) + [1])
    im2 = np.reshape(im2, list(im2.shape) + [1])

    u, v, im2W = pyflow.coarse2fine_flow(
        im1, im2, alpha, ratio, minWidth, nOuterFPIterations, nInnerFPIterations,
        nSORIterations, colType)
    relative_flow = np.concatenate((u[..., None], v[..., None]), axis=2)

    flow = absolute_coorindates + relative_flow

    Image.fromarray(source).save("interpolate/%05i.tiff" % j)
    j += 1

    for ti in np.linspace(0, 1, NFRAMES + 1, endpoint=False)[1:]:
        back = - ti * flow
        forward = (1 - ti) * flow
        bf = trans(source, back)
        af = trans(destination, forward)
        frame = (1 - ti) * bf + ti * af

        Image.fromarray(frame.astype(np.uint8)).save("interpolate/%05i.tiff" % j)
        j += 1

Image.fromarray(destination).save("interpolate/%05i.tiff" % j)
