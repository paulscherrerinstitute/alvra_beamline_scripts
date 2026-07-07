dimport numpy as np
import json
import os, math

from IPython.display import clear_output

from alvra_tools import clock
from alvra_tools.load_data import *
from alvra_tools.utils import *
from alvra_tools.XAS_functions import *


####################################

def Johann_scan(detector, scan, channels_list, thr_low, thr_high, I0_threshold, quantile, numsteps=None):
    clock_int = clock.Clock()
    
    s = scan[0]
    channels_ROI = Get_ROI_names(s, detector)
    channels_pp = [channel_Events] + channels_list + channels_ROI
    channels_all = channels_pp

    readbacks = scan.readbacks
    if numsteps==None:
        numsteps=len(scan)
    
    intensity_on       = []
    intensity_off      = []
    intensity_on_shot  = []
    intensity_off_shot = []
    Delays_fs_shot     = []

    for i, step in enumerate(scan[:numsteps]):
	    
        check_files_and_data(step)
        check = get_filesize_diff(step)  
        if check:
            clear_output(wait=True)
            filename = scan.files[i][0].split('/')[-1].split('.')[0]
            print ("Took {} seconds for the previous step".format(clock_int.tick()))
            print ('Processing: {}'.format(scan.fname.split('/')[-3]))
            print ('Step {} of {}: Processing {}'.format(i+1, numsteps, filename))

            resultsPP, results, _, _ = load_data_compact_pump_probe(channels_pp, channels_all, step)

            IzeroP = resultsPP[channel_Izero122].pump
            IzeroU = resultsPP[channel_Izero122].unpump
            #Delays_fs_shot.extend(resultsPP[channel_delay_beckhoff].pump)

            thresh = (IzeroP>I0_threshold) & (IzeroU>I0_threshold)
            IzeroP = IzeroP[thresh]
            IzeroU = IzeroU[thresh]
            

            intensity_roi_on = {}
            intensity_roi_off = {}
            intensity_roi_on_shot = {}
            intensity_roi_off_shot = {}
            
            tags = []
		
            for roi in channels_ROI:
                tag = roi
                
                data_on = resultsPP[roi].pump[thresh]
                data_off = resultsPP[roi].unpump[thresh]
		    
                thr_on  = threshold(data_on, thr_low, thr_high)

                inten_on = np.sum(thr_on, axis=1)
                inten_on = np.sum(inten_on, axis=1)
                inten_on = inten_on / IzeroP 
                #intensity_roi_on_shot[tag] = inten_on
                #inten_on = np.nanmean(inten_on)                
                
                thr_off  = threshold(data_off, thr_low, thr_high)
                
                inten_off = np.sum(thr_off, axis=1)
                inten_off = np.sum(inten_off, axis=1)
                inten_off = inten_off / IzeroU
                #intensity_roi_off_shot[tag] = inten_off
                #inten_off = np.nanmean(inten_off)

                filtervals = create_corr_condition(inten_on, inten_off, quantile)
                
                intensity_roi_on_shot[tag]  = inten_on[filtervals]
                intensity_roi_off_shot[tag] = inten_off[filtervals]
                inten_on  = np.nanmean(inten_on[filtervals])
                inten_off = np.nanmean(inten_off[filtervals]) 
                

                intensity_roi_on[tag]  = inten_on
                intensity_roi_off[tag] = inten_off
                tags.append(tag)
                
            Delays_fs_shot.extend((resultsPP[channel_delay_beckhoff].pump)[filtervals])

            intensity_on.append(intensity_roi_on)
            intensity_off.append(intensity_roi_off)
            intensity_on_shot.append(intensity_roi_on_shot)
            intensity_off_shot.append(intensity_roi_off_shot)
       
        if i==0:
            meta = resultsPP["meta"]
    
    return(intensity_on, intensity_off, intensity_on_shot, intensity_off_shot, Delays_fs_shot, tags, readbacks, meta)


