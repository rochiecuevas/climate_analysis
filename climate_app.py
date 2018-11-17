#################################################
# Dependencies
#################################################

# Package for handling time data
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct

from flask import Flask, request, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo = False)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Establish the dates for the last year on record
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

first_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()[0]

year_ago = dt.date(int(last_date[0:4]), int(last_date[5:7]), int(last_date[8:10])) - dt.timedelta(days = 365)

# Create a list of dates
dates = session.query(Measurement.date).all()
date_list = [row[0] for row in dates]
session.close()

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the climate app! Today we explore precipitation and \
        temperature in Oahu, HI.<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<startdate><br/>"
    )


@app.route("/api/v1.0/stations")
def stns():
    """Returns a list of weather stations."""
    # Query information about the weather stations
    sel = [Measurement.station, Station.name, Station.elevation, 
           Station.latitude, Station.longitude]

    results = session.query(*sel).filter(Measurement.station == Station.station).group_by(Measurement.station).all()
    
    # Organise query object contents into a nested dictionary
        # Main dictionary key is row[0], which contains station ids
        # Subdictionary keys are: 
            # row[1], station name
            # row[2], station elevation
            # row[3], latitude
            # row[4], longitude
    stations = []
    all_stns = {}
    for row in results:
        if row[0] not in all_stns:
            all_stns[row[0]] = {}
            all_stns[row[0]]["name"] = row[1]
            all_stns[row[0]]["elevation"] = row[2]
            all_stns[row[0]]["lat"] = row[3]
            all_stns[row[0]]["lng"] = row[4]
    stations.append(all_stns)
    
    return jsonify(stations)
    session.close()    


@app.route("/api/v1.0/tobs")    
def tobs():
    """Returns observed temperature records for 1 year from the last record."""

    # Query the database for records
    sel = [Measurement.date, Measurement.station, Measurement.tobs]
    
    results = session.query(*sel).filter(Measurement.date > year_ago).all()

    temp_dict = {}
    for row in results:
        if row[0] not in temp_dict:
            temp_dict[row[0]] = {}
        temp_dict[row[0]][row[1]] = row[2]

    temps_list = [temp_dict]        
    
    return jsonify(temps_list)
    session.close() 
    
@app.route("/api/v1.0/precipitation")
def rain():
    """Returns precipitation results for 1 year from the last record."""

    # Query all precipitation data
    results = session.query(Measurement.date, Measurement.station, Measurement.prcp).order_by(Measurement.date).filter(Measurement.date > year_ago).all()
    
    # Organise query object contents into a nested dictionary
        # Main dictionary key is row[0], which contains dates
        # Subdictionary keys are in row[1], which contains station ids
        # Values are in row[2], which contains precipitation records  
    rain = []
    prcp_dict = {}
    for row in results:
        if row[0] not in prcp_dict:
            prcp_dict[row[0]] = {}
        prcp_dict[row[0]][row[1]] = row[2]
    rain.append(prcp_dict)
        
    return jsonify(rain)      
    session.close()     


@app.route("/api/v1.0/<startdate>") 
def weather_reports(startdate):
    if startdate not in date_list:
        return(f"You need to select a valid date. It has to be on or after {first_date}.")
    else:
        # Query the results from the startdate to the last date on record
        sel = [func.min(Measurement.prcp), func.avg(Measurement.prcp), func.max(Measurement.prcp), func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        
        results = session.query(*sel).filter(Measurement.date >= startdate).all()

        # Create a dictionary containing the results
        weather_dict = {}            
        for row in results:
            weather_dict["date_01"] = startdate
            weather_dict["date_02"] = last_date
            weather_dict["tempF_min"] = round(row[3], 2)
            weather_dict["tempF_avg"] = round(row[4], 2)
            weather_dict["tempF_max"] = round(row[5], 2)               
            weather_dict["precipitation_min"] = round(row[0], 2)
            weather_dict["precipitation_avg"] = round(row[1], 2)
            weather_dict["precipitation_max"] = round(row[2], 2)
        weather_list = [weather_dict]    
        
        return jsonify (weather_list)
        session.close()

@app.route("/api/v1.0/<startdate>/<enddate>") 
def weather_reports2(startdate, enddate):
    
    # Check if the startdate is in the date_list
    if startdate not in date_list:
        return(f"You need to select a valid date. It has to be on or after {first_date}.")
    else:
        if enddate not in date_list:
            return(f"You need to select a valid date. It has to be on or before {last_date}.")   
        else:
            if enddate < startdate:
                return ("Your vacation cannot end before it starts. Pick another end date.")
            else:
                # List the variables that will be queried
                sel = [func.min(Measurement.prcp), func.avg(Measurement.prcp), func.max(Measurement.prcp), func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

                # Query the weather data for the range set by the start and the end dates
                results = session.query(*sel).filter(Measurement.date >= startdate).filter(Measurement.date <= enddate).all()

                # Create a dictionary containing the results
                weather_dict = {}
                for row in results:
                    weather_dict["date_01"] = startdate
                    weather_dict["date_02"] = enddate
                    weather_dict["tempF_min"] = round(row[3], 2)
                    weather_dict["tempF_avg"] = round(row[4], 2)
                    weather_dict["tempF_max"] = round(row[5], 2)
                    weather_dict["precipitation_min"] = round(row[0], 2)
                    weather_dict["precipitation_avg"] = round(row[1], 2)
                    weather_dict["precipitation_max"] = round(row[2], 2)
                weather_list = [weather_dict]    

                return jsonify (weather_list)    
                session.close()