from bcore.std                          import pre
from datetime                           import datetime
import psycopg2
import psycopg2.extras
from os                                 import path
import json


def pg_config():
    with open(path.expanduser('~/.pg_postgres'), 'r') as fd:
        return json.loads(fd.read())

def quote(string):
    return f"'{string}'"

def ts(string):
    try:
        return quote(datetime.strptime(string, '%m/%d/%Y %H:%M:%S %p'))
    except ValueError:
        return 'NULL'

class DBBase():
    def __init__(self):
        pgcfg = pg_config()
        self.pgcon = None
        self.pgcon = psycopg2.connect(host=pgcfg['host'], port=pgcfg['port'], database=pgcfg['database'], user=pgcfg['user'], password=pgcfg['password'])

    def __del__(self):
        if self.pgcon is not None:
            self.pgcon.close()

    def execute(self, query):
        try:
            cur = self.pgcon.cursor()
            cur.execute(query)
            cur.close()
            self.pgcon.commit()
        except psycopg2.DatabaseError as e:
            pre(e)

    def drop_table(self):
        q  = f'drop table {self.table_name};'
        self.execute(q)

    def query(self, query):
        cursor = self.pgcon.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query)
        return cursor

    def fetch_all(self, query):
        results = self.query(query).fetchall()
        return results

    def fetch_one(self, query):
        results = self.query(query).fetchone()
        return results

class BugsTable(DBBase):
    def __init__(self, module):
        super(BugsTable, self).__init__()
        self.table_name = f"{module.lower().replace('-', '').replace(' ', '_')}_bugs"

    def create_schema(self):
        q  = 'create table if not exists '
        q += f'{self.table_name} ( '
        q += '    id integer primary key,'
        q += '    module varchar,'
        q += '    regression varchar,'
        q += '    disposition varchar,'
        q += '    ts_opened timestamp,'
        q += '    ts_closed timestamp,'
        q += '    ts_fixed timestamp,'
        q += '    os varchar,'
        q += '    requester varchar,'
        q += '    engineer varchar'
        q += ');'
        self.execute(q)

    def add(self, m):
        q  = f'INSERT INTO {self.table_name} ('
        q += 'id, '
        q += 'module,'
        q += 'regression,'
        q += 'disposition,'
        q += 'ts_opened,'
        q += 'ts_closed,'
        q += 'ts_fixed,'
        q += 'os,'
        q += 'requester,'
        q += 'engineer'
        q += ') VALUES ('
        q += f'{m["id"]},'
        q += f'{quote(m["module"])},'
        q += f'{quote(m["regression"])},'
        q += f'{quote(m["disposition"])},'
        q += f'{ts(m["ts_opened"])},'
        q += f'{ts(m["ts_closed"])},'
        q += f'{ts(m["ts_fixed"])},'
        q += f'{quote(m["os"])},'
        q += f'{quote(m["requester"])},'
        q += f'{quote(m["engineer"])}'
        q += ');'
        self.execute(q)

class BugsStatsTable(DBBase):
    def __init__(self, module):
        super(BugsStatsTable, self).__init__()
        self.table_name = f"{module.lower().replace('-', '').replace(' ', '_')}_bug_stats"

    def create_schema(self):
        q  = 'create table if not exists '
        q += f'{self.table_name} ( '
        q += '    ts timestamp primary key,'
        q += '    open integer,'
        q += '    total integer'
        q += ');'
        self.execute(q)

    def update(self, ts, total_open, total_all):
        q  = f"INSERT INTO {self.table_name} VALUES "
        q += f"('{ts}', {total_open}, {total_all}) "
        q += f"ON CONFLICT(ts) DO UPDATE SET open = {total_open}, total = {total_all};"
        self.execute(q)

    def add(self, ts, topen, total):
        q  = f'INSERT INTO {self._table_name} ('
        q += 'ts, open, total'
        q += f") VALUES ({ts}, {topen}, {total});"
        self.execute(q)
