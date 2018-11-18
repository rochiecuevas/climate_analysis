# What's the weather like in O'ahu, HI?

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

The total daily precipitation across weather stations were calculated and used for the timeseries plot.

```python
# Use the mean and the standard deviations for precipitation
pptn_df = df2.groupby("date").sum()
```

The dates were in string format, hence, these needed to be converted to datetime in preparation for visualising precipitation in a timeseries plot. Since each date actually represented a period of one day, the dates were further converted to the period data type.

```python
# Data type of the date
pptn_df.index.values.dtype

# Date is currently set as string; need to convert to datetime and then to period format
# Resource: http://earthpy.org/time_series_analysis_with_pandas_part_2.html

pptn_df["prcp"].index = pd.to_datetime(pptn_df["prcp"].index) # string to datetime
pptn_df.index = pptn_df["prcp"].to_period(freq = "D").index # time stamps to daily time periods
pptn_df.index
```

The timeseries plot was then generated.

```python
# Timeseries plot by a daily frequency
pptn_df.plot(y = "prcp", figsize = (15,8), legend = False)
plt.xlabel("Date", fontsize = 16)
plt.ylabel("Daily Precipitation (in)", fontsize = 16)
plt.tight_layout()
plt.savefig("Images/pptn.svg")
plt.savefig("Images/pptn.png")
```

However, the pattern was not very clear when viewed at a daily basis. To determine monthly patterns, the mean was recalculated from the data resampled on a monthly basis.

```python
# Get the mean by month
pptn_df_monthly_avg = pptn_df.iloc[:, 0:1].resample("M").mean() 
```

This could then be viewed in a line chart in which the x-axis contained the months and the y-axis contained the precipitation levels. A trendline and its equation were displayed to show patterns in precipitation over time.

```python
# Monthly precipitation averages for one year
x = np.arange(len(pptn_df_monthly_avg.index))
y = pptn_df_monthly_avg["prcp"].values
plt.figure(figsize = (15,8))
plt.plot(x, y, marker = "o", markersize = 12, color = "red")

# Calculate the trendline (linear fitting)
# Resource: http://widu.tumblr.com/post/43624347354/matplotlib-trendline
z = np.polyfit(x, y, 1) 
p = np.poly1d(z)
plt.plot(x, p(x),"b--")

# the line equation:
equation = (f"y = %.3fx + %.3f"%(z[0],z[1]))

# Plot attributes
plt.text(-0.55,0.22, equation, fontsize = 16)
plt.ylabel("Average Precipitation", fontsize = 16)
plt.xlabel("Month", fontsize = 16)
plt.xticks(x, pptn_df_monthly_avg.index.values, rotation = 45)
plt.tight_layout()
plt.savefig("Images/pptn_monthly_avg.svg")
plt.savefig("Images/pptn_monthly_avg.png")
```

To get more information about precipitation patterns, a kernel distribution plot, overlaid with a rug plot, was generated.

```python
# Precipitation distribution
plt.figure(figsize = (15,8))
sns.distplot(pptn_df["prcp"], kde = True, hist = False, rug = True,
             kde_kws = {"shade": True, "linewidth": 3},
             rug_kws = {"color": "black"})
plt.xlabel("Precipitation (in)", fontsize = 16)
plt.ylabel("Density", fontsize = 16)
plt.tight_layout()
plt.savefig("Images/density_precipitation.svg")
plt.savefig("Images/density_precipitation.png")
```

### Temperature records in O'ahu for the last 12 months
The same approach in converting the dates from string to datetime and then to period type was conducted. Instead of getting temperature sums (which is essentially meaningless), daily and monthly average temperatures were obtained. The daily temperature average from the nine weather stations were plotted in a timeseries while the monthly average was plotted in a histogram. It must be noted, however, that histograms might not show a good story because the data analyst plugs in the number of bins.

```python
# Plot the temperature in a histogram
# NB: Histograms use arbitrarily set number of bins, which affects the shape of the distribution
plt.figure(figsize = (15,8))
plt.hist(tobs_df["mean"], bins = 50, edgecolor = "black")
plt.xlabel("Temperature (°F)", fontsize = 16)
plt.ylabel("Frequency", fontsize = 16)
plt.xlim(60, 85)
plt.tight_layout()
plt.savefig("Images/hist_temp.svg")
plt.savefig("Images/hist_temp.png")
```

Hence, the data was also plotted as a kernel density plot overlaid with a rug plot. The rug plot shows where each point lies on the x-axis. The thicker the band, the higher the kernel density. 

### Is there a relationship between temperature, precipitation, and location of weather stations?
Because temperature and precipitation *might* be associated with a weather station's location (latitude, longitude, and elevation in this case), the different variables were plotted into scatterplots to visualise any correlations.

```python
# Create a scatterplot matrix to show relationships among the environmental variables
sns.set(font_scale = 1.25)
g = sns.pairplot(grouped_df1, diag_kind = "kde", diag_kws = dict(shade = True))
plt.tight_layout()
plt.savefig("Images/scatter_matrix_envi.svg")
plt.savefig("Images/scatter_matrix_envi.png")
```

### Weather conditions during selected date ranges
To be able to choose the dates, I opted to use inputs in while loops. This allowed me to do a few things:
1. Validate the start and the end dates (i.e., February 29th is only valid in a leap year)
2. Check if I get the order of the dates right (i.e., A date range cannot end before it begins)
3. Check if the dates I chose were included in the database (i.e., The range should be between January 1, 2010 and August 23, 2017)

