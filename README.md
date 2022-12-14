# Traffic Anoamly Detection with TP-FDS
This repository contains traffic data with anomalies being labeled by 20 different experts using TP-FDS. 
A Python code is also included that applies Fast-ABOD to traffic data benefiting from the TP-FDS. Other anomaly detection methods also can be imbeded in this code for comparison purposes (See the PyOD library).

The labeled data can be found in the "Labeled Data" folder. Data collected in Melbourne arterials are the files named with a single number and a letter. The number indicate the location (intersection) of the loop detectors (as in the provided figure), and the letter shows the direction of the incoming traffic to the intersection.   
The name of the sites used from the Seattle loop data are mentioned in the name of the other four csv files. 
More information about the Seattle dataset can be found in: https://github.com/zhiyongc/Seattle-Loop-Data 

![image](https://user-images.githubusercontent.com/112522995/211434468-132e50da-4ff4-4a58-805d-857a1decca57.png)


## Data Visualization

The labeling procedure is recorded for better understanding: https://youtu.be/I7wv8SyDsaQ . We used dash from Plotly to build the web app for this experiment. A sample code for design of the dash app can be found in https://github.com/imaantaheri/anomaly-labeling. 
A TP-FDS demonstration of the data from 14-E.csv is shown here with colors indicating the anomaly probability.

![image](https://user-images.githubusercontent.com/112522995/207738766-6141bff3-89c7-4d29-bc87-699cfd137e17.png)

The whole data with selected anomalies can be oserved below. The color bar shows the propability of the points being anomalous.
It can be observed that anomalies can be found in every parts of the diagram both in the congested and uncongested regimes. 

![image](https://user-images.githubusercontent.com/112522995/211430268-522e30db-fb38-4569-86b9-1e54a31ec1d2.png)

## Analysis of the labels in time series view

A part of the data from one location is selected and points with more than 70% of anomaly probability are spotted on it.
As we can see, looking at the data, with benefiting from the TP-FDS, not only improves the labeling speed, but also results in a more precise labeling outcomes. Selection of all anomalies are justifyable (see the below figure). There are some situations (as mentioned by the red box in the figure below) that may seem to be anomalous, but it is not labeled by the TP-FDS. These parts show the power of the TP-FDS as it considers all the data at once (not just a part of it like in the below) to make a judgment about the data.   

![image](https://user-images.githubusercontent.com/112522995/211432048-dbd49049-33ec-4db6-a45c-64557d0b2795.png)