def VonHamos_scan(detector, scan, channels_list, thr_low, thr_high, savedir, I0_threshold, badruns, numsteps=None):
    clock_int = clock.Clock()
    
    s = scan[0]
    channels_ROI = Get_ROI_names(s, detector)
    channels_pp = [channel_Events] + channels_list + channels_ROI
    channels_all = channels_pp

    readbacks = scan.readbacks
    if numsteps==None:
        numsteps=len(scan)
    
    spectra_on       = []
    spectra_off      = []
    spectra_shots_on  = []
    spectra_shots_off = []
    Delays_fs_shot     = []

    for i, step in enumerate(scan[:numsteps]):
        check_files_and_data(step)
        check = get_filesize_diff(step)  
        if i+1 in badruns: 
            check=False
        if check:
            clear_output(wait=True)
            filename = scan.files[i][0].split('/')[-1].split('.')[0]
            print ("Took {} seconds for the previous step".format(clock_int.tick()))
            print ('Processing: {}'.format(scan.fname.split('/')[-3]))
            print ('Step {} of {}: Processing {}'.format(i+1, numsteps, filename))

            resultsPP, results, _, _ = load_data_compact_pump_probe(channels_pp, channels_all, step)

            IzeroP = resultsPP[channel_Izero122].pump
            IzeroU = resultsPP[channel_Izero122].unpump

            thresh = (IzeroP>I0_threshold) & (IzeroU>I0_threshold)

            IzeroP = IzeroP[thresh]
            IzeroU = IzeroU[thresh]
            Delays_fs_shot.extend((resultsPP[channel_delay_beckhoff].pump)[thresh])

            spectrum_roi_on  = {}
            spectrum_roi_off = {}
            spectrum_roi_shots_on  = {}
            spectrum_roi_shots_off = {}
            
            tags = []
		
            for roi in channels_ROI:
                tag = roi
                
                data_on  = (resultsPP[roi].pump)[thresh]
                data_off = (resultsPP[roi].unpump)[thresh]
		    
                thr_on  = threshold(data_on, thr_low, thr_high)
                spec_on = np.sum(thr_on, axis=1)
                spec_on = spec_on / IzeroP[:,None]
                spectrum_roi_shots_on[tag] = spec_on
                spec_on = np.nanmean(spec_on, axis=0)
                
                thr_off  = threshold(data_off, thr_low, thr_high)
                spec_off = np.sum(thr_off, axis=1)
                spec_off = spec_off / IzeroU[:,None]
                spectrum_roi_shots_off[tag] = spec_off
                spec_off = np.nanmean(spec_off, axis=0)

                spectrum_roi_on[tag]  = spec_on
                spectrum_roi_off[tag] = spec_off
                tags.append(tag)

            spectra_on.append(spectrum_roi_on)
            spectra_off.append(spectrum_roi_off)
            spectra_shots_on.append(spectrum_roi_shots_on)
            spectra_shots_off.append(spectrum_roi_shots_off)
            
            os.makedirs(savedir+'/'+filename, mode=0o775, exist_ok=True)
            save_data_pp(savedir+'/'+filename, spectrum_roi_shots_on, spectrum_roi_shots_off, resultsPP[channel_delay_beckhoff].pump)
       
        if i==0:
            meta = resultsPP["meta"]
    
    return(spectra_on, spectra_off, spectra_shots_on, spectra_shots_off, Delays_fs_shot, tags, readbacks, meta)

def Johann_static(detector, scan, channels_list, thr_low, thr_high, numsteps=None):
    clock_int = clock.Clock()
    
    s = scan[0]
    channels_ROI = Get_ROI_names(s, detector)
    channels_list = channels_list + channels_ROI

    readbacks = scan.readbacks
    if numsteps==None:
        numsteps=len(scan)
    
    intensity       = []
    intensity_shot  = []
    
    for i, step in enumerate(scan[:numsteps]):
	    
        check_files_and_data(step)
        check = get_filesize_diff(step)  
        if check:
            clear_output(wait=True)
            filename = scan.files[i][0].split('/')[-1].split('.')[0]
            print ("Took {} seconds for the previous step".format(clock_int.tick()))
            print ('Processing: {}'.format(scan.fname.split('/')[-3]))
            print ('Step {} of {}: Processing {}'.format(i+1, numsteps, filename))

            results, _ = load_data_compact(channels_list, step)

            Izero = results[channel_Izero122]

            intensity_roi = {}
            intensity_roi_shot = {}
            
            tags = []
		
            for roi in channels_ROI:
                tag = roi
                
                data = results[roi]
		    
                thr = threshold(data, thr_low, thr_high)

                inten = np.sum(thr, axis=1)
                inten = np.sum(inten, axis=1)
                inten = inten / Izero
                intensity_roi_shot[tag] = inten
                inten = np.sum(inten)                

                intensity_roi[tag]  = inten
                tags.append(tag)

            intensity.append(intensity_roi)
            intensity_shot.append(intensity_roi_shot)
       
        if i==0:
            meta = results["meta"]
    
    return(intensity, intensity_shot, tags, readbacks, meta)

