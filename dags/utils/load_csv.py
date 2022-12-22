import pandas as pd
import mysql.connector as msql
from mysql.connector import Error
import json

def fn_load_csv():
    people_df = pd.read_csv('/usr/local/airflow/dags/data/people.csv', index_col=False, delimiter = ',')
    places_df = pd.read_csv('/usr/local/airflow/dags/data/places.csv', index_col=False, delimiter = ',')

    try:
        conn = msql.connect(host='database', user='codetest',  database='codetest',
                            password='swordfish')
        if conn.is_connected():
            cursor = conn.cursor()
            #loop through the data frame
            for i,row in people_df.iterrows():
                #here %S means string values 
                sql = "INSERT INTO people(given_name,family_name,date_of_birth,place_of_birth) VALUES (%s,%s,%s,%s)"
                cursor.execute(sql, tuple(row))
                print("Record inserted to people")
            for i,row in places_df.iterrows():
                #here %S means string values 
                sql = "INSERT INTO places(city,county,country) VALUES (%s,%s,%s)"
                cursor.execute(sql, tuple(row))
                print("Record inserted to places")
            # the connection is not auto committed by default, so we must commit to save our changes
            conn.commit()
        sql_query = pd.read_sql_query ('''
                                        select pl.country country,count(p.given_name) TotalCount
                                        from people p join places pl 
                                        on p.place_of_birth=pl.city 
                                        group by pl.country
                               ''', conn)
        df = pd.DataFrame(sql_query, columns = ['country','TotalCount'])
        out = json.loads(df.to_json(orient='values'))
        jsonData = {};
        totl=len(out)
        for k in range(totl):
            jsonData[out[k][0]] = out[k][1];
        with open('/usr/local/airflow/dags/output/summary_output.json', 'w') as f:
            f.write(json.dumps(jsonData))
    except Error as e:
        print("Error while connecting to MySQL", e)