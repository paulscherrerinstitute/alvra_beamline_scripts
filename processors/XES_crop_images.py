#!/usr/bin/env python3

import functools
print = functools.partial(print, flush=True)


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



import h5py
import numpy as np

import jungfrau_utils as ju

from alvra_tools import load_gain_data, load_pede_data
from alvra_tools import load_JF_data, apply_module_map
from alvra_tools import save
from alvra_tools import Clock
from alvra_tools import crop_roi
from alvra_tools.load_data import _get_detector_name, _apply_to_all_images, _get_module_map


clock = Clock()

print("Set up gain, pedestal and pixel mask")

print("> Load")
print("gain file:", fname_gain)
print("pede file:", fname_pede)

G        = load_gain_data(fname_gain)
P, mask  = load_pede_data(fname_pede)

print("Dimensions of G: ", G.shape)
print("Dimensions of P: ", P.shape)
print("Dimensions of mask: ", mask.shape)

print ("It took", clock.tick(), "seconds to set things up.")


print("Processing", ifname)

with h5py.File(ifname, "r") as f:
    detector_name = _get_detector_name(f)
    module_maps = _get_module_map(f)

print("Detector name:", detector_name)

print("> Load data")
images, pulse_ids = load_JF_data(ifname, nshots=None)

print("> Apply module map, gain, pedestal and pixel mask")
if module_maps is not None:
    print ("Will apply module map:", module_maps[0])
    images_full = []
    for image, module_map in zip(images, module_maps):
        image, mask_mod = apply_module_map(image, module_map, mask)
        image = ju.apply_gain_pede(image, G, P, mask_mod, highgain=False)
        images_full.append(image)
    images = images_full
else:
    print ("All modules are active")
    images = _apply_to_all_images(ju.apply_gain_pede, images, G, P, mask, highgain=False)

print("> Apply geometry")
images = _apply_to_all_images(ju.apply_geometry, images, detector_name)

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



