#!/usr/bin/env python
# coding: utf-8

"""
    File name: index.py
    Use: index from where to build the app (app.py) and other pages.
    Author: Lutecity (Melanie Baconnais & Chloe Gobe) 
    Date created: 04/2023
    Python Version: 3.10.4
"""

##############################################################
#                       IMPORTS
##############################################################
#_____________________________________________________________
# 3-RD PARY LIBRARIES
# DASH
import dash
import dash_bootstrap_components as dbc 

##############################################################
#                  DASH IMPLEMENTATION
##############################################################
FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

app = dash.Dash(__name__,
                title='Man City App',
                update_title='Loading ...',
                external_stylesheets = [dbc.themes.BOOTSTRAP, FA],
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])
                
server = app.server 
