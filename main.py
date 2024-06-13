from database.db_base import DBBase
from agentbase.agent_base import AgentBase
import sys


def create_db():
    db = DBBase('database/test.db')
    db.execute_sql('''
        create table if not exists chat
        (id integer primary key autoincrement,
        name varchar(255),
        created_time timestamp not null
        );
        ''')
    db.execute_sql('''
        create table if not exists message
        (id integer primary key autoincrement,
        role varchar(255) not null,
        content varchar(255) not null,
        chat_id integer not null,
        created_time timestamp not null
        );
        ''')


def run(prompt: str):
    ab = AgentBase('gpt-35-turbo-instruct', 'database/test.db')
    result = ab.chat_completion(prompt)
    print(result)


if __name__ == '__main__':
    run(sys.argv[1])
    