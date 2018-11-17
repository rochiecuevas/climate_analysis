# What's the weather like in Oahu, HI?

## Introduction
Hawaii is an archipelago of [volcanic islands](https://oceanservice.noaa.gov/facts/hawaii.html) in the north Pacific Ocean. It is a popular tourist destination all year round. There are [eight main islands](https://en.wikipedia.org/wiki/List_of_islands_of_Hawaii): Hawai'i, Maui, Kaho'olawe, Lana'i, Moloka'i, O'ahu, Kaua'i, and Ni'ihau. O'ahu is the [third largest](https://traveltips.usatoday.com/8-large-islands-hawaii-108082.html) island in the archipelago and one with varied geographies. It features a plateau in between two parallel mountain ranges. [It is widely known](https://www.britannica.com/place/Oahu) for its place in modern military history, its tourism, and its pineapples. 
<br><br>
When is the best time to visit O'ahu? A factor that certainly contributes to one's decision is the weather. In this study, I explored the weather patterns (indicated by precipitation and temperature). A case study is presented in which the weather during my vacation there is indicated.
## Method
Data was obtained from nine weather stations located in the central, the eastern, and the southern parts of the island (Figure 1).
<br><br>
![map_markers](https://github.com/rochiecuevas/climate_analysis/blob/master/Images/map_markers.png)

Fig 1. Location of the weather stations in O'ahu.
<br><br>
These stations are found in different elevations (Table 1). The weather station with the lowest elevation, Honolulu Observatory is located near Ewa Beach. On the other hand, the weather station with the highest elevation, Upper Wahiawa 874.3, is located in the plateau between the Waianae range (to the west) and the Koolau range (to the east). [These mountain ranges used to be shield volcanoes](https://www.gohawaii.com/islands/oahu/travel-info/maps).
<br><br>
Table 1. Elevations of the different weather stations in O'ahu

|Station ID|Station Name|Elevation (masl)|
|---|---|---:|
|USC00519397|Waikiki 717.2|3.0|
|USC00513117|Kaneohe 838.1|14.6|
|USC00514830|Kualoa Ranch HQ 886.9|7.0|
|USC00517948|Pearl City|11.9|
|USC00518838|Upper Wahiawa 874.3|306.6|
|USC00519523|Waimanalo Experimental Farm|19.5|
|USC00519281| Waihee 837.5|32.9|
|USC00511918| Honolulu Observatory 702.2|0.9|
|USC00516128| Manoa Lyon Arboretum 785.2|152.4|

<br>Daily weather data (precipitation and temperature) were obtained from these weather stations and stored in the  `hawaii.sqlite` database. This database consists of two tables: `Measurements` and `Stations`. The data was then reflected into Python ([version 3.6.6](https://www.python.org/downloads/release/python-366/)) using [SQLAlchemy](https://www.sqlalchemy.org/). Data was processed using [pandas](https://pandas.pydata.org/pandas-docs/stable/), [numpy](http://www.numpy.org/), and [datetime](https://docs.python.org/3/library/datetime.html) modules. Data visualisation was  performed using [matplotlib](https://matplotlib.org/contents.html) and [seaborn](https://seaborn.pydata.org/) modules.
<br><br>
  
## Case study
The database contains weather data from January 1, 2010 to August 23, 2017.

```python
# Return the earliest date in the dataframe
Earliest_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()
first_date = Earliest_date[0]
first_date

# Return the latest date in the dataframe
Latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
end_date = Latest_date[0]
end_date
```


