# What's the weather like in Oahu, HI?

## Introduction
Hawaii is an archipelago of [volcanic islands](https://oceanservice.noaa.gov/facts/hawaii.html) in the north Pacific Ocean. It is a popular tourist destination all year round. There are [eight main islands](https://en.wikipedia.org/wiki/List_of_islands_of_Hawaii): Hawai'i, Maui, Kaho'olawe, Lana'i, Moloka'i, O'ahu, Kaua'i, and Ni'ihau. O'ahu is the [third largest](https://traveltips.usatoday.com/8-large-islands-hawaii-108082.html) island in the archipelago and one with varied geographies. It features a plateau in between two parallel mountain ranges. [It is widely known](https://www.britannica.com/place/Oahu) for its place in modern military history, its tourism, and its pineapples. 
<br><br>
When is the best time to visit O'ahu? A factor that certainly contributes to one's decision is the weather. In this study, I explored the weather patterns (indicated by precipitation and temperature). A case study is presented in which the weather during my vacation there is indicated.

## Method
Daily weather data (precipitation and temperature) were obtained from these weather stations and stored in the  `hawaii.sqlite` database. This database consists of two tables: `Measurements` and `Stations`. The data was then reflected into Python ([version 3.6.6](https://www.python.org/downloads/release/python-366/)) using [SQLAlchemy](https://www.sqlalchemy.org/). Data was processed using [pandas](https://pandas.pydata.org/pandas-docs/stable/), [numpy](http://www.numpy.org/), and [datetime](https://docs.python.org/3/library/datetime.html) modules. Data visualisation was  performed using [folium](http://python-visualization.github.io/folium/docs-v0.5.0/modules.html), [matplotlib](https://matplotlib.org/contents.html) and [seaborn](https://seaborn.pydata.org/) modules.

### Database date range
To determine the date range, the earliest date was retrieved from the database and then sorted in ascending order; the date of the latest record was also determined by retrieving the dates from the database and then sorting the dates in descending order.

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

The end date was a string. To determine the date from one year ago (365 days), the end date was converted to the datetime format. 

```python
# Calculate the date 1 year ago from the last data point in the database
year_ago = dt.date(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:11])) - dt.timedelta(days = 365)
start_date = str(year_ago)
start_date
```

### Weather station information
A query was created to determine the number of stations included in the database.

```python
# Design a query to show how many stations are available in this dataset 
no_stns = session.query(func.count(distinct(Measurement.station))).all()
```

Then, a database was generated by merging the `Measurements` and `Stations` tables.

```python
# Merge the measurement and the station tables based on station id
sel = [Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs,
       Station.name, Station.elevation, Station.latitude, Station.longitude]

same_stn = session.query(*sel).filter(Measurement.station == Station.station).all()

# Create a dataframe combining Measurement and Station data
df1 = pd.DataFrame(same_stn)
```

The ranges of temperatures and precipitation levels per weather station could be visualised using box plots.

```python
# Visualise the precipitation ranges per weather station
b = df1.boxplot(by="station", column = ["prcp"], figsize = (15,8))
plt.xticks(rotation = 90)
plt.xlabel("Station", fontsize = 16)
plt.ylabel("Precipitation (in)", fontsize = 16)
plt.ylim(-0.1,2)
plt.title("")
plt.suptitle("")
plt.tight_layout()

# Visualise the temperature ranges per weather station
b = df1.boxplot(by="station", column = ["tobs"], figsize = (15,8))
plt.xticks(rotation = 90)
plt.xlabel("Station", fontsize = 16)
plt.ylabel("Temperature (°F)", fontsize = 16)
plt.ylim(50,100)
plt.title("")
plt.suptitle("")
plt.tight_layout()
```

The data was then grouped by `station id` and the means of precipitation, `prcp`, and temperature, `tobs`, were calculated.

```python
# Get averages for precipitation and observed temperature
grouped_df1 = df1.groupby("station").mean()
grouped_df1 = grouped_df1.reset_index()
```

A new query was created to determine the most active among the nine stations.

```python
# Select the columns for the analyses
sel2 = [Measurement.station, func.count(Measurement.station)]

# What are the most active stations? (i.e. what stations have the most rows)?
stn_count = session.query(*sel2).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

# Select the most active station (most number of measurements)
most_active_stn = stn_count[0][0]
```

Once the most active station was identified, the precipitation and temperature summary statistics (minimum, maximum, and average) for this station was determined, covering the last year of the database's records.

```python
# Calculate the minimum, average, and maximum temperature and precipitation in the most active station in the last year on record
sel3 = [func.min(Measurement.prcp), func.avg(Measurement.prcp), func.max(Measurement.prcp), 
        func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

summary_weather = session.query(*sel3).filter(Measurement.station == most_active_stn).\
filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

prcp_min = round(summary_weather[0][0], 1)
prcp_avg = round(summary_weather[0][1], 1)
prcp_max = round(summary_weather[0][2], 1)
temp_min = round(summary_weather[0][3], 1)
temp_avg = round(summary_weather[0][4], 1)
temp_max = round(summary_weather[0][5], 1)
```

### Precipitation in O'ahu for the last 12 months
To determine the mean daily precipitation levels, a query covering the last year in the database was created. This was then converted into a dataframe, and summary statistics were calculated by date.

```python
# Select the columns for the analyses
sel4 = [Measurement.date, Measurement.station, Measurement.prcp]

# Perform a query to retrieve the total observations and precipitation measurements
data = session.query(*sel4).filter(Measurement.date > year_ago).all()

# Save the query results as a Pandas DataFrame and set the index to the date column
df2 = pd.DataFrame(data)
df2 = df.sort_values("date", ascending = True) # Sort the dataframe by date
df2 = df.set_index("date")

# Use Pandas to calculate the summary statistics for precipitation
grouped = df2.groupby("date").describe()
```

The mean and the standard deviations were retained from the subsequent dataframe.

```python
# Use the mean and the standard deviations for precipitation
pptn_df = grouped["prcp"].iloc[:, 1:3]
```

The dates were in string format, hence, these needed to be converted to datetime in preparation for visualising precipitation in a timeseries plot. Since each date actually represented a period of one day, the dates were further converted to the period data type.

```python
# Data type of the date
pptn_df.index.values.dtype

# Date is currently set as string; need to convert to datetime and then to period format
# Resource: http://earthpy.org/time_series_analysis_with_pandas_part_2.html

pptn_df["mean"].index = pd.to_datetime(pptn_df["mean"].index) # string to datetime
pptn_df.index = pptn_df["mean"].to_period(freq = "D").index # time stamps to daily time periods
pptn_df.index
```

The timeseries plot was then generated.

```python
# Timeseries plot by a daily frequency
pptn_df.plot(y = "mean", figsize = (15,8), legend = False)
plt.xlabel("Date", fontsize = 16)
plt.ylabel("Average Precipitation", fontsize = 16)
plt.tight_layout()
plt.savefig("Images/pptn.svg")
plt.savefig("Images/pptn.png")
```