def VonHamos_static(detector, scan, channels_list, thr_low, thr_high, savedir, I0_threshold, badruns, numsteps=None):
    clock_int = clock.Clock()
    
    s = scan[0]
    channels_ROI = Get_ROI_names(s, detector)
    channels_list = channels_list + channels_ROI

    readbacks = scan.readbacks
    if numsteps==None:
        numsteps=len(scan)
    
    spectra       = []
    spectra_shots = []

    for i, step in enumerate(scan[:numsteps]):
        check_files_and_data(step)
        check = get_filesize_diff(step)  
        if i+1 in badruns: 
            check=False
        if check:
            clear_output(wait=True)
            filename = scan.files[i][0].split('/')[-1].split('.')[0]
            print ("Took {} seconds for the previous step".format(clock_int.tick()))
            print ('Processing: {}'.format(scan.fname.split('/')[-3]))
            print ('Step {} of {}: Processing {}'.format(i+1, numsteps, filename))

            results, _ = load_data_compact(channels_list, step)

            Izero = results[channel_Izero122]

            thresh = Izero>I0_threshold

            Izero = Izero[thresh]
            
            spectrum_roi = {}
            spectrum_roi_shots = {}            
            tags = []
		
            for roi in channels_ROI:
                tag = roi
                
                data = (results[roi])[thresh]
		    
                thr = threshold(data, thr_low, thr_high)
                spec = np.sum(thr, axis=1)
                spec = spec / Izero[:,None]
                spectrum_roi_shots[tag] = spec
                spec = np.sum(spec, axis=0)

                spectrum_roi[tag]  = spec
                tags.append(tag)

            spectra.append(spectrum_roi)
            spectra_shots.append(spectrum_roi_shots)
            
            os.makedirs(savedir+'/'+filename, mode=0o775, exist_ok=True)
            save_data(savedir+'/'+filename, spectrum_roi_shots)
       
        if i==0:
            meta = results["meta"]
    
    return(spectra, spectra_shots, tags, readbacks, meta)


def unwrap_data_PP(ROIs, counter, on, off):
    ons  = {}
    offs = {}
    for key in ROIs:
        on_roi  = []
        off_roi = [] 
        for index_step in range(counter):
            on_roi.append(on[index_step][key])
            off_roi.append(off[index_step][key])
        ons[key] = on_roi
        offs[key] = off_roi
    return ons, offs

def unwrap_data_static(ROIs, counter, spec_array):
    specs  = {}
    for key in ROIs:
        specs_roi  = []
        for index_step in range(counter):
            specs_roi.append(spec_array[index_step][key])
        specs[key] = specs_roi
    return specs


def unwrap_data_PP_delayscan(ROIs, counter, ints_on, ints_off):
    intss_on  = {}
    intss_off = {}
    for key in ROIs:
        int_on  = []
        int_off = [] 
        for index_step in range(counter):
            int_on.extend(ints_on[index_step][key])
            int_off.extend(ints_off[index_step][key])
        intss_on[key] = int_on
        intss_off[key] = int_off
    return intss_on, intss_off

def save_data(reducedir, spec_shots):
    run_array = {}
    run_array = {"spectrum_roi_shots": spec_shots}

    np.save(reducedir+'/run_array', run_array)


def save_data_pp(reducedir, ons, offs, delays):
    run_array = {}
    run_array = {"spectrum_roi_shots_on": ons,
                 "spectrum_roi_shots_off": offs,
                 "Delay_fs_shot": delays}

    np.save(reducedir+'/run_array', run_array)

















