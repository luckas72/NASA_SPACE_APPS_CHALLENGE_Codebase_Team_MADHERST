# -*- coding: utf-8 -*-
# author: ZJendex
# place: Boston Amherst
# last update: Oct/3/2021

import numpy as np
import netCDF4 as nc
from geopy.geocoders import Nominatim
import os


def restructure(country_map):
    """
    country_map  (list) : a list of country names
    """

    directory_in_file = [
        ncfile
        for ncfile in os.listdir()
        if (ncfile.__contains__(".nc") or ncfile.__contains__(".nc4"))
    ]
    datasets = [  # Open up multiple nc4 files to be read-in and to be restructured
        nc.Dataset(ncfile, "r") for ncfile in directory_in_file
    ]  # Change to support multiple files

    # Just a constant look up table
    var_to_use = [
        "TSOIL1",
        "TSOIL2",
        "TSOIL3",
        "TSOIL4",
        "TSOIL5",
        "TSOIL6",
        "LHLAND",
        "Var_LHLAND",
        "PRECSNOLAND",
        "Var_PRECSNOLAND",
        "PRMC",
        "Var_PRMC",
        "QINFIL",
        "Var_QINFIL",
        "SMLAND",
        "Var_SMLAND",
    ]
    # A data structure to be mapped by a country
    varmap = {key: [] for key in var_to_use}  # {var_to_use : [] # parrallel file list}
    # Auxiliar data structure

    coun_varmap = {
        country: varmap for country in country_map
    }  # Main structure to map the datapoints by country ranking in parallelism

    for dataset in datasets:
        # Get latitude and longtitude points
        lat_list = np.array(dataset.variables["lat"]).tolist()
        lon_list = np.array(dataset.variables["lon"]).tolist()

        # Numpy object list to reduce traverse through the datasets
        np_obj_lis = {
            var_name: np.array(dataset.variables[var_name]).reshape(361, 576)
            for var_name in var_to_use
        }

        print("About to get the files data")
        # Map the usefull variable value by lat,lon, if lat,lon happens to be a country then will return an object.
        # If it happens to be an unclaimed territory, then it will return None
        for i in range(len(lat_list)):
            for j in range(len(lon_list)):
                # initialize Nominatim API to get territoty information
                geolocator = Nominatim(user_agent="NASA app")
                la = str(lat_list[i])
                lo = str(lon_list[j])
                location = geolocator.reverse(la + "," + lo)
                if location == None:  # None means that there isn't any country
                    # print("inside location condition")
                    continue

                # print("Got location")
                address = location.raw["address"]
                country_name = address.get("country", "")
                country_name = country_name.upper()
                if country_name in country_map:
                    print("mapping to country")
                    for var in np_obj_lis:
                        coun_varmap[country_name][var].append(np_obj_lis[var][i][j])

        print("Finished getting data")

    return coun_varmap

    # Data needed to upload to Kintone