```python
# Personal vacation dates, use while loops to make sure that entries are valid.
while True:
    print("What is the start date of your vacation? (yyyy-mm-dd)")
    vac_start = input()

    if vac_start not in list(df3["date"]):
        print("Please try again. Date is not in the list.\nFollow this format (yyyy-mm-dd): 2016-02-29\n")
    else:
        break

while True:        
    print("What is the end date of your vacation? (yyyy-mm-dd)")
    vac_end = input()
        
    if vac_end not in list(df3["date"]):
        print("Please try again. Follow this format (yyyy-mm-dd): 2016-02-29")
    else:
        break

while vac_start > vac_end:
    print("\nYour vacation cannot end before it started! Please try again.")
    
    print("What is the end date of your vacation? (yyyy-mm-dd)")
    vac_end = input()

print("Calculating....")
```

Once the dates were validated and accepted by the program, the temperature and precipitation summaries in the date range indicated were retrieved through a session query function called `calc_temps`.

```python
# This function called `calc_temps` will accept start date and end date in the format 
# '%Y-%m-%d' and return the minimum, average, and maximum temperatures for that range of dates
def calc_weather(start_date, end_date):
    """TMIN, TAVG, and TMAX, PMIN, PAVG, and PMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVG, and TMAX, PMIN, PAVG, and PMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs),
                         func.min(Measurement.prcp), func.avg(Measurement.prcp), func.max(Measurement.prcp)).filter(Measurement.date >= start_date).\
                         filter(Measurement.date <= end_date).all()
```

The summary temperature statistics could be plotted as a bar graph, with the bar height representing the average temperature and the y-error bar representing the difference between the maximum and minimum values.

```python
# Calculate the weather statistics
summary_vac_weather = calc_weather(vac_start, vac_end)

# Plot the temperature statistics as a bar plot
yerr = summary_vac_weather[0][2] - summary_vac_weather[0][0]

plt.figure(figsize = (15,8))
plt.bar(1, summary_vac_weather[0][1], yerr = yerr)
plt.xlim(0,2)
plt.ylabel("Temperature (°F)")
```

However, if<br><br>
Temp<sub>ave</sub> ≠ Temp<sub>max</sub> - Temp<sub>min</sub><br><br>
Then using the difference between Temp<sub>max</sub> and Temp<sub>min</sub> might not be appropriate. It is better to visualise the temperature using a box plot.

```python
# Plot the results from your previous query as a box plot.
vacation_temp = session.query(Measurement.tobs).\
                         filter(Measurement.date >= vac_start).\
                         filter(Measurement.date <= vac_end).all()

# Create a list of temperatures recorded during the vacation period
temps = [temp[0] for temp in vacation_temp]

# Create box plot to show range of temperatures recorded during the vacation period
plt.figure(figsize = (15,8))
plt.boxplot(temps, showmeans = True)
plt.ylabel(f"Temperature (°F)", fontsize = 16)
plt.title(f"Temperature range during the vacation period, {vac_start} to {vac_end}", fontsize = 16)
plt.savefig("Images/box_temperature_vacation.svg")
plt.savefig("Images/box_temperature_vacation.png")
```

The total rainfall per weather station during the selected date range was queried and placed in a dataframe.

```python
# Calculating total rainfall during the vacation using SQLAlchemy
sel5 = [Measurement.station, Station.name, 
        func.sum(Measurement.prcp).label("rainfall_sum"), 
        Station.elevation, Station.latitude, Station.longitude]

vac_rainfall = session.query(*sel5).filter(Measurement.station == Station.station).  filter(Measurement.date >= vac_start).      filter(Measurement.date <= vac_end).        group_by(Measurement.station).             order_by(func.sum(Measurement.prcp).desc()).all()

pd.DataFrame(vac_rainfall)
```

The daily normals (i.e., the average, minimum, and maximum values per day across years) was also calculated for the selected period using the function `daily_normals`. But because the function accepted month-day combinations, the dates had to be reformatted first.

```python
# Use the start and end date to create a range of dates
dates = session.query(Measurement.date).     filter(Measurement.date >= vac_start).filter(Measurement.date <= vac_end).group_by(Measurement.date).all()

# List of dates
date_range = [date[0] for date in dates]

# Strip off the year and save a list of %m-%d strings
mm_dd_range = [date[5:10] for date in date_range]
```

And then the function was used.
```python
def daily_normals(date):
    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()
```

This function was looped through the elements in the list of dates (converted to month-day format).

```python
# Loop through the list of %m-%d strings and calculate the normals for each date
normals_lst = [daily_normals(mm_dd) for mm_dd in mm_dd_range]
normals = [item[0] for item in normals_lst]
```

The data was then loaded into a dataframe and subsequently plotted into an area plot.

```python
# Plot the daily normals as an area plot with `stacked=False`
x = np.arange(0,len(normal_df))

normal_df.plot.area(stacked = False, alpha = 0.5, figsize = (15,8))
plt.xlabel("Date", fontsize = 16)
plt.ylabel("Temperature (°F)", fontsize = 16)
plt.xticks(x, mm_dd_range, rotation = 45)
plt.legend(fontsize = 16)
plt.tight_layout()
plt.savefig("Images/area_temp_vacation.svg")
plt.savefig("Images/area_temp_vacation.png")
```