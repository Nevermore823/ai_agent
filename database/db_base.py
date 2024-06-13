import sqlite3
from py2neo import Graph, Node, Relationship
import pandas as pd
import traceback
import warnings
warnings.filterwarnings("ignore")


class DBBase:
    def __init__(self, db_path, **kwargs):
        self.db_path = db_path
        self.graph_db_url = ""
        self.graph_db_user = ""
        self.graph_db_password = ""

        # 结构型数据库目前支持 sqlite
        # todo:配置 pgsql，sql sever 等主流数据库
        self.g = Graph(self.graph_db_url, auth=(self.graph_db_user,  self.graph_db_password))
        print('已成功连接neo4j：{}'.format(self.graph_db_url))
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        print('已成功连接{}'.format(self.db_path))
        
        self.cur.execute('''
            create table if not exists chat
    (
        id   integer primary key autoincrement,
        name text,
        created_time timestamp
    );
        ''')
        
        self.cur.execute('''
            create table if not exists message
    (
        id              integer primary key autoincrement,
        content         text,
        role            text not null,
        tool_call_id    text,
        chat_id         integer not null
        created_time    timestamp
    );
        ''')
        
        self.cur.execute('''
        create table if not exists tool_call
    (
        id                 integer primary key autoincrement,
        tool_id            text not null,
        type               text not null,
        function_name      text,
        function_arguments text,
        message_id         integer not null
        created_time       timestamp
    )
        ''')
        

    def execute_sql(self, sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
            print('sql: "{}" done'.format(sql))
        except Exception:
            print(str(traceback.format_exc()))

    def sql2df(self, sql):
        try:
            df = pd.read_sql_query(sql, self.conn)
            return df
        except Exception:
            print(str(traceback.format_exc()))
            return None

    def insert_by_df(self, df, table_name, schema, index=False, index_label=None, if_exists='replace', chunksize=None):
        try:
            if chunksize is None:
                df.to_sql(table_name, self.conn, schema, if_exists=if_exists, index=index)
            else:
                df.to_sql(table_name, self.conn, schema, if_exists=if_exists, chunksize=chunksize,
                          index=index, index_label=index_label)
            return 0
        except Exception:
            print(str(traceback.format_exc()))
            return 1

    def execute_cypher(self, sql):
        try:
            return self.g.run(sql)
        except Exception:
            print(str(traceback.format_exc()))
    
