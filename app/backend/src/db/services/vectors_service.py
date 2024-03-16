from orm.models import Vectors
from orm.connection import Session
from openai import OpenAI
from sqlalchemy import text
import time

client = OpenAI()

def create_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model, dimensions=1536).data[0].embedding


# function to insert a vector embedding into vector table
def insert_vector(script_id, vector):
    session = Session()
    new_vector = Vectors(vector_id=script_id, vector=vector)
    session.add(new_vector)
    session.commit()
    session.refresh(new_vector)
    session.close()
    return new_vector.vector_id
 
def query_search(query: str):
    session = Session()
    query = create_embedding(query)
    sql = text(f"""
        SELECT vector_id
        FROM vectors
        ORDER BY vector <-> '{query}'
        LIMIT 5;
    """)
    start = time.time()
    results = session.execute(sql).fetchall()
    end = time.time()
    print("################", end - start)
    return results
