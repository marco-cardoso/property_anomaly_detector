
<h1>London Rental Property Anomaly Detector</h1>

<h2>Description</h2>

Yearly, many people, when renting a property, are victims of scams in many websites worldwide. 
Fraudsters pose as landlords and convince would-be tenants to send funds via money transfer. Typically
they create advertisements of great properties for an incredibly low price compared to properties of 
the same category. Under the pressure of making a "great deal"  most part of the victims do everything
the fraudsters tell them to do because of the fear of other people renting the property.

There's a great video from BBC explaining better how the scams work (Click in the image below to watch on youtube) :

[![BBC Video](https://img.youtube.com/vi/mOGAxUqHxsE/0.jpg)](https://www.youtube.com/watch?v=mOGAxUqHxsE)


Property rental websites are very similar : They possess a webpage listing the advertisements with options to filter the
results. Each advertisement has a page that can put you in touch with the property agent/fraudster. 


![alt text](https://github.com/marco-cardoso/property_anomaly_detector/blob/master/zoopla_properties.png)


This project aims to create an unsupervised solution for the problem using machine learning to help the website managers
to identify scams.


<h2> System </h2>

It was created a system to download the London properties from Zoopla daily and apply the anomaly detector over them. For each property,
an anomaly score is attached. Zoopla was chosen because it has an API with endpoints to download rental properties. As the name
suggests just because it has a high anomaly score it does not mean that it is a scam. It could be a real agent offering a great deal or
an advertisement with misfiled fields. Consequently, an anomaly. That is the reason that the name of the project is not "scam detector". 
However, if someone creates a scam with a very attractive price, certainly will receive a high anomaly score.

![PAD DASH](https://github.com/marco-cardoso/property_anomaly_detector/blob/master/pad_dash.png)

Every day a routine detects the TOP 100 London properties with the highest scores and displays in the table. You can click in each anomaly
to see the bar plot comparison and the property location. This tool could be used by the website managers to help them to spot scams. 

You can also insert the data of a property individually to check its anomaly score. Just click on the "Classify" button.

![ss individual](https://github.com/marco-cardoso/property_anomaly_detector/blob/master/classify_individual_property.png)

This dialog will show the given property anomaly score and the daily highest anomaly score for comparison purposes.

You can visit the system at : http://3.13.238.29:8080


<h2> Architecture </h2>

![arch](https://github.com/marco-cardoso/property_anomaly_detector/blob/master/pad_arch.jpg)

This is the repository responsible to store the backend code. </br>
The repository with the React API is available at : https://github.com/marco-cardoso/property_anomaly_detector_frontend

<h3> React instance </h3>

<ul>
    <li>Nginx container - Responsible to handle the requests and send them to the React API </li>
    <li>React container - Responsible to serve the SPA</li>
</ul>

<h3> Flask instance </h3>

<ul>
    <li>Nginx container - Responsible to handle the requests and send them to the Flask API </li>
    <li>Flask container - Responsible to load the anomalies from the database and classify them individually</li>
    <li>CRON container - Responsible to update the anomalies daily</li>
    <li>Mongo container - Where the TOP 100 anomalies are stored at each CRON run</li>
</ul>

<h4> Modularization </h4>

It was decided to separate the app in two python packages : A module with everything related to the API and another with the 
functions related to ML and the jupyter notebooks.

Docker uses them to build the containers. 

Both are available at : https://github.com/marco-cardoso/property_anomaly_detector/tree/master/packages 

The flask container uses the API package to run the flask app using gunicorn as server and the anomaly package to
perform operations related to the anomalies. The CRON container uses just the last one.


<h3>Docker</h3>

Requirements
<ul>
    <li>At least dockver v19.03.12 </li>
    <li>At least docker-compose v1.26.2</li>
    <li>An AWS account with an IAM user that has full access to S3.</li>
</ul>

Change the below environment variables values, located at :

https://github.com/marco-cardoso/property_anomaly_detector/blob/master/variables.env

<ul>
    <li>ZOOPLA_API - YOUR_ZOOPLA_KEY </br>
      https://developer.zoopla.co.uk/
    </li>
</ul>

After the requirements are satisfied open a terminal in the project root folder and type :

    docker-compose up --build
    
<h3>Warning</h3>

Ideally, the best architeture would be a separated instance for MONGO and CRON containers. With more
attention to the last one, given the fact that is responsible to load thousands of MongoDB documents and detect the latest
anomalies, using a lot of RAM memory and CPU power. Nonetheless, this architecture was chosen for simplicity and to
reduce the costs on AWS, since only one instance is enough due to the low amount of user requests.


<h2> Anomaly detection method </h2>

https://github.com/marco-cardoso/property_anomaly_detector/blob/master/packages/property_anomaly_detector/property_anomaly_detector/anomaly/detect_anomalies.py


The first step to come up with a solution for the problem was to perform an EDA to understand the data better, the results are available at :

https://github.com/marco-cardoso/property_anomaly_detector/blob/master/notebooks/eda.ipynb

Since the main focus of the project is to detect anomalies related to the monthly rental price there's no point in trying to detect
outliers related to the other features. We need to give more importance to properties at lower prices.


To detect the properties with the highest chance to be an anomaly the first step is to load all properties from the MongoDB. Then, they are
grouped by Type (Flat, studio, etc...) and Shared occupancy state (If is a shared property or not). The nearest neighbors 
algorithm ball_tree is applied to each group using the variables latitude, longitude, amount of bedrooms, and amount of receipts. The
algorithm, for each property, detects its 20 nearest neighbors. Finally, it calculates the median monthly rental price of the neighbors 
and subtracts with the price of the property being analysed. This process is done for all the properties in MongoDB. If the difference
between a property and its neighbors is positive it means the property is more expensive, otherwise it is cheaper. In order for the score
to be more intuitive it is multiplied by -1. So the higher the score the higher is the probability of being an anomaly.



<b>Why to not use property_type and shared_occupancy variables with the nearest neighbors algorithm, instead of grouping them ?</b>

Property type has many unique values. If OneHotEncoder was applied it would produce a huge amount of features. Consequently, it would increase
the processing time dramatically. And the most important factor : If a property has type X, which only has more two
properties in the entire database the nearest neighbor algorithm would use properties of other types to perform the distance calculation.
Using the other variables to get the nearest points, such as the number of bedrooms for example. This is not feasible, since just because
two properties have the same number of bedrooms and different types it does not mean they have similar prices. The price distributions 
vary very much for each property type. The same explanation applies to shared_occupancy.

<b>Why to not use the PyOD default KNearestNeighbors outlier implementation ?</b>

The PyOD KnearestNeighbors implementation detects multivariate outliers and does not have a parameter to calculate the outlier scores for 
a specific feature. It looks at all the features for outliers. Meaning that if a property has a strange amount of bedrooms or recepts it would receive
a high anomaly score. This problem only cares about the monthly rental price outliers, but taking into consideration the similarity of the other
features.


<b>Instead of using the nearest neighbors algorithm, why do not simply create a loop over the postal codes and apply the same process ?</b>

Many postal codes have few or many properties to perform the calculation, resulting in sometimes a result not very accurate.

<b>Why to not simply use the Z-Score test ?</b>

![z_score](https://i0.wp.com/statisticsbyjim.com/wp-content/uploads/2019/10/z-score_equ.png?resize=86%2C38&ssl=1)

Some groups of property types and shared occupancy have a lot of properties. Different boroughs have different distributions, if a property is near a touristic attraction
the price is higher. It's necessary to apply the nearest neighbor algorithm to take this into consideration. The final calculation (outlier score) is slightly similar to
the Z score. It just does not divide the subtraction by the standard deviation and uses the median instead of the mean. This way makes it more intuitive to understand the value itself, which is simply the inverse of the difference between the property rental price and the median of its neighbors.

