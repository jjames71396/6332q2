#Programming Assignment 2
#Jordan James 1001879608
#CSE 6332-002

import math
import pandas as pd
import os, uuid
from sqlalchemy import create_engine
import pymysql
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

query = '''SELECT *
    FROM cities
    '''

df = pd.read_csv(r"static\city.csv")

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

    
    df.to_sql('cities', con=engine, if_exists='replace',
           index_label='idx')
    
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
    for i,r in enumerate(df["State"]):
        if r == args[0] and int(df["Population"][i]) >= args[1] and int(df["Population"][i]) <= args[2]:
            print(df["Population"][i])
            df["Population"][i] = int(df["Population"][i])+  args[3]
            print(df["Population"][i])
            
    
    df.to_sql('cities', con=engine, if_exists='replace',
           index_label='idx')
    
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
    f = float(results["lat"])
    l = float(results["lon"])
    
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
