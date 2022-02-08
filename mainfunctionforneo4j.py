from neo4j import GraphDatabase
from tqdm import tqdm
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow_text as text
import tensorflow_hub as hub
import json
import os

bert_encoder=hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4")
bert_preprocess=hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3")


#


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
def get_sentence_embeding(sentences):
    preprocessed_text=bert_preprocess(sentences)
    return bert_encoder(preprocessed_text)['pooled_output']

def recommandmovies(input_movie_id):
        
    # input_movie_genres=pd.DataFrame([dict(_) for _ in neo.get_genre(input_movie)])
    input_movie_genres=[ _["genre"] for _ in neo.query(f''' 
                        match (m:movie) where m.id="{input_movie_id}" with m
                        match (m)-[r:`genre-type`]-(g)
                        with m,g
                        return g.name as genre ''')]
    # input_movie_genres

    #
    input_movie_directors= [ _["id"] for _ in neo.query(f''' 
                match(m: movie) 
                where m.id="{input_movie_id}"
                with m
                match (m)-[r:directed]-(d)
                with m,d
                return d.id as id
    ''')]
    # input_movie_directors

    input_movie_writers= [ _["id"] for _ in neo.query(f''' 
                match(m: movie) 
                where m.id="{input_movie_id}"
                with m
                match (m)-[r:written]-(w)
                with m,w
                return w.id as id
    ''')]
    # input_movie_writers

    # including this directors
    same_persona_directors=dict()
    for each_director in tqdm(input_movie_directors):
        for g in input_movie_genres:
                if(g=="Film-Noir"):
                    g="FilmNoir"
                elif(g=="Sci-Fi"):
                    g="SciFi"
                elif(g=="Reality-TV"):
                    g="RealityTV"
                g=g+"_trait"
                value=[_[g] for _ in neo.query(f'''
                                match (d:director) 
                                where d.id>={each_director}
                                with d 
                                return d.{g} as {g}
                                ''')]
                # print(value)
                query_result=neo.query(f''' 
                            match (d:director)
                            where d.{g}= {value[0]}
                            with d
                            return d.id as id,d.{g} as {g}
                ''')
                # print(query_result)
                for _ in query_result:
                    same_persona_directors[_["id"]]=_[g]

    # print("Length: "+str(len(same_persona_directors)))
    # sorting based on values
    # for i in same_persona_directors:
    #     print(i,same_persona_directors[i],sep=" ")
    #     break
    same_persona_directors = sorted(same_persona_directors.items(), key=lambda x: x[1], reverse=True)
    # for i in same_persona_directors:
    #     print(i[0],i[1])
    #     break
    # print("Length: "+str(len(same_persona_directors)))

    #

    # including this writers
    same_persona_writers=dict()
    for each_writer in tqdm(input_movie_writers):
        for g in input_movie_genres:
                if(g=="Film-Noir"):
                    g="FilmNoir"
                elif(g=="Sci-Fi"):
                    g="SciFi"
                elif(g=="Reality-TV"):
                    g="RealityTV"
                g=g+"_trait"
                value=[_[g] for _ in neo.query(f'''
                                match (w:writer) 
                                where w.id>={each_writer}
                                with w 
                                return w.{g} as {g}
                                ''')]
                # print(value)
                query_result=neo.query(f''' 
                            match (w:writer) 
                            where w.{g}={value[0]}
                            with w
                            return w.id as id,w.{g} as {g}
                ''')
                # print(query_result)
                for _ in query_result:
                    same_persona_writers[_["id"]]=_[g]

    # print("Length: "+str(len(same_persona_writers)))

    # sorting based on values
    for i in same_persona_writers:
        print(i,same_persona_writers[i],sep=" ")
        break
    same_persona_writers = sorted(same_persona_writers.items(), key=lambda x: x[1], reverse=True)
    for i in same_persona_writers:
        print(i[0],i[1])
        break
    print("Length: "+str(len(same_persona_writers)))

    input_movie_rating=[_["rating"] for _ in neo.query(
    f'''
        match(m:movie)  
        where m.id ="{input_movie_id}"
        with m
        return m.rating as rating
    ''')]

    input_movie_rating[0]

    final_movies_list=[]
    # test=[91515]
    # for each_creator in test:
    directors_len=len(same_persona_directors)
    if(directors_len>5):
        directors_len=5
    for each_creator in tqdm(same_persona_directors[:directors_len]):
        query_result=neo.query(f'''
            match (d:director)
            where d.id ={each_creator[0]}
            with d
            match (d)-[r:directed]-(m:movie)
            with d,m
            where m.rating>{input_movie_rating[0]}
            and any(x in split(m.genre,"|") where x in {input_movie_genres})
            return m.id as id
        ''')
        # print(query_result)
        for each_movie in query_result:
            final_movies_list.append(each_movie["id"])
    print("Length: "+str(len(final_movies_list)))

    writers_len=len(same_persona_writers)
    if(writers_len>10):
        writers_len=10
    for each_creator in tqdm(same_persona_writers[:writers_len]):
        query_result=neo.query(f'''
            match (w:writer)
            where w.id ={each_creator[0]}
            with w
            match (w)-[r:written]-(m:movie)
            with w,m
            where m.rating>{input_movie_rating[0]}
            and any(x in split(m.genre,"|") where x in {input_movie_genres})
            return m.id as id
        ''')
        # print(query_result)
        for each_movie in query_result:
            final_movies_list.append(each_movie["id"])
    print("Length: "+str(len(final_movies_list)))

    l=len(final_movies_list)
    if(l>10):
        final_movies_list=final_movies_list[:10]
    l=len(final_movies_list)

    input_movie_plot=[ _["plot"] for _ in neo.query(f''' 
                match (m:movie) where m.id="{input_movie_id}"
                with m
                return m.plot as plot
    ''')]
    input_movie_plot[0]

    # input movies vector
    input_movie_vector=get_sentence_embeding([input_movie_plot[0]])

    final_movies=dict()
    if(len(final_movies_list)>5):
            final_movies_list=final_movies_list[:5]
    for each_final_movie_id in tqdm(final_movies_list):
        query_result=[ _["plot"] for _ in neo.query(f''' 
                match(m:movie)
                where m.id="{each_final_movie_id}"
                with m
                return m.plot as plot 
        ''')]
        final_movies[each_final_movie_id]=get_sentence_embeding([query_result[0]])
    print("Length: "+str(len(final_movies_list)))

    for each_final_movie_id in tqdm(final_movies):
        result=cosine_similarity([input_movie_vector[0]],[final_movies[each_final_movie_id][0]])
        final_movies[each_final_movie_id]=result[0][0]
    print("Length: "+str(len(final_movies)))

    for i in final_movies:
        print(final_movies[i])
        break
    final_movies = sorted(final_movies.items(), key=lambda x: x[1], reverse=True)

    for i in final_movies:
        print(i[0],i[1])
        break
    return final_movies

