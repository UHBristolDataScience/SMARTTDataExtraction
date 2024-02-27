import pyodbc
import sys
from pathlib import Path
import pandas as pd

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


test_query = "SELECT TOP 10 * FROM D_Intervention"


if __name__ == '__main__':

    save_path = Path(
        "../data/test_query_results.tsv"
    )

    if len(sys.argv) > 1:
        _db = sys.argv[1]
        _server = sys.argv[2]
    else:
        _db = "CISReportingDB"
        _server = "ubhnt34.ubht.nhs.uk"

    print(
        "Connecting to database %s on server %s..."
        % (_db, _server)
    )

    df = run_query(
        test_query,
        db=_db,
        server=_server
    )
    df.to_csv(save_path, sep="\t")
    print("Query complete and results saved to %s." % save_path)
