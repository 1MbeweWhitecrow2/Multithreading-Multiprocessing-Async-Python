# Multithreading-Multiprocessing-Async-Python
Repository contains python scripts that include multithreading, multiprocessing and async programming.


To run script, first, You have to create .env file in Your folder.

.env file should contain:

ALPHAVANTAGE_API_KEY=YOUR_KEY
PGHOST=localhost
PGPORT=5432
PGUSER=YOUR_PG_USER
PGPASSWORD=YOUR_PG_PASSWORD
PGDATABASE=NAME_OF_PG_DATABASE

You can test your PostgreSql connection, by running test_postgres.py file.

fetch_info.py is responsible for getting short company description from official
CocaCola website.

fetch_logo.py is responsible for getting CocaCola logo from wikipedia.

fetch_price.py is responsible for getting CocaCola stock prices by AlphaVantage API.

coca_fetchers.py allows You to run above three request concurrently, utilizing threading, making
those three requests on separate threads each. By uncommenting code at the bottom of the file, 
You can test if script run properly. 

pipeline_async.py is a main file of repository, that lets You run full process. At first, script runs coca_fetchers.py,
running on 3 separate threads. Then, script utilize asynchronous programming and multithreading to: create .txt file 
with company description, save time series data to postgresql and create .html file, containing CocaCola stock price chart.
Each output is created on separate process and utilize asyncio library to implement asynchronous programming.