def get_movie_id(name,year):
    result=[ _["id"] for _ in neo.query(f'''
         match (m:movie) with m
         where m.Movie="{name}" and m.year ={year}
         return m.id as id
         ''')]
    return result[0]

def automate(name,year):
    List=[]
    final_list=recommandmovies(get_movie_id(name,year))
    for i in final_list:
        query_result=neo.query(f'''
        match (m:movie) 
        where m.id="{i[0]}"
        with m
        return m.Movie as movie,m.`small cover` as smallposter,m.id as id
        ''')
        for each_query_result in query_result:
            each_record={
         "name":each_query_result["movie"],
        "posterlink":each_query_result["smallposter"],
        "id":each_query_result["id"]
            }
            List.append(each_record)
        # try:
        #     os.remove("./static/results.json")
        # except:
        #     pass
        with open("./static/results.json",'w') as f:
            json.dump(List,f)
            f.close()

def getmovieinfo(id):
    List2=[]
    query_result=neo.query(f'''
    match (m:movie) 
    where m.id="{id}"
    with m
    return m.Movie as movie,m.year as year,m.genre as genre,m.rating as rating,m.duration as duration,m.plot as plot,m.`small cover` as poster
    ''')

    for each_query_result in query_result:

        each_record={
        "name":each_query_result["movie"],
        "year":each_query_result["year"],
        "genre":each_query_result["genre"],
        "rating":each_query_result["rating"],
        "duration":each_query_result["duration"],
        "plot":each_query_result["plot"],
        "poster":each_query_result["poster"]
        }
    List2.append(each_record)
    # try:
    #     os.remove("./static/results.json")
    # except:
    #     pass
    with open("./static/movieinfo.json",'w') as f:
        json.dump(List2,f)
        f.close()
    direc=[]
    directors_result=neo.query(f'''
    match (m:movie) where m.id="{id}"
    with m
    match (m)-[r:directed]-(d:director)
    return d.name as name,d.Headshot as photo
    ''')
    for each_query_result in directors_result:
        d_record={
            "name":each_query_result["name"],
            "photo":each_query_result["photo"]
        }
        direc.append(d_record)
    with open("./static/directors.json",'w') as f:
        json.dump(direc,f)
        f.close()
    writer=[]
    writers_result=neo.query(f'''
    match (m:movie) where m.id="{id}"
    with m
    match (m)-[r:written]-(d:writer)
    return d.name as name,d.Headshot as photo
    ''')
    for each_query_result in writers_result:
        d_record={
            "name":each_query_result["name"],
            "photo":each_query_result["photo"]
        }
        writer.append(d_record)
    with open("./static/writers.json",'w') as f:
        json.dump(writer,f)
        f.close()
    actor=[]
    actors_result=neo.query(f'''
    match (m:movie) where m.id="{id}"
    with m
    match (m)-[r:`acted-in`]-(d:actor)
    return d.name as name,d.Headshot as photo
    ''')
    for each_query_result in actors_result:
        d_record={
            "name":each_query_result["name"],
            "photo":each_query_result["photo"]
        }
        actor.append(d_record)
    with open("./static/cast.json",'w') as f:
        json.dump(actor,f)
        f.close()


# x=automate("Iron Man",1931)
# input_movie_id="tt0044954"
# input_movie_id=get_movie_id("Iron Man",1931)
# print(input_movie_id)
# final_result=recommandmovies(input_movie_id)