def XES_static_ROIs(scan, channels_list, thr_low, thr_high, index=0, del_bkg=True):
    s = scan[index]
    detector = "JF10T01V01"
#    detector = "JF02T09V03"
#    channels_ROI = add_ROI_channels(s, detector)

    channels_ROI = Get_ROI_names(s, detector)
    #channels_ROI = ['JF02T09V03:ROI_Ka_Si331', 'JF02T09V03:ROI_Ka_Si333']
    print (channels_ROI)
    if del_bkg:
        channels_ROI = clean_ROI_names(channels_ROI)
    channels_list = channels_list + channels_ROI
    
    check_files_and_data(s)
    check = get_filesize_diff(s)

    energy = scan.readbacks
    
    intensity  = []
    intensity_peak = []
    spectra = []
    Delays_fs_shot = []

    for i, step in enumerate(scan):
    
        if check:
            clear_output(wait=True)
            filename = scan.files[index][0].split('/')[-1].split('.')[0]

            print ('Processing: {}'.format(scan.fname.split('/')[-3]))
            print ('Step {} of {}: Processing {}'.format(i+1, len(scan.files), filename))
    	     
            results, _ = load_data_compact(channels_list, step)

            Delays_fs_shot.extend(results[channel_delay_beckhoff])
    	    
            thresholded = {}
            averaged = {}
            spectrum = {}
            tags = []

            intensity_roi = {}
            intensity_peak_roi = {}
            
            for roi in channels_ROI:
                data = results[roi]
                thr  = threshold(data, thr_low, thr_high)
                if angle_rot[roi] != 0:
                    thr = ndimage.rotate(thr, angle_rot[roi], axes=(1,2), reshape=False)
                avg   = np.average(thr, axis=0) 
                proj  = np.sum(avg, axis=0)
                inten = np.sum(avg)
                
                maxind = np.argmax(proj)
                int_peak = np.sum(proj[maxind-3:maxind+3])
                
                tag = roi#.split(':')[-1]
                
                thresholded[tag] = thr
                averaged[tag] = avg
                spectrum[tag] = proj
                tags.append(tag)
                
                #intensity.append(np.sum(avg))
                intensity_roi[tag]  = inten
                intensity_peak_roi[tag] = int_peak
                #print (intensity)

            intensity.append(intensity_roi)
            intensity_peak.append(intensity_peak_roi)
            spectra.append(spectrum)
    	    
        meta = results["meta"]

    return(results, energy, intensity, intensity_peak, spectra, tags, meta, Delays_fs_shot)

def clean_ROI_names (channels_ROI):
    for ROIname in channels_ROI:
        if "bkg" in ROIname:
            channels_ROI.remove(ROIname)
    return channels_ROI

def unwrap_data2(ROIs, counter, intensities):
    ints  = {}
    for key in ROIs:
        int_all = []
        for index_step in range(counter):
            #print (index_step, key)
            #print (intensities[index_step][key])
            int_all.append(intensities[index_step][key])
            #print (np.shape(int_all))
        ints[key] = int_all
        #print (ints[key])
    return ints



def unwrap_data_PP_TT(ROIs, counter, ints_on, ints_off):
    intss_on  = {}
    intss_off = {}
    for key in ROIs:
        int_on  = []
        int_off = [] 
        for index_step in range(counter):
            int_on.extend(ints_on[index_step][key])
            int_off.extend(ints_off[index_step][key])
        intss_on[key] = int_on
        intss_off[key] = int_off
    return intss_on, intss_off

def unwrap_spectra_PP_TT(ROIs, counter, specs_on, specs_off):
    specss_on  = {}
    specss_off = {}
    for key in ROIs:
        s_on  = []
        s_off = [] 
        for index_step in range(counter):
            s_on.extend(specs_on[index_step][key])
            s_off.extend(specs_off[index_step][key])
        specss_on[key] = s_on
        specss_off[key] = s_off
    return specss_on, specss_off

