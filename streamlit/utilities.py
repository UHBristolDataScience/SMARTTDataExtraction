import pyodbc
import json
import pandas as pd
import streamlit as st
from st_pages import hide_pages


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
