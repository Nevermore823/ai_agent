import requests
import json
import sqlite3
from typing import List, Dict
from openai.lib.azure import AzureOpenAI
from database.db_base import DBBase
from agentbase.tools import *
import pandas as pd
from agentbase.keys import *
from pathlib import Path


class AgentBase:
    def __init__(self, model_name, db_path, api_key=None, end_point=None, api_version=None):
        self.client = AzureOpenAI(
            azure_endpoint=end_point,
            api_key=key,
            api_version="2024-02-01"
            )
        self.db = DBBase(db_path)
        self.model_name = model_name
        
        self.tool_map = {
            'generate_sql': self.db.sql2df,
            'generate_cypher': self.db.execute_cypher
            }
    
    def _get_chat_id(self):
        chat_df = self.db.sql2df(f'''
                                select id as chat_id,
                                name from chat 
                                where name = '{self.model_name}'
                                order by id desc
                                limit 1
                                ''')
        if len(chat_df) > 0:
            chat_id, chat_name = chat_df.loc[0, 'chat_id'], chat_df.loc[0, 'name']
            message_count = self.db.sql2df(f'''
            select count(*) from message where chat_id = {chat_id}
            ''')
            message_count = message_count.values[0][0]
            # 若对话在 10轮以内，则沿用 chat_id，否则创建新的 chat_id
            if message_count < 10:
                return chat_id
        else:
            # 如果没有记录，则新增一条 chat 记录，并使用这个 chat 的 id
            self.db.execute_sql(f'''
            insert into chat (name, created_time) values ('{self.model_name}', current_timestamp)
            ''')
            chat = self.db.sql2df(f'''
            select max(id) id from chat where name = '{self.model_name}' 
            ''')
            chat_id = chat.values[0][0]
            return chat_id
    
    def _get_message(self, chat_id) -> List:
        content_df = self.db.sql2df(f'''
        select role, content from message where chat_id = {chat_id} and role != 'tool' order by id ASC
        ''')
        messages = []
        for i in content_df.index:
            messages.append(dict(role=content_df.loc[i, 'role'], content=content_df.loc[i, 'content']))
        return messages
    
    def chat_completion(self, prompt: str) -> str:
        chat_id = self._get_chat_id()
        messages = self._get_message(chat_id=chat_id)
        new_user_message = {'role': 'user', 'content': prompt}
        messages.append(new_user_message)
        
        completions = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=tool_list,
            )
        # insert_messages(chat_id, new_user_message)
        self.db.execute_sql(f'''
        insert into message (role, content, chat_id, created_time) VALUES('{new_user_message['role']}',
        '{new_user_message['content']}',
        '{chat_id}', current_timestamp)
        ''')
        new_assistant_message = completions.choices[0].message
        # print(completions.model_dump_json(indent=4))
        self.db.execute_sql(f'''
        insert into message (role, content, chat_id, created_time) VALUES('{new_assistant_message.model_dump()['role']}',
        '{new_assistant_message.model_dump()['content']}', '{chat_id}', current_timestamp)
        ''')
        # insert_messages(chat_id, new_assistant_message.model_dump())
        
        choice = completions.choices[0]
        if choice.finish_reason == "tool_calls":
            messages.append(choice.message)
            for tc in choice.message.tool_calls:
                tool = self.tool_map.get(tc.function.name)
                if tool:
                    arguments = list(json.loads(tc.function.arguments).values())[0]
                    content = tool(arguments)
                    if isinstance(content, pd.DataFrame):
                        if len(content) > 0:
                            content_result = content.values[0][0]
                        else:
                            content_result = 0
                       
                    else:
                        content_result = json.dumps({"content": content}, ensure_ascii=False)
                    messages.append({
                        "role": "tool",
                        "content": content_result,
                        "tool_call_id": tc.id
                        })
                    self.db.execute_sql(f'''
                    insert into message (role, content, chat_id, created_time) VALUES('tool', '{content_result}',
                    {chat_id}, current_timestamp)
                    ''')
        elif choice.finish_reason == "stop":
            pass
        return choice.message.content


if __name__ == '__main__':
    ab = AgentBase('gpt-35-turbo-instruct', '../database/test.db')
    # print(test)
