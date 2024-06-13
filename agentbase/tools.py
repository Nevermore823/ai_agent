from database.DDL import *
import trafilatura

db_tools = {
    "type": "function",
    "function": {
        "name": "generate_sql",
        "description": f"""
                根据以下建表语句，结合用户传入的查询需求，生成满足用户条件的 SQL，除了 SQL不要有任何其他的输出
                建表语句: {DDL1}
                注意：要输出DQL，不是 DDL 或 DML
                **输出前一定要反复确认你的输出是否满足用户要求**
            """,
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": f"根据建表语句，结合用户传入的查询需求，生成满足用户条件的 查询SQL，除了 SQL不要有任何其他的输出"
                    }
                }
            },
        "required": ["sql"],
        }
    }

graph_tools = {
    "type": "function",
    "function": {
        "name": "generate_cypher",
        "description": f"""
                根据以下建表语句，结合用户传入的查询需求，生成满足用户条件的 cypher，除了查询cypher不要有任何其他的输出
                Neo4j_schema: {graph_schema}
                **输出前一定要反复确认你的输出是否满足用户要求**
            """,
        "parameters": {
            "type": "object",
            "properties": {
                "cypher": {
                    "type": "string",
                    "description": f"根据Neo4j_schema，结合用户传入的查询需求，生成满足用户条件的 查询cypher，除了cypher不要有任何其他的输出"
                    }
                }
            },
        "required": ["cypher"],
        }
    }


def web_crawl(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    return trafilatura.extract(downloaded)

tool_list = [db_tools, graph_tools]

