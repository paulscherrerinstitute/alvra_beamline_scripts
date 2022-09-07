import pathlib,pyFAI,glob,warnings,os,json
import numpy as np
from datetime import datetime as dt
import scipy.io
from sfdata import SFDataFile, SFDataFiles, SFScanInfo
#from alvra_tools.channels import *

warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
except:
    rank = 0
    size = 1
    comm = None
    
###########################################################################

def initialize(pgroup, run, binned):
    meta_dir = set_dirs(pgroup, run)
    ai = init_pyFAI(binned)
    mask = get_mask(binned)
    
    return meta_dir, ai, mask

###########################################################################

def correct_scan(scan, JF, binned, work=False):
    for i, files in enumerate(scan.files):
        new_files = []
        for sc_file in files:
           # print (sc_file)
            if "JF02" in sc_file:
                continue
            if "JF06" in sc_file:
                if work:
                    sc_file = sc_file.replace('p20222/raw/','p20222/work/reduced_data/no_rounding/')
                else:
                    check_raw_folder = scan.fname.replace('meta/scan.json', 'raw_data/')
                    folder_raw_size = len(os.listdir(check_raw_folder))
                    #print ('size folder={}'.format(folder_raw_size))
                    if binned:
                        if folder_raw_size>0:
                            sc_file = sc_file
                    else:
                        if folder_raw_size>0:
                            sc_file = sc_file.replace('/data/acq','/raw_data/acq')
            #print (sc_file)
            new_files.append(sc_file)
        scan.files[i] = new_files
    return scan

###########################################################################

def correct_path(scan, step, JF, binned, work=False):
    if work:
        #print ('----- Use reduced data WORK -----')
        for fn in step.fnames:
            if JF in fn:
                break
        raw_fn = fn.replace('p20222/raw/','p20222/work/reduced_data/no_rounding/')
        raw_f = SFDataFile(raw_fn)
        step.update(raw_f)
        step.fnames.append(raw_fn)
        step.files.append(raw_f)     
    else:
        check_raw_folder = scan.fname.replace('meta/scan.json', 'raw_data/')
        folder_raw_size = len(os.listdir(check_raw_folder))
        if binned:
            if folder_raw_size>0:
            #    print ('----- Use reduced data -----')
                step=step
            #else:
            #    print ('----- No reduced data found!! ------')
        else:
            if folder_raw_size>0:
                print ('----- Use raw data -----')
                for fn in step.fnames:
                    if JF in fn:
                        break
                raw_fn = fn.replace('p20222/raw/','p20222/work/reduced_data/no_rounding/')
                raw_f = SFDataFile(raw_fn)
                step.update(raw_f)
                step.fnames.append(raw_fn)
                step.files.append(raw_f)
            #else:
            #    print ('----- Use reduced data -----')
    return step

###########################################################################

def set_dirs(pgroup, run):
    here = str(pathlib.Path(__file__).parent.absolute())
    data_dir = '/sf/alvra/data/{}/raw/'.format(pgroup)
    #data_dir = '/sf/alvra/data/{}/work/reduced_data/no_rounding/'.format(pgroup)
    for folder in os.listdir(data_dir): 
            if f'run{run:04d}' in folder:
                run_dir = data_dir + folder + '/'
    meta_dir = run_dir + 'meta/'
    
    return meta_dir
    
###########################################################################

def set_channels(JF, Izero, TT):
    channel_list = ["SAR-CVME-TIFALL5:EvtSet", JF, Izero, TT]
    return channel_list
    
###########################################################################

def init_pyFAI(binned):
    here = str(pathlib.Path(__file__).parent.absolute())
    
    if binned:
        try:
            ai = pyFAI.load(here + '/../References/LaB6_z0_11p07keV_binned.poni')  # needs poni profile
        except FileNotFoundError:
            ai = None
            print ('----- poni file not found! -----')
        #jf_file_list = np.sort(glob.glob(run_dir + 'data/*.JF06T32*.h5'))
    else:
        try:
            ai = pyFAI.load(here + '/../References/LaB6_z0_11p07keV.poni')
        except FileNotFoundError:
            ai = None
            print ('----- poni file not found! -----')
    
    return ai
###########################################################################            

