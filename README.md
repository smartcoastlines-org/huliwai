# huliwai

"huliwai" is the name given to the water sensor developed by the smartcoastlines.org project. It is an affordable data logger measuring pressure (water level), temperature, and light. In Hawaiian, 'huli' is sometimes used to mean 'to search', 'search out', or 'seek out', as well as 'turning' or 'flipping'. Huli Honua implies how Earth is studied, and we posit that through huli wai, we search beneath the water's surface for understanding and insight to derive solutions in watershed observations and restoration. We are also flipping the typical scientific model, by putting primary sensors and research tools into the hands of communities and educational groups who generally don't have direct access to such environmental sensor technologies.

The huliwai GitHub repository is the home for open-source code to work with the sensor loggers. Python scripts are available for interfacing with the sensors, verifying operations, collecting real-time sensor data, initiating a deployment schedule, downloading data, converting binary data files to csv, plotting data, and more. Running these scripts will be dependent on running other Python libraries, including matplotlib and scipy, and depending on your local configuration, you may need to 'sudo apt install libatlas-base-dev' in order to get scipy and numpy working.

The huliwai sensor was originally developed by Stanley H.I. Lio in Brian Glazer's lab for the smartalawai.org project, funded by the University of Hawaii at Manoa. Additional development and outreach support has been leveraged with support from the National Science Foundation, Schmidt Marine Technology Partners, and through a collaboration with the Purple Maia Foundation enabled by an EPA Environmental Education award. 

![image](/huliwai_stream.png)
