from neo4j import GraphDatabase
from tqdm import tqdm
import pandas as pd
import json

class Neo4j:
    def __init__(self,uri,user,password):
        self.driver = GraphDatabase.driver(uri,auth=(user,password))

    def query(self,query):
        result=None
        with self.driver.session() as session:
            result = list(session.run(query))
            session.close()
        return result

    def get_movies_based_on_genre(self,genre_name):
        result=None
        with self.driver.session() as session:
            query = f"""
                    match (g:genre) where g.name=$genre_name with g
                    match (g)-[r:`genre-type`]-(m)
                    return m.id as id,m.Movie as movie,m.genre as genre,m.rating as rating,m.votings as votings
                    """
            result=list(session.run(query,genre_name=genre_name))
            session.close()
        return result

    def close(self):
        self.driver.close()

neo = Neo4j("bolt://localhost:7687","neo4j","1234")

# movie and year
# query_result=neo.query(f'''
# match(m:movie) with m 
# return m.Movie as movie, m.year as year
# ''')
# L=[]

# for each_result in query_result:
#     each_record={
#         "name":each_result["movie"],
#         "year":each_result["year"]
#     }
#     L.append(each_record)



# poster links
query_result=neo.query(f'''
match(m:movie) with m 
return m.Movie as movie,m.`fullsize cover` as posterlink
''')
L=[]
for each_result in query_result:
    each_record={
         "name":each_result["movie"],
        "posterlink":each_result["posterlink"]
    }
    L.append(each_record)
    if len(L)==100:
        break
with open("movies_posterlinks.json",'w') as f:
    json.dump(L,f)
    