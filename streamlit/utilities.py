import pyodbc
from st_pages import hide_pages


def _hide_pages():
    hide_pages(
            ['intervention_mapping', 'attribute_mapping', 'choose_data_source']
    )


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
