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

    def enter_df(self, df, name, if_exists='fail', index=False):
        df.to_sql(
            name,
            self.connect(),
            if_exists=if_exists, index=index
        )


assessment_initial_query = """
    SELECT
        table1.interventionId, MIN(table1.shortLabel) as shortLabel, MIN(table1.longLabel) as longLabel, MIN(table1.conceptCode) as conceptCode, 
        COUNT(P.ptAssessmentId) as numberOfPatients, MIN(P.chartTime) as firstChartTime, MAX(P.chartTime) as lastChartTime, 
        COUNT(P.chartTime) as numberOfRecords, min(P.clinicalUnitId) as minClinicalUnitId, max(P.clinicalUnitId) as maxClinicalUnitId
    FROM (
    SELECT * FROM D_Intervention where tableTypeId = 4
    ) as table1
    RIGHT JOIN (
    Select * from PtAssessment WHERE PtAssessment.clinicalUnitId in (5, 8, 9)
    ) as P
    ON table1.interventionId = P.interventionId
    GROUP BY table1.interventionId;
"""