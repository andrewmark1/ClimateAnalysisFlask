# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 18:35:18 2019

@author: Andrew
"""
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

engine = create_engine("sqlite:///resources/hawaii.sqlite", connect_args={'check_same_thread':False})

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

data_start_date = session.query(Measurement).order_by(Measurement.date).first()
data_end_date = session.query(Measurement).order_by(Measurement.date.desc()).first()

query_beg = dt.datetime.strptime(data_end_date.date,'%Y-%m-%d') - dt.timedelta(days=366)

app = Flask(__name__)

@app.route("/")
def home():
    return("<h1> List of all available api routes: </h1>\
           <ul>\
               <li> <strong> /api/v1.0/precipitation: </strong> Convert query results to a dictionary using date as the key and prcp as the value; returns a JSON </li>\
               <li> <strong> /api/v1.0/stations: </strong> Returns a JSON list of stations from the dataset </li>\
               <li> <strong> /api/v1.0/tobs: </strong> Query the dates and temperature observations from a year from the last data point </li>\
               <li> <strong> /api/v1.0/start: </strong> Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date </li>\
               <li> <strong> /api/v1.0/start/end: </strong> Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start and end date </li>\
           </ul>"
          )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    precip_list = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict['Date'] = date
        precip_dict['Precipitation'] = prcp
        precip_list.append(precip_dict)
    
    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station, Station.name, Station.latitude, \
               Station.longitude, Station.elevation).all()

    station_list = []
    for station, name, lat, long, elev in results:
        station_dict = {}
        station_dict['Station'] = station
        station_dict['Name'] = name
        station_dict['Latitude'] = lat
        station_dict['Longitude'] = long
        station_dict['Elevation'] = elev
        station_list.append(station_dict)
    
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_beg).order_by(Measurement.date).all()
    
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['Date'] = date
        tobs_dict['Temperature'] = tobs
        tobs_list.append(tobs_dict)
        
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def temp_start(start):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
   
    temp_start_dict = {'Min Temperature': results[0][0],
                       'Avg Temperature': results[0][1],
                       'Max Temperature': results[0][2] 
                      }
    
    return jsonify(temp_start_dict)
    
@app.route('/api/v1.0/<start>/<end>')
def temp_start_end(start, end):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()
   
    temp_start_end_dict = {'Min Temperature': results[0][0],
                       'Avg Temperature': results[0][1],
                       'Max Temperature': results[0][2] 
                      }
    
    return jsonify(temp_start_end_dict)



if __name__ == "__main__":
    app.run(debug=True)