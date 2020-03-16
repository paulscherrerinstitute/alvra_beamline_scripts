This repository contains mainly Jupyter notebooks scripts to be used for the analysis of the JF4p5 images and BS data.

Files:


Scripts for JF data loading and plotting:

1) XES_pump_probe.ipynb
script to load the full detector (JF4p5M or FLEX ones) images, convert them (apply gain, pedestal, module map, crop ROIs). It can be used to load a single file or an energy (resonanat XES) or time scan. The analysis is done with thresholding, summing and distributing ON and OFF. Finally it plots the projections for pump probe XES data. Uses the new jungfrau_utils library: 8000 images for 9 modules (4.5M) require about 45 seconds processing time.

2) XES_pump_probe_CROP.ipynb			
script to load cropped ROIs, set up in run_control. The data are already converted and reduced within the pipeline and saved in /sf/alvra/data/*pgroup*/res. It can be used to load a single file or an energy (resonanat XES) or time scan. The script loads the images, apply threshold, and distribute ON and OFF. It plots the projections for pump probe XES data. Does not need the new jungfrau_utils.

3) XES_noPP.ipynb
script to load the full detector (JF4p5M or FLEX ones) images, convert them (apply gain, pedestal, module map, select ROIs), does not distribute images in ON / OFF but averages all of them. It can be used to load a single file or an energy (resonanat XES). The analysis is done with thresholding. Finally it plots the projections for XES data in the chosen ROIs (standard 2 with 2 backgrounds). Uses the new jungfrau_utils library: 8000 images for 9 modules (4.5M) require about 45 seconds processing time.



Scripts for XANES data loading and plotting:

1) XAS_monoscans_norm.ipynb	
script for loading Xray diode (PIPS) data for plotting time resolved XANES in TFY. Normalization is done shot-to-shot after filtering the shots based on histograms of fluorescence and Izero data (correlation). 

2) XAS_monoscans_norm_noPP.ipynb	
script for loading Xray diode (PIPS) data for plotting in TFY. Rarely use, just in case of no pump probe data, however the previous script is more regularly updated and can handle the same (by summing pump and unpump data). 

3) XAS_timescan_norm.ipynb	
script for loading Xray diode (PIPS) data for plotting time scans at fixed incident energy in TFY. Normalization is done shot-to-shot after filtering the shots based on histograms of fluorescence and Izero data (correlation). 

4) XAS_fluencescan_norm.ipynb	
script for loading Xray diode (PIPS) data for plotting fluence scans at fixed delay incident energy in TFY. Normalization is done shot-to-shot after filtering the shots based on histograms of fluorescence and Izero data (correlation). 

Scripts for general beamline use:

1) YAG_pump_probe.ipynb
Script to read the cross-correlation YAG scans for t0 determination. Normalization is done shot-to-shot and averaged. 

2) scanMono_noPP.ipynb
Script to read the transmission through the mono with a downstream intensity monitor and plot the spectrum, also fitted with a Gaussian curve to return the central energy and the width.

3) Knife_edge_noPP.ipynb
Script to read the FEL transmission across the knife edges, used to measure the focused beam size. The error function plot can be fitted to return the width in X and Y.

4) Jet_scans_noPP.ipynb
Script to read and plot the fluorescence (and transmission) Xray diode as a function of X stage values, run to precisely determine the jet position.

5) BS_check_Laser_int.ipynb
script for reading data to look at signals from laser diodes. Used to confirm illumination mode (4/1, 11/1, 19/1) in the debug phase of these different modes.

6) BSread_singleChannel.ipynb
simple script used to load only one BS channel. Can be used to plot correlations between different detectors used as intensity monitors (PBPSs, gas monitor, etc etc)

7) PALM_processing.ipynb
Script used to load and process PALM data, based on similar scripts from Photon Diagnostics group (C. Arrell). Composed essentially by two parts: a) loading and processing of a THz scan recorded in eco, b) extraction of arrival times with the palm_setup function contained within the Photodiag package. Picks up the pumped shots via event code (if saved).
