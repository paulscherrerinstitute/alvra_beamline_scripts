#!/usr/bin/env python3

fname_gain = "/sf/alvra/config/jungfrau/gainMaps/JF02T09V02/gains.h5"
#fname_pede = "/sf/alvra/data/p17983/res/JF_pedestals/pedestal_20190703_1848.JF02T09V02.res.h5"
#fname_pede = "/sf/alvra/data/p17983/res/JF_pedestals/pedestal_20190703_0745.JF02T09V02.res.h5"
fname_pede = "/sf/alvra/data/p17983/res/JF_pedestals/pedestal_20190723_1255.JF02T09V02.res.h5"

#TODO store/load from files? see below
roi1 = [3200, 4000, 0, 512]
roi2 = [4900, 5200, 0, 512]
roi3 = [7100, 7300, 0, 512]
roi4 = [6900, 7100, 0, 512]


import argparse
import functools

import numpy as np

import jungfrau_utils as ju
from alvra_tools import Clock, crop_roi, save

print = functools.partial(print, flush=True)


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("input",  help="Raw input filename")
parser.add_argument("output", help="Assembled output filename")

parser.add_argument("-g", "--gain", help="Gain map filename",     default=fname_gain)
parser.add_argument("-p", "--pede", help="Pedestal map filename", default=fname_pede)

#metavar = "xmin xmax ymin ymax"
#metavar = tuple(metavar.split())
#parser.add_argument("-r1", "--roi1", help="Region Of Interest 1", nargs=4, type=int, default=roi1, metavar=metavar)
#parser.add_argument("-r2", "--roi2", help="Region Of Interest 2", nargs=4, type=int, default=roi2, metavar=metavar)

clargs = parser.parse_args()

ifname = clargs.input
ofname = clargs.output

fname_gain = clargs.gain
fname_pede = clargs.pede

#roi1 = clargs.roi1
#roi2 = clargs.roi2

#TODO
#import numpy as np

#output_folder = "/".join(ofname.split("/")[:-2])
#roi1_file = output_folder + "/roi1.txt"
#roi2_file = output_folder + "/roi2.txt"
#roi1 = np.genfromtxt(roi1_file).astype(int)
#roi2 = np.genfromtxt(roi2_file).astype(int)


clock = Clock()

print ("It took", clock.tick(), "seconds to set things up.")

print("Processing", ifname)

with ju.File(ifname, gain_file=fname_gain, pedestal_file=fname_pede) as juf:
    print("Detector name:", juf.detector_name)
    print("> Load jungfrau data")
    pulse_ids = juf["pulse_id"][:]
    images = juf[:]

print("> Crop")
images_roi1 = crop_roi(images, roi1)
images_roi2 = crop_roi(images, roi2)
images_roi3 = crop_roi(images, roi3)
images_roi4 = crop_roi(images, roi4)

if 0 in images_roi1.shape:
    print("ROI1 seems to have removed too much. cropped images shape:", images_roi1.shape)

if 0 in images_roi2.shape:
    print("ROI2 seems to have removed too much. cropped images shape:", images_roi2.shape)

if 0 in images_roi3.shape:
    print("ROI3 seems to have removed too much. cropped images shape:", images_roi3.shape)

if 0 in images_roi4.shape:
    print("ROI4 seems to have removed too much. cropped images shape:", images_roi3.shape)

print("> Store to", ofname)
save(ofname, pulse_ids=pulse_ids,
    images_roi1=images_roi1, images_roi2=images_roi2, images_roi3=images_roi3, images_roi4=images_roi4,
    coords_roi1=roi1,        coords_roi2=roi2,        coords_roi3=roi3,        coords_roi4=roi4
)


print ("It took", clock.tick(), "seconds to process this file")
print ("Job done! It took", clock.tock(), "seconds in total")
