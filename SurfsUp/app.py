# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime, timedelta
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare (autoload_with=engine)
# reflect the tables
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return jsonify({
        'Available Routes': [
            '/api/v1.0/precipitation',
            '/api/v1.0/stations',
            '/api/v1.0/tobs',
            '/api/v1.0/<start>',
            '/api/v1.0/<start>/<end>'
        ]
    })

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_year_date = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)

    # Query the last 12 months of precipitation data
    session = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year_date).all()
    
    # Convert results to a dictionary
    precipitation_data = {date: prcp for date, prcp in session}
    
    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    # Query all stations
    session = session.query(Station.station).all()
    
    # Convert results to a list
    stations_list = [station[0] for station in session]
    
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_year_date = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)

    # Query the most active station's temperature observations for the previous year
    active_station = 'USC00519281'  # Replace with logic to find the most active station if needed
    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == active_station,
        Measurement.date >= last_year_date
    ).all()

    # Convert results to a list of dictionaries
    tobs_list = [{'date': date, 'temperature': tobs} for date, tobs in results]
    
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def start(start):
    # Query the minimum, average, and maximum temperatures for dates >= start
    session = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    # Convert results to a dictionary
    temp_stats = {
        'TMIN': session[0][0],
        'TAVG': session[0][1],
        'TMAX': session[0][2]
    }
    
    return jsonify(temp_stats)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    # Query the minimum, average, and maximum temperatures for the date range
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert results to a dictionary
    temp_stats = {
        'TMIN': results[0][0],
        'TAVG': results[0][1],
        'TMAX': results[0][2]
    }
    
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)