def get_mask(binned):
    here = str(pathlib.Path(__file__).parent.absolute())
    if binned:
        try:
            mask1 = np.load(here + '/../Masks/mask_borders_and_defects_binned.npy')
            mask2 = np.load(here + '/../Masks/mask_dead_pix_binned.npy')
        except FileNotFoundError:
            print ('----- mask file not found! -----')
            mask1 = None
            mask2 = None
    else:
        try:
            mask1 = np.load(here + '/../Masks/mask_run0034_acq0001_bs.npy')
            mask2 = np.load(here + '/../Masks/mask_borders_and_defects.npy')
        except FileNotFoundError:
            print ('----- mask file not found! -----')
            mask1 = None
            mask2 = None        
    mask = np.logical_or(mask1, mask2)
    return mask

###########################################################################
        
def integrate(meta_dir, ai, mask_data, binned, JF, Izero, TT, qbins, abins, qmin, qmax, req_shots, n_steps, run, suffix):
    
    if rank == 0:
        elapsed = np.NaN
        tic = dt.now()
        
    json_file = meta_dir + 'scan.json'
    scan = SFScanInfo(json_file)
    scanvar = scan.readbacks
    nfiles = len(scan.files[:n_steps])
    
    channels = set_channels(JF, Izero, TT)
    
    S0 = np.empty((qbins, nfiles))
    S2 = np.empty((qbins, nfiles))

    on_avg = np.empty((qbins, nfiles))
    off_avg = np.empty((qbins, nfiles))
    S_azi = np.empty((qbins, nfiles))
    
    maxshots = get_max_shots(json_file)
    all_s1d = np.zeros((nfiles, maxshots + 1, qbins)) * np.NaN 
    
    idx_valid = []
    idx_on = []
    idx_off = []
    data_Izero = []
    data_TT = []

    #scan = correct_scan(scan, JF, binned, work=True)
    scan = correct_scan(scan, JF, binned, work=False)
    
    for ii, step in enumerate(scan[:n_steps]):
        
        #step = correct_path(scan, step, JF, binned, work=True)
        
        n_imgs = len(step[JF])
        #jf_data = step[JF][:n_shots]
        jf_filename = step.fnames[-1]
        
        if req_shots is None:
            n_shots = n_imgs
        else:
            n_shots = req_shots
        
        if rank == 0:
            print ('###########################################')
            print ('Step: {} --- File: {}'.format(ii+1,jf_filename))
            print ('###########################################')
            print ('Total images are {}, will integrate {} images'.format(n_imgs, n_shots))
        
        if size > 1:
            if rank == 0:
                s_1d = np.empty((size, n_shots // size + 1, qbins))
                mask = np.zeros((size, n_shots // size + 1), bool)
            else:
                s_1d = None
                mask = None
            s_1d = comm.scatter(s_1d, root=0)
            mask = comm.scatter(mask, root=0)
        else:
            s_1d = np.empty((n_shots, qbins))
        
        for i, img in enumerate(step[JF][rank:n_shots:size]):
        
            print(f'rank {rank:02d} integrating image {rank+i*size:04d}')
            qs, s_1d[i, :] = ai.integrate1d(img, qbins, mask=mask_data, method='cython', unit='q_A^-1',
                                                         correctSolidAngle=True, polarization_factor=1)
            if size > 1:
                mask[i] = True
        print(f'rank {rank:02d}: finished integration')
        
        if size > 1:
            s_1d = np.array(comm.gather(s_1d, root=0))
            mask = np.array(comm.gather(mask, root=0))

            if rank == 0:
                mask = mask.reshape(-1, order='F')
                s_1d = s_1d.reshape(-1, qbins, order='F')
                s_1d = s_1d[mask, :]
                all_s1d[ii, :n_shots, :] = s_1d
                
                S_azi[:, ii], on_avg[:,ii], off_avg[:,ii], data_Izero_step, data_TT_step, idx_valid_step, idx_on_step, idx_off_step = average_on_off(step, channels, JF, Izero, TT, s_1d, qs, qmin, qmax, n_shots)
                idx_valid.append(idx_valid_step)
                idx_on.append(idx_on_step)
                idx_off.append(idx_off_step) 
                data_Izero.append(data_Izero_step)
                data_TT.append(data_TT_step)
        else:
            s_1d = s_1d
            all_s1d[ii, :n_shots, :] = s_1d

            S_azi[:, ii], on_avg[:,ii], off_avg[:,ii],  data_Izero_step, data_TT_step, idx_valid_step, idx_on_step, idx_off_step = average_on_off(step, channels, JF, Izero, TT, s_1d, qs, qmin, qmax, n_shots)
            idx_valid.append(idx_valid_step)
            idx_on.append(idx_on_step)
            idx_off.append(idx_off_step)
            data_Izero.append(data_Izero_step)
            data_TT.append(data_TT_step)
            
    #print (np.shape(S_azi))
    scanvar = scanvar[:n_steps]
    
    if rank == 0:
        toc = dt.now()
        t = toc - tic
        print(f'#####################################################################################')
        print(f'#### Finished Reduction on {size} cores in {t.seconds // 3600}h{t.seconds // 60 % 60}m{t.seconds % 60}s')
        print(f'#####################################################################################')
        elapsed = f'{t.seconds // 3600}h{t.seconds // 60 % 60}m{t.seconds % 60}s'
        savedict = {
            'Sazi':S_azi,
            'on_avg':on_avg,
            'off_avg':off_avg,
            'all_s1d': all_s1d,
            'scanvar':scanvar,
            'q':qs,
            'idx_valid':idx_valid,
            'idx_on':idx_on,
            'idx_off':idx_off,
            'i0s': data_Izero, 
            'TTs': data_TT
        }
        save(savedict, run, suffix)

    return

###########################################################################

def average_on_off(step, channels, JF, Izero, TT, s_1d, qs, qmin, qmax, n_shots):
    
    subset = step[channels]
    #subset.print_stats(show_complete=True)
    subset.drop_missing()    # Get valid indices...
    valid_idx = subset[JF].valid[:n_shots]
    #print (len(s_1d), len(valid_idx))
    s_1d = s_1d[valid_idx]
    print (len(s_1d))
    
    Data_Izero =subset[Izero].data[:n_shots]
    Data_TimeTool =subset[TT].data[:n_shots]
    
    Event_code = subset['SAR-CVME-TIFALL5:EvtSet'][:n_shots]
            
    FEL_raw  = Event_code[:,13] #Event 13: changed from 12 on June 22
    Ppicker  = Event_code[:,200]
    Laser    = Event_code[:,18]
    Darkshot = Event_code[:,21]
        
    FEL = FEL_raw
            
    if Darkshot.mean()==0:
        index_on = np.logical_and.reduce((FEL, Laser))
        index_off  = np.logical_and.reduce((FEL, np.logical_not(Laser)))
    else:
        index_on = np.logical_and.reduce((FEL, Laser, np.logical_not(Darkshot)))
        index_off = np.logical_and.reduce((FEL, Laser, Darkshot))  
        
    #index_on_nshots = np.intersect1d(valid_idx, index_on)
    #index_off_nshots = np.intersect1d(valid_idx, index_off)
    #print (len(index_on_nshots), len(index_off_nshots))
        
    s_1d_on  = s_1d[index_on]#_nshots]
    s_1d_off = s_1d[index_off]#_nshots]
    
    pids_on  = subset[JF].pids[index_on]#_nshots]
    pids_off = subset[JF].pids[index_off]#_nshots]
    
    offs_1d = np.empty_like(s_1d_on)
    q_norm = (qs > qmin) & (qs < qmax)
    
    if np.size(np.array(pids_off)) == 0:
        offs_1d = s_1d_on
    else:
        for jj in range(len(s_1d_on)):
            ind = np.argmin(np.abs(pids_on[jj] - pids_off))
            offs_1d[jj,:] = s_1d_off[ind,:]
    
    print (len(s_1d_on), len(offs_1d))
        
    on_1d  = s_1d_on / np.nanmean(s_1d_on[:, q_norm], axis=1)[:, np.newaxis]
    off_1d = offs_1d / np.nanmean(offs_1d[:, q_norm], axis=1)[:, np.newaxis]
        
    on_avg_slice = np.nanmedian(on_1d, axis=0).T
    off_avg_slice = np.nanmedian(off_1d, axis=0).T
        
    Sazi_slice = np.nanmedian(on_1d - off_1d, axis=0)
    
    #print (np.shape(Sazi_slice))

    return Sazi_slice, on_avg_slice, off_avg_slice, Data_Izero, Data_TimeTool, valid_idx, index_on, index_off

###########################################################################

def save(savedict, run, suffix):
    here = str(pathlib.Path(__file__).parent.absolute())
    output_dir = here + '/../Output/'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = output_dir + f'run_{run:04d}_reduced_' + suffix
    
    scipy.io.savemat(output_file +'.mat', savedict)
    np.save(output_file +'.npy', savedict)
    
    print ('Saved file: {}'.format(output_file))

###########################################################################

def get_max_shots(json_file):
    with open(json_file) as f:
        data = json.load(f)
    shots = [delta[1]-delta[0] for delta in data['pulseIds']]
    return max(shots)

###########################################################################
