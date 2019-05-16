import numpy as np
from scipy.special import erf


def _bin(a, binning):
    if a.size % binning != 0:
        rounded = a.size // binning * binning
        a = a[0:rounded]
    return a.reshape((-1, binning))

def bin_sum(a, binning):
    return _bin(a, binning).sum(axis=1)

def bin_mean(a, binning):
    return _bin(a, binning).mean(axis=1)


def convert_to_photon_num_range(image, photon_range):
    """
    Convert energy to a number of photons counting values falling within a particular range.
    This will always return integer photon counts.
    """
    offset = photon_range[0]
    mean = np.mean(photon_range)
    return np.ceil(np.divide(image - offset, mean))

def convert_to_photon_num_mean(image, photon_range):
    """
    Convert energy to a number of photons using the central energy of a single photon.
    This can return fractional number of photons.
    """
    return image / np.mean(photon_range)


def crop_roi(arr, roi):
    if roi is None:
        return arr
#    return arr[..., roi[0][0]:roi[0][1], roi[1][0]:roi[1][1]]
    r0 = slice(*roi[0])
    r1 = slice(*roi[1])
    return arr[..., r0, r1]


def errfunc(x, a, b, c, d):
    return a + b*erf((c-x)*2*np.sqrt(np.log(2))/(np.abs(d)))



