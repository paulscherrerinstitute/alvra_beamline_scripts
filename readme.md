This repository contains mainly Jupyter notebooks scripts to be used for the analysis of the JF4p5 images and BS data.

Files:


Scripts for JF data loading and plotting:

1) XES_scans_process.ipynb			script to select ROIs in the JF4p5 data and save only cropped data.
						This is *not* used for any analysis.
						Use it to crop/process (pedestals & gain corrections and save the raw data)
						This procedure has been made automatic with the watcher.py and the associated 
						XES_process.py script, but can be still run manually with this notebook.
						
2) XES_scans_json_final.ipynb			script for JF4p5 data, can be used for analysis of 3 different kind of files:
						a) individual independent files (recorded with bsdaqJF.acquire)
						b) individual files in a scan (recorded with scansJF.ascan)
						c) looping through all the files of a scan (recorded with scansJF.ascan)
						This script loads the all image from the detector and does the ROI selection.
						If the ROIs have been already saved in a separate (smaller) file, use the 
						"XES_scans_readout_cropped_final.ipynb" script.
						
3) XES_scans_readout_cropped_final.ipynb	script for JF4p5 data, used for analysis of single files or files in a scan.
						Used for cropped data.
						
						
Scripts for BS data loading and plotting:

1) BS_check_Laser_int.ipynb			script for BS data only (no JF), to look at signals from laser diodes.
						Used to confirm illumination mode (4/1, 11/1, 19/1) etc etc.
						
2) BSread_singleChannel.ipynb			simple script used to load only one BS channel.

3) BSdataLoad_final.ipynb			---
						


Scripts for the analysis of YAG pump probe data for T0 determination:
						
1) YAG_pumpprobe_BS.ipynb                       script for analyzing the YAG data (FEL pump, laser probe).
						In this script the laser runs at double rate than the FEL (50 vs 25 Hz for instance).
						The script is very similar to BS_analysis, but better create another one with the proper assignment of FEL on/off shots
						Version prepared for the SFX Rhodopsin beamtime -- p17569 						

2) YAG_pumpprobe_BS_GK.ipynb			same as before (YAG_pumpprobe_BS) 
						Most recent version, updated and used during the SFX Rhodopsin beamtime -- p17569

3) YAG_scans_json.ipynb				script for YAG scans, with more efficient and fast data loading and on/off distribution.
						Version created in January 2019, prepared for the CytC beamtime -- p17803

4) YAG_scans_json_norm.ipynb			script for YAG scans, status as at the end of the CytC beamtime -- p17803
						Added normalization shot-to-shot, ready for KR2 sfx beamtime -- p17806

5) YAG_scans_json_norm_Izero.ipynb		Same as before, but with additional condition on Izero intensity.
						Ready for KR2 sfx beamtime -- p17806


Scripts for the analysis of the knife edge scans for xray & laser spotsize determination: 

1) Knife_edge_scans.ipynb			script for Knife edge scans
						Created and used during the SFX Rhodopsin beamtime -- p17569

2) Knife_edge_scans_json.ipynb			script for Knife edge scans
						Upgraded version (faster) created in January 2019, prepared for CytC beamtime -- p17803
						Kept the same name for the improved version used during CytC beamtime.
						Added loaded channels and plots also for jet X-scans.
