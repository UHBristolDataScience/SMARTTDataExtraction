import pyodbc
import json
import pandas as pd
import streamlit as st
from st_pages import hide_pages
import sqlite3


# TODO: add to class that is only instantiated once?
def _hide_pages():
    with open("config.json", 'r') as infile:
        config = json.load(infile)

    hide_pages(config["hide_pages"])


# TODO: migrate to better/newer SQLAlchemy (avoid warning):
#  https://stackoverflow.com/questions/71082494/getting-a-warning-when-using-a-pyodbc-connection-object-with-pandas
def run_query(sql, db=None, server=None, connection_timeout=15, query_timeout=90):

    tc = "yes"
    cnxn = pyodbc.connect(
        'trusted_connection=' + tc
        + ';DRIVER={SQL Server};SERVER=' + server
        + ';DATABASE=' + db
        + ';timeout=%d' % connection_timeout)

    cnxn.timeout = query_timeout
    data = pd.read_sql(sql, cnxn)

    return data


class LocalDatabaseWrapper:
    """
    Wrapper to handle interaction with local database (currently Sqlite).
    """

    def __init__(self, database_path):

        self.path = database_path
        self._test()

    def connect(self):
        return sqlite3.connect(self.path)

    def _test(self):
        # try:
            self.connect()
        # except:

    def query_pd(self, sql):
        return pd.read_sql_query(sql, self.connect())

    def enter_df(self, df, name, if_exists='fail', index=False, index_label=None):
        df.to_sql(
            name,
            self.connect(),
            if_exists=if_exists, index=index,
            index_label=index_label
        )

    def insert_query(self, sql):
        con = self.connect()
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        con.close()


def initial_fact_table_query(table='PtLabResult', table_type_id=23, clinical_unit_ids=[5, 8, 9]):
    unit_string = ", ".join(f"{x}" for x in clinical_unit_ids)

    return f"""
        SELECT
            table1.interventionId, MIN(table1.shortLabel) as shortLabel, MIN(table1.longLabel) as longLabel, MIN(table1.conceptCode) as conceptCode, 
            COUNT(P.encounterId) as numberOfPatients, MIN(P.chartTime) as firstChartTime, MAX(P.chartTime) as lastChartTime, 
            COUNT(P.chartTime) as numberOfRecords, min(P.clinicalUnitId) as minClinicalUnitId, max(P.clinicalUnitId) as maxClinicalUnitId
        FROM (
        SELECT * FROM D_Intervention where tableTypeId = {table_type_id}
        ) as table1
        RIGHT JOIN (
        Select * from {table} as t WHERE t.clinicalUnitId in ({unit_string})
        ) as P
        ON table1.interventionId = P.interventionId
        GROUP BY table1.interventionId;
    """
