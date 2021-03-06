import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)


# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f'<a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></br>'
        f'<a href="/api/v1.0/stations">/api/v1.0/stations</a></br>'
        f'<a href="/api/v1.0/tobs">/api/v1.0/tobs</a></br>'
        f'<a href="/api/v1.0/<start>">/api/v1.0/&ltstart&gt</a></br>'
        f'<a href="/api/v1.0/<start>/<end>">/api/v1.0/&ltstart&gt/&ltend&gt</a></br>'     
    )

#helper funcs
# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(from_date, to_date=None):
    session = Session(engine)
    if to_date == None:
        to_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= from_date).filter(Measurement.date <= to_date).all()

# function usage example
#print(calc_temps('2012-02-28', '2012-03-05'))

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a Dictionary using date as the key and prcp as the value."""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['prcp'] = prcp
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    # Query all passengers
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for id, station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation                
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """query for the dates and temperature observations from a year from the last data point"""
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
    # Query Measurements
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    start_date = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=366)

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start_date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for date, tobs in results:
        station_dict = {}
        station_dict["date"] = date
        station_dict["tobs"] = tobs
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/<start>/")
@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""

    results = calc_temps(start)
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for TMIN, TAVG, TMAX in results:
        station_dict = {}
        station_dict["TMIN"] = TMIN
        station_dict["TAVG"] = TAVG
        station_dict["TMAX"] = TMAX
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""

    results = calc_temps(start, end)
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for TMIN, TAVG, TMAX in results:
        station_dict = {}
        station_dict["TMIN"] = TMIN
        station_dict["TAVG"] = TAVG
        station_dict["TMAX"] = TMAX
        all_stations.append(station_dict)

    return jsonify(all_stations)



if __name__ == '__main__':
    app.run(debug=True)
