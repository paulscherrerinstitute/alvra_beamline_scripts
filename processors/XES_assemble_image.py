#!/usr/bin/env python3

fname_gain = "/sf/alvra/config/jungfrau/gainMaps/JF02T09V02/gains.h5"
fname_pede = "/sf/alvra/data/p17983/res/JF_pedestals/pedestal_20190703_1848.JF02T09V02.res.h5"



import argparse

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



import h5py
import numpy as np

import jungfrau_utils as ju

from alvra_tools import load_gain_data, load_pede_data
from alvra_tools import load_JF_data
from alvra_tools import save
from alvra_tools import Clock
from alvra_tools.load_data import _get_detector_name, _apply_to_all_images


clock = Clock()

print("Set up gain, pedestal and pixel mask")

print("> Load")
G         = load_gain_data(fname_gain)
P, mask   = load_pede_data(fname_pede)

print("Dimensions of G: ", G.shape)
print("Dimensions of P: ", P.shape)
print("Dimensions of mask: ", mask.shape)

print ("It took", clock.tick(), "seconds to set things up.")


print("Processing", ifname)

with h5py.File(ifname, "r") as f:
    detector_name = _get_detector_name(f)

print("Detector name:", detector_name)

print("> Load data")
images, pulse_ids = load_JF_data(ifname, nshots=None)

print("> Apply gain, pedestal and pixel mask")
images = _apply_to_all_images(ju.apply_gain_pede, images, G, P, mask, highgain=False)

print("> Apply geometry")
images = _apply_to_all_images(ju.apply_geometry, images, detector_name)

print("> Crop")
images = images[..., 5000:]
images[np.logical_or(images < 4, images > 10)] = 0
image = images.mean(axis=0)

print("> Store to", ofname)
save(ofname, image=image)

print ("It took", clock.tick(), "seconds to process this file")
print ("Job done! It took", clock.tock(), "seconds in total")



