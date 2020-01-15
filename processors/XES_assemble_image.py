#!/usr/bin/env python3

fname_gain = "/sf/alvra/config/jungfrau/gainMaps/JF02T09V02/gains.h5"
fname_pede = "/sf/alvra/data/p17983/res/JF_pedestals/pedestal_20190703_1848.JF02T09V02.res.h5"


import argparse

import numpy as np

import jungfrau_utils as ju
from alvra_tools import Clock, save

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("input",  help="Raw input filename")
parser.add_argument("output", help="Assembled output filename")

parser.add_argument("-g", "--gain", help="Gain map filename",     default=fname_gain)
parser.add_argument("-p", "--pede", help="Pedestal map filename", default=fname_pede)

clargs = parser.parse_args()

ifname = clargs.input
ofname = clargs.output

fname_gain = clargs.gain
fname_pede = clargs.pede

clock = Clock()

print ("It took", clock.tick(), "seconds to set things up.")

print("Processing", ifname)

with ju.File(ifname, gain_file=fname_gain, pedestal_file=fname_pede) as juf:
    print("Detector name:", juf.detector_name)
    print("> Load jungfrau data")
    pulse_ids = juf["pulse_id"][:]
    images = juf[:]

print("> Crop")
images = images[..., 5000:]
images[np.logical_or(images < 4, images > 10)] = 0
image = images.mean(axis=0)

print("> Store to", ofname)
save(ofname, image=image)

print ("It took", clock.tick(), "seconds to process this file")
print ("Job done! It took", clock.tock(), "seconds in total")
