import pyodbc
import json
import pandas as pd
import streamlit as st
from st_pages import hide_pages
import sqlite3
from numpy import logical_or


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


# TODO: add context manager to connection so can't be left hanging
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
            COUNT(P.chartTime) as numberOfRecords, min(P.clinicalUnitId) as minClinicalUnitId, max(P.clinicalUnitId) as maxClinicalUnitId,
            MIN(table1.tableTypeId) as tableTypeId
        FROM (
        SELECT * FROM D_Intervention where tableTypeId = {table_type_id}
        ) as table1
        RIGHT JOIN (
        Select * from {table} as t WHERE t.clinicalUnitId in ({unit_string})
        ) as P
        ON table1.interventionId = P.interventionId
        GROUP BY table1.interventionId;
    """


def initial_attribute_query(intervention_id, table='PtLabResult', clinical_unit_ids=[5, 8, 9]):
    unit_string = ", ".join(f"{x}" for x in clinical_unit_ids)

    return f"""
        SELECT DISTINCT(attributeId) 
        FROM {table} 
        WHERE interventionId = {intervention_id} and clinicalUnitId in ({unit_string});
    """


def example_attribute_data_query(attribute_id, table, n=50):
    return f"""
        SELECT TOP {n} 
            D.attributeId, D.shortLabel, D.longLabel, P.clinicalUnitId, P.terseForm, 
            P.verboseForm, P.valueNumber, P.valueString, P.valueDateTime, P.unitOfMeasure 
        FROM (
          SELECT * FROM {table} WHERE (
            encounterId in (SELECT encounterId from {table}) 
            and attributeId = {attribute_id}
          )
        ) as P
        INNER JOIN (
          SELECT * FROM D_Attribute WHERE attributeId={attribute_id}
        ) as D
        ON P.attributeId = D.attributeId
    """


def full_extraction_query(attribute_id, table, clinical_unit_ids=[5, 8, 9]):
    unit_string = ", ".join(f"{x}" for x in clinical_unit_ids)

    return f"""
            SELECT
                D.attributeId, P.interventionId, P.encounterId, D.shortLabel as attributeShortLabel, 
                D.longLabel as attributeLongLabel, 
                P.clinicalUnitId, P.terseForm, P.verboseForm, P.valueNumber, P.valueString, P.valueDateTime, 
                P.unitOfMeasure, P.chartTime, P.storeTime, P.utcChartTime, P.careProviderId, P.tableTypeId,
                P.bedId, P.lowerNormal, P.upperNormal, D.conceptLabel as attributeConceptLabel, 
                D.conceptCode as attributeConceptCode 
            FROM (
              SELECT * FROM {table}
              WHERE (
                encounterId in (SELECT encounterId from {table}) 
                and attributeId = {attribute_id}
                and clinicalUnitId in ({unit_string})
              )
            ) as P
            INNER JOIN (
              SELECT * FROM D_Attribute WHERE attributeId = {attribute_id}
            ) as D
            ON P.attributeId = D.attributeId;
        """

    # return f"""
    #     SELECT
    #         D.attributeId, P.interventionId, P.encounterId, D.shortLabel as attributeShortLabel,
    #         D.longLabel as attributeLongLabel,
    #         P.clinicalUnitId, P.terseForm, P.verboseForm, P.valueNumber, P.valueString, P.valueDateTime,
    #         P.unitOfMeasure, P.chartTime, P.storeTime, P.utcChartTime, P.careProviderId, P.tableTypeId,
    #         P.bedId, P.lowerNormal, P.upperNormal, D.conceptLabel as attributeConceptLabel,
    #         D.conceptCode as attributeConceptCode
    #     WITH NOT SKABOOM
    #     FROM (
    #       SELECT * FROM {table}
    #       WHERE (
    #         encounterId in (SELECT encounterId from {table})
    #         and attributeId in ({attributes_string})
    #         and chartTime in (SELECT chartTime from {table})
    #         and clinicalUnitId in ({unit_string})
    #       )
    #     ) as P
    #     INNER JOIN (
    #       SELECT * FROM D_Attribute WHERE attributeId in ({attributes_string})
    #     ) as D
    #     ON P.attributeId = D.attributeId;
    # """


def get_search_strings_for_variable(var):

    return [
        s.strip()
        for s in
        st.session_state.schema.loc[
            st.session_state.schema.Variable == var
        ]['Search Strings'].iloc[0].split(',')
    ]


def search_strings_to_logical_index(dataframe, search_strings):
    return logical_or.reduce(
        [
            dataframe.longLabel.str.contains(search_string, case=False)
            for search_string in search_strings
        ]
    )


def load_interventions():
    """
    Function to load, from local Sqlite db, all interventions that were
    previously found in ICCA using the search strings from the schema.

    Joins all into a single dataframe.
    """
    fact_tables = st.session_state.config['icca']['fact_tables']
    interventions = pd.concat(
        [
            st.session_state.local_db.query_pd(
                f"SELECT * FROM {table}Interventions"
            )
            for table in fact_tables.keys()
        ],
        axis=0
    )
    interventions.dropna(axis=0, subset=['shortLabel', 'longLabel'], inplace=True)
    interventions.reset_index(drop=True, inplace=True)
    return interventions


def load_example_data(attribute_id_list, add_median_iqr=False):
    attribute_string = ", ".join(f"{x}" for x in attribute_id_list)
    df = st.session_state.local_db.query_pd(
        f"""
            SELECT * FROM example_attribute_data
            WHERE attributeId in ({attribute_string})
        """
    )
    return_data = df.groupby('attributeId').apply(pd.DataFrame.sample, n=1, random_state=42).reset_index(drop=True)

    if add_median_iqr:

        numeric_df = df.copy()
        numeric_df['valueNumber'] = pd.to_numeric(numeric_df['valueNumber'], errors='ignore')
        numeric_df = numeric_df[[not isinstance(v, str) for v in numeric_df.valueNumber]]

        df_median = numeric_df.groupby('attributeId').agg(
            {'valueNumber': 'median'}
        ).rename(columns={'valueNumber': 'median'})
        df_lqr = numeric_df[['attributeId', 'valueNumber']].groupby('attributeId').agg(
            'quantile', q=0.25
        ).rename(columns={'valueNumber': 'lower_quartile'})
        df_uqr = numeric_df[['attributeId', 'valueNumber']].groupby('attributeId').agg(
            'quantile', q=0.75
        ).rename(columns={'valueNumber': 'upper_quartile'})

        return_data = (
            return_data
                .join(df_median, on='attributeId')
                .join(df_lqr, on='attributeId')
                .join(df_uqr, on='attributeId')
        )

    return return_data


def mark_variable_as_mapped():

    st.session_state.local_db.insert_query(
        f"""
                UPDATE schema
                SET mapping_complete = True
                WHERE "Variable" = "{st.session_state.active_variable}";
            """
    )
    st.session_state['schema'] = st.session_state.local_db.query_pd(
        "SELECT * FROM SCHEMA"
    )
    progress = 1 / len(st.session_state.schema)
    st.session_state.local_db.insert_query(
        f"""
                UPDATE info
                SET variable_mapping_progress = variable_mapping_progress + {progress}
                WHERE "name" = "{st.session_state.project_name}";
            """
    )
    st.session_state['active_intervention_id'] = None
