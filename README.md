# Market Tracker

Shiny for python application to show historical performance of select stocks.

This project grew out of a desire to compare stocks I currently own in a single view. Most sites
require a user to navigate back and forth between different stocks to compare performance. I didn't want to write down numbers and click back and forth when doing research so I created a dashboard to display the information in the format I wanted.

The dashboard utilizes the stock API [Alphavantage](https://www.alphavantage.co/). I came across a lot of different stock market APIs when researching this project. The Alphavantage API provided the best free tier for my use case.

## Shiny for python

The project started as a data gathering problem with various APIs and storing the data using SQLite. I wanted a way to display the data and ended up exploring [Shiny for Python](https://shiny.posit.co/py/). Having used Shiny for R extensively I thought it would be fun to explore the much newer Shiny for Python framework. Things were a little clunky for me at first as I adapted to the different syntax styles, but eventually got used to it. Python offers a more robust web server in Univorn than the R side.

## Future work
I plan to host this on shinyapps.io so I can take better advantage of the information in it. I would also like to explore the Shiny side of the project more and see how the framework develops with future releases. 

