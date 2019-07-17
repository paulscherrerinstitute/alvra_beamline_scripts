#!/usr/bin/env python3

fname_gain = "/sf/alvra/config/jungfrau/gainMaps/JF02T09V02/gains.h5"
fname_pede = "/sf/alvra/data/p17983/res/JF_pedestals/pedestal_20190703_1848.JF02T09V02.res.h5"

#TODO store/load from files? see below
roi1 = [7650, 7900, 150, 400]
roi2 = [4000, 7000, 150, 400]
roi3 = [-250,   -1,   0, 250]


import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("input",  help="Raw input filename")
parser.add_argument("output", help="Cropped output filename")

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



import jungfrau_utils as ju

from alvra_tools import load_gain_data, load_pede_data
from alvra_tools import load_crop_JF_data_v02, crop_roi
from alvra_tools import save_JF_data_cropped
from alvra_tools import Clock


clock = Clock()

print("Set up gain, pedestal and pixel mask")

print("> Load")
G         = load_gain_data(fname_gain)
P, mask   = load_pede_data(fname_pede)

print("Dimensions of G: ", G.shape)
print("Dimensions of P: ", P.shape)
print("Dimensions of mask: ", mask.shape)

print("> Apply ROIs")
print("ROI1:", roi1)
print("ROI2:", roi2)
print("ROI3:", roi3)

P_roi1    = crop_roi(P, roi1)
G_roi1    = crop_roi(G, roi1)
mask_roi1 = crop_roi(mask, roi1)

P_roi2    = crop_roi(P, roi2)
G_roi2    = crop_roi(G, roi2)
mask_roi2 = crop_roi(mask, roi2)

P_roi3    = crop_roi(P, roi3)
G_roi3    = crop_roi(G, roi3)
mask_roi3 = crop_roi(mask, roi3)

print("Dimensions of ROI1 G: ", G_roi1.shape)
print("Dimensions of ROI1 P: ", P_roi1.shape)
print("Dimensions of ROI1 mask: ", mask_roi1.shape)

print("Dimensions of ROI2 G: ", G_roi2.shape)
print("Dimensions of ROI2 P: ", P_roi2.shape)
print("Dimensions of ROI2 mask: ", mask_roi2.shape)

print("Dimensions of ROI3 G: ", G_roi3.shape)
print("Dimensions of ROI3 P: ", P_roi3.shape)
print("Dimensions of ROI3 mask: ", mask_roi3.shape)

print ("It took", clock.tick(), "seconds to set things up.")


print("Processing", ifname)

print("> Load and crop data")
images_roi1, images_roi2, images_roi3, pulse_ids = load_crop_JF_data_v02(ifname, roi1, roi2, roi3, max_num_frames=100)

if 0 in images_roi1.shape:
    print("ROI1 seems to have removed too much. cropped images shape:", images_roi1.shape)

if 0 in images_roi2.shape:
    print("ROI2 seems to have removed too much. cropped images shape:", images_roi2.shape)

if 0 in images_roi3.shape:
    print("ROI3 seems to have removed too much. cropped images shape:", images_roi3.shape)

print("> Apply gain, pedestal and pixel mask")
images_roi1 = ju.apply_gain_pede(images_roi1, G_roi1, P_roi1, mask_roi1, highgain=False)
images_roi2 = ju.apply_gain_pede(images_roi2, G_roi2, P_roi2, mask_roi2, highgain=False)
images_roi3 = ju.apply_gain_pede(images_roi3, G_roi3, P_roi3, mask_roi3, highgain=False)

print("> Store to", ofname)
save_JF_data_cropped(ofname, images_roi1, images_roi2, images_roi3, pulse_ids, roi1, roi2, roi3)

print ("It took", clock.tick(), "seconds to process this file")
print ("Job done! It took", clock.tock(), "seconds in total")



