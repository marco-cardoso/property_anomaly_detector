**<h1>Zoopla API scraper</h1>**

The zoopla.py script uses the ZOOPLA API to get properties from the London districts that are currently being displayed in their website.
Make sure to have installed all the dependencies available in one of the package files in the root of this
project. E.g requirements.txt

You also need to have the follow environment variables properly configured :

<ul>
    <li>
        ZOOPLA_API
        <p>Your Zoopla API key. In order to get it you need to register into ZOOPLA website : </p>
        <a href="https://developer.zoopla.co.uk">https://developer.zoopla.co.uk</a>
    </li>
    <li>
        MONGO_HOST
        <p>Your MongoDB host.</p>
    </li>
    <li>
        MONGO_PORT
        <p>Your MongoDB port</p>
    </li>
</ul>


It's also necessary to have a MongoDB collection with the London districts. In order to
create this collection execute once the script located at :

    src/property_anomaly_detector/datasets/save_ld_district_names.py

All the instructions necessary to run save_ld_district_names.py are available on itself.

With all necessary steps done simply execute :

    python zoopla.py

At the end of the execution a log will be generated in this folder called debug.log. 
    
**It takes several hours** to get all the properties since It's respecting the website policy of 
100 requests per hour.