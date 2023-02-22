from bcore.std                          import pre
from nvcore.nvcreds                     import nvkpis_postgres
from datetime                           import datetime
import psycopg2
from os                                 import path
import json


def pg_config():
    with open(path.expanduser('~/.pg_postgres'), 'r') as fd:
        return json.loads(fd.read())

class DBBase():
    def __init__(self):
        pgcfg = nvkpis_postgres()
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
        q  = f'drop table {self._table_name};'
        self.execute(q)

class BugTable(DBBase):
    def __init__(self, module):
        super(BugTable, self).__init__()
        self._table_name = f"{module.replace(' ', '_')}_bugs"

    def create_schema(self):
        q  = 'create table if not exists '
        q += f'{self._table_name} ( '
        q += '    id integer,'
        q += '    module varchar,'
        q += ');'
        self.execute(q)

    def add(self, m):
        q  = f'INSERT INTO {self._table_name} ('
        q += 'id, '
        q += 'module, '
        q += ') VALUES ('
        q += f'{m["id"]},'
        q += f'{m["module"]}'
        q += ');'
        self.execute(q)
