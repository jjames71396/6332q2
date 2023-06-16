#Programming Assignment 2
#Jordan James 1001879608
#CSE 6332-002

import math
import pandas as pd
import os, uuid
from sqlalchemy import create_engine
import pymysql
from sqlalchemy import create_engine, update, MetaData, Table
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)

# Setting up initial parameters
typ = "'earthquake'"
r = 5000
f = 40
l = 1
ns = r/111        # North-south distance in degrees (69 for miles, 111 for km)
ew = ns / math.cos(f) # East-west distance in degrees
sf = f-ns
nf = f+ns
wl = l-ew
el = l+ew

# Setting up database connection parameters
server = 'q2server.mysql.database.azure.com'
database = 'testdb'
username = 'servadmin'
password = '#hackme123'
port = '3306'

engine = create_engine(
    f"mysql+pymysql://{username}:{password}@{server}:{port}/{database}",
    connect_args={"ssl": {"ssl_ca": "DigiCertGlobalRootCA.crt.pem"}},
)

path = "static"
download_file_path = os.path.join(path, "city.csv")
df = pd.read_csv(download_file_path)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/location', methods=['POST'])
def location():
    # Retrieving data from the request form
    arg = request.form.get('name')
    args = arg.split(',')
    
    sf = float(args[0])
    nf = float(args[2])
    wl = float(args[1])
    el = float(args[3])
    
    # SQL query to retrieve earthquakes within the specified boundaries
    query = '''SELECT *
    FROM cities
    WHERE lat BETWEEN {} AND {}
    AND
    lon BETWEEN {} AND {}
    '''
        
    
    # Executing the SQL query based on different boundary scenarios
    if sf < nf and el < wl:
        result = pd.read_sql_query(query.format(sf,nf,el,wl, typ), engine)
    elif sf < nf and wl < el:
        result = pd.read_sql_query(query.format(sf,nf,wl,el, typ), engine)
    elif nf < sf and wl < el:
        result = pd.read_sql_query(query.format(nf,sf,wl,el, typ), engine)
    elif nf < sf and el < wl:
        result = pd.read_sql_query(query.format(nf,sf,el,wl, typ), engine)          
        
    # Rendering the template with the query result
    if result is not None:
       return render_template('count.html', name = len(result), tables=[result.to_html(classes='data', header="true")])
    else:
       print('Request for count page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

@app.route('/range', methods=['POST'])
def range():
    # Retrieving data from the request form
    result = None
    arg = request.form.get('name')
    args = arg.split(',')
    args[2] = int(args[2])
    args[3] = float(args[3])
    args[4] = float(args[4])
    df.loc[len(df.index)] = args

    # Define the data for the new record as a dictionary
    new_record = {
        'City': args[0],
        'State': args[1],
        'Population': args[2],
        'lat': args[3],
        'lon': args[4]
    }

    # Convert the dictionary into a DataFrame
    ins = pd.DataFrame([new_record])

    # Insert the record into the database
    table_name = 'cities'
    ins.to_sql(table_name, con=engine, if_exists='append', index=False)
    
    # Rendering the template with the query result
    if result is not None:
       return render_template('count.html', name = len(result), tables=[result.to_html(classes='data', header="true")])
    else:
       print('Request for count page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))
       
@app.route('/increment', methods=['POST'])
def increment():
    # Retrieving data from the request form
    result = None
    arg = request.form.get('name')
    args = arg.split(',')
    args[1] = int(args[1])
    args[2] = int(args[2])
    args[3] = int(args[3])
    query = '''SELECT *
    FROM cities
    WHERE Population BETWEEN {} AND {}
    '''
    
    # Table name, field to increment, and population range
    metadata = MetaData(bind=engine)
    table_name = 'cities'
    table = Table(table_name, metadata, autoload=True)
    field_to_increment = 'Population'
    min_population = args[1]
    max_population = args[2]

    # Construct the update query
    stmt = (
        update(table)
        .where(table.c.Population.between(min_population, max_population))
        .values({field_to_increment: table.c.Population + args[3]})  
    )

    # Execute the update query
    with engine.begin() as connection:
        connection.execute(stmt)
    
    # Rendering the template with the query result
    if result is not None:
       return render_template('count.html', name = len(result), tables=[result.to_html(classes='data', header="true")])
    else:
       print('Request for count page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

@app.route('/count', methods=['POST'])
def count():
    # SQL query to retrieve earthquakes of a specific type and magnitude greater than a threshold
    query = '''SELECT *
    FROM cities
    WHERE City = {}
    '''
    result = None
    arg = request.form.get('name')
    arg = "'" + arg + "'"
    results = pd.read_sql_query(query.format(arg), engine)
    r = float(100)
    print(results["lat"])
    if len(results["lat"]) < 2:
        f = float(results["lat"])
        l = float(results["lon"])
    else:
        f = float(results["lat"][0])
        l = float(results["lon"][0])
    
    ns = r/111        # North-south distance in degrees (69 for miles, 111 for km)
    ew = ns / math.cos(f) # East-west distance in degrees
    sf = f-ns
    nf = f+ns
    wl = l-ew
    el = l+ew
    
    query = '''SELECT *
    FROM cities
    WHERE lat BETWEEN {} AND {}
    AND
    lon BETWEEN {} AND {}
    '''
    
    # Executing the SQL query based on different boundary scenarios
    if sf < nf and el < wl:
        result = pd.read_sql_query(query.format(sf,nf,el,wl, typ), engine)
    elif sf < nf and wl < el:
        result = pd.read_sql_query(query.format(sf,nf,wl,el, typ), engine)
    elif nf < sf and wl < el:
        result = pd.read_sql_query(query.format(nf,sf,wl,el, typ), engine)
    elif nf < sf and el < wl:
        result = pd.read_sql_query(query.format(nf,sf,el,wl, typ), engine) 
    
    # Rendering the template with the query result
    if result is not None:
       return render_template('count.html', name = len(result), tables=[results.to_html(classes='data', header="true")], tabs =[result.to_html(classes='data', header="true")])
    else:
       print('Request for count page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

if __name__ == '__main__':
   app.run()
