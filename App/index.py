#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
# 3RD-PARTY LIBRARIES
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

#_____________________________________________________________
# LOCAL LIBRAIRIES
from app import app
import pages
server = app.server


##############################################################
#                       APP LAYOUT
##############################################################
app.layout = html.Div(
   [
      dcc.Location(id='url'),
      # Navbar(),   
      html.Div(id = 'page-content')
   ]
)

##############################################################
#                       DATA CONTROL
##############################################################
# . . . . . . . . . . . . . . . . .. . . . . . . . . . . . . . 
# - - - - - - - - - - - APP.py - - - - - - - - - - - - -

#_____________________________________________________________
#BASED ON THE PAGE TO DISPLAY, CHANGE THE LAYOUT 
@app.callback(
   Output(component_id = 'page-content', component_property = 'children'),
   [
      Input(component_id = 'url', component_property = 'pathname')
   ]
)
def display_page(pathname):
   page_name = app.strip_relative_path(pathname)
   if not page_name:
      return pages.match_analysis.match_analysis()
   else : 
      return 0


@app.callback(
   Output(component_id = 'match-analysis-link', component_property = 'active'),
   [
      Input(component_id = 'url', component_property = 'pathname')
   ]
)
def set_page_active(pathname):
   if pathname =="/" :
      return True
      

if __name__ == '__main__':
    app.run_server(debug=True)