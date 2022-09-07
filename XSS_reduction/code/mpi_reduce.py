import sys, warnings
#import json, pyFAI, glob, warnings, os, pathlib, sys
#import scipy.io
#import numpy as np
#from datetime import datetime as dt
#from lmfit import Model
#import jungfrau_utils as ju
#from sfdata import SFDataFiles, SFScanInfo
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)
from utils import *

binned = False
suffix = 'unchunked'

pgroup = 'p20263'
#pgroup = 'p20222'
Izero = 'SAROP11-PBPS122:INTENSITY'
JF = 'JF06T32V02'
TimeTool = 'SARES11-SPEC125-M1.edge_position'


run = int(sys.argv[1]) # get run number

meta_dir, ai, mask_data = initialize(pgroup, run, binned)

integrate(meta_dir, ai, mask_data, binned, JF, Izero, TimeTool, qbins=500, abins=7, qmin=1.3, qmax=3.5, req_shots=None, n_steps=None, run=run, suffix=suffix)

#save(files2save, run, suffix)

