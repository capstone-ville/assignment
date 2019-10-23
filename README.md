# assignment

This repo is for the Coursera assignment Capstone Project - The Battle of Neighborhoods.

*A description of the problem and a discussion of the background. (15 marks)*

Introduction/Business Problem

A boutique hotel located in Madrid, Spain would like to open up a new hotel in Paris, France. One of the key aspects that their clients value is the various types of services nearby the hotel area - restaurants, bars, cafes, gyms etc. Knowing that, the hotel owners would like to see if there's a similar type of area in Paris to settle down to.

*A description of the data and how it will be used to solve the problem. (15 marks).*

For comparing two different areas in two different cities from two different countries there are a couple of items that need to be resolved. Firstly, a list of neighbourhoods needs to be found. Wikipedia is often a good source for this, however the format the information is provided can be a bit different between different pages. Python can scrape the tables listing the areas. Secondly, to determine the coordinates, Geopy can be used to fetch this information based on the names of the areas. Thirdly, the Foursquare API can be used to find the venues in each area and then k-means clustering can be used to identify similar areas. Finally the areas can be visualized by using Folium so that the stakeholders can review the outcome in a sensible format.

More details how it is done in practice is in the file assignment.py.
