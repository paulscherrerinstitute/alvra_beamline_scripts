This repository contains mainly Jupyter notebooks scripts to be used for the analysis of the JF4p5 images and BS data.

Files:

Scripts for XANES data loading and plotting:

1) Reduce_XANES.ipynb	
Loads and reduce scans (raw data) acquired for XAS in TFY (pips or APD diodes), saves reduced data as NPY arrays to be loaded by other scripts.

2) Plotting_XANES.ipynb
Loads reduced data, does filtering based on correlation, averages or compares between different scans. 
Also plots 2D (delay vs energy) scans acquired with continuous delay stage movement.

3) Plotting_XANES_timescans.ipynb
Loads reduced data, does rebinning of the time delay axis, filtering based on correlation, averages or compares between different scans. 
Fits risetime or decay time constants.

4) XANES_static.ipynb
Loads, reduces and plots data from static (not pump probe) XANES spectra.
It does the filter based on correlation, averages multiple scans if requested or plot them together.

... to be completed...
