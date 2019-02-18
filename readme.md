This repository contains mainly Jupyter notebooks scripts to be used for the analysis of the JF4p5 images and BS data.

Files:


Sripts for JF data loading and plotting:

1) alvra_exp-Copy5.ipynb                        Very first script for the analysis of the JF4p5 data.
                                                This is an old file which was the basis for developing the other files
						Version from July 2018, after TiO2 beamtime -- p17245

2) XES_scans_analysis_Febpy_Oct18.ipynb		script for JF4p5 data, single files or for looping over scan data
						Not normalized data.
						Version from November 2018, after Febpy commissioning beamtime -- p17589

3) XES_analysis_BSnorm.ipynb			script for JF4p5 data, single files or for looping over scan data
						The data are normalized with the Izero data saved in the BSREAD parallel file
                                                Version from November 2018, after Febpy commissioning beamtime -- p17589



Scripts for BS data loading and plotting:

4) BS_analysis.ipynb				script for BS data only (no JF), for looping over scan data.
						Version from November 2018, after Febpy commissioning beamtime -- p17589

5) BS_scans_json.ipynb                          script for BS data only (no JF), for looping over scan data.
						Upgraded version (much faster) from January 2019, prepared for CytC beamtime -- p17803



Scripts for the analysis of YAG pump probe data for T0 determination:
						
6) YAG_pumpprobe_BS.ipynb                       script for analyzing the YAG data (FEL pump, laser probe).
						In this script the laser runs at double rate than the FEL (50 vs 25 Hz for instance).
						The script is very similar to BS_analysis, but better create another one with the proper assignment of FEL on/off shots
						Version prepared for the SFX Rhodopsin beamtime -- p17569 						

7) YAG_pumpprobe_BS_GK.ipynb			same as before (YAG_pumpprobe_BS) 
						Most recent version, updated and used during the SFX Rhodopsin beamtime -- p17569

8) YAG_scans_json.ipynb				script for YAG scans, with more efficient and fast data loading and on/off distribution.
						Version created in January 2019, prepared for the CytC beamtime -- p17803

9) YAG_scans_json_norm.ipynb			script for YAG scans, status as at the end of the CytC beamtime -- p17803
						Added normalization shot-to-shot, ready for KR2 sfx beamtime -- p17806

10) YAG_scans_json_norm_Izero.ipynb		Same as before, but with additional condition on Izero intensity.
						Ready for KR2 sfx beamtime -- p17806


Scripts for the analysis of the knife edge scans for xray & laser spotsize determination: 

9) Knife_edge_scans.ipynb			script for Knife edge scans
						Created and used during the SFX Rhodopsin beamtime -- p17569

10) Knife_edge_scans_json.ipynb			script for Knife edge scans
						Upgraded version (faster) created in January 2019, prepared for CytC beamtime -- p17803