def XES_delayscan_ROIs(detector, scan, channels_list, thr_low, thr_high, numsteps=-1, del_bkg=True):
    from alvra_tools import clock
    clock_int = clock.Clock()
    s = scan[0]
    channels_ROI = Get_ROI_names(s, detector)
    if del_bkg:
        channels_ROI = clean_ROI_names(channels_ROI)
    channels_pp = [channel_Events] + channels_list + channels_ROI
    channels_all = channels_pp

    readbacks = scan.readbacks
    
    spectra_on = []
    spectra_off = []
    spectra_shots_on = []
    spectra_shots_off = []
    thresholdeds_on = []
    thresholdeds_off = []
    intensity_on  = []
    intensity_off = []
    Delays_fs_shot = []

    for i, step in enumerate(scan[:numsteps]):
	    
        check_files_and_data(step)
        check = get_filesize_diff(step)  
        if check:
            clear_output(wait=True)
            filename = scan.files[i][0].split('/')[-1].split('.')[0]
            print ("Took {} seconds for the previous step".format(clock_int.tick()))
            print ('Processing: {}'.format(scan.fname.split('/')[-3]))
            print ('Step {} of {}: Processing {}'.format(i+1, numsteps, filename))

            resultsPP, results, _, _ = load_data_compact_pump_probe(channels_pp, channels_all, step)

            IzeroP = resultsPP[channel_Izero122].pump
            IzeroU = resultsPP[channel_Izero122].unpump

            Delays_fs_shot.extend(resultsPP[channel_delay_beckhoff].pump)
		
            thresholded_on = {}
            averaged_on = {}
            spectrum_on = {}
            spectrum_shots_on = {}
		
            thresholded_off = {}
            averaged_off = {}
            spectrum_off = {}
            spectrum_shots_off = {}

            intensity_roi_on = {}
            intensity_roi_off = {}

            tags = []
		
            for roi in channels_ROI:
                data_on = resultsPP[roi].pump
                data_off = resultsPP[roi].unpump
		    
                thr_on  = threshold(data_on, thr_low, thr_high)
                if angle_rot[roi] != 0:
                    thr_on = ndimage.rotate(thr_on, angle_rot[roi], axes=(1,2), reshape=False)

                inten_on = np.sum(thr_on, axis=1)
                inten_on = np.sum(inten_on, axis=1)
                inten_on = inten_on / IzeroP 
                inten_on = np.sum(inten_on)
                
                avg_on  = np.average(thr_on, axis = 0)
                spec_shots_on = thr_on.sum(axis=1)
                spec_on = avg_on.sum(axis=0)
                # inten_on = np.sum(avg_on)         # uncomment for real Johann data!
		    
                thr_off  = threshold(data_off, thr_low, thr_high)
                if angle_rot[roi] != 0:
                    thr_off = ndimage.rotate(thr_off, angle_rot[roi], axes=(1,2), reshape=False)

                inten_off = np.sum(thr_off, axis=1)
                inten_off = np.sum(inten_off, axis=1)
                inten_off = inten_off / IzeroP 
                inten_off = np.sum(inten_off)

                avg_off  = np.average(thr_off, axis = 0)
                spec_shots_off = thr_off.sum(axis=1)
                spec_off = avg_off.sum(axis=0)
                #inten_off = np.sum(avg_off)      # uncomment for real Johann data!   
		    
                tag = roi#.split(':')[-1]
    
                thresholded_on[tag] = thr_on
                averaged_on[tag] = avg_on
                spectrum_on[tag] = spec_on
                spectrum_shots_on[tag] = spec_shots_on
		    
                thresholded_off[tag] = thr_off
                averaged_off[tag] = avg_off
                spectrum_off[tag] = spec_off
                spectrum_shots_off[tag] = spec_shots_off

                intensity_roi_on[tag]  = inten_on
                intensity_roi_off[tag] = inten_off
		
                tags.append(tag)

            spectra_on.append(spectrum_on)
            spectra_off.append(spectrum_off)
            spectra_shots_on.append(spectrum_shots_on)
            spectra_shots_off.append(spectrum_shots_off)
            thresholdeds_on.append(thresholded_on)
            thresholdeds_off.append(thresholded_off)
            intensity_on.append(intensity_roi_on)
            intensity_off.append(intensity_roi_off)

        if i==0:
            meta = resultsPP["meta"]
    
    return(intensity_on, intensity_off, spectra_on, spectra_off, spectra_shots_on, spectra_shots_off, thresholdeds_on, thresholdeds_off, tags, readbacks, Delays_fs_shot, meta)
