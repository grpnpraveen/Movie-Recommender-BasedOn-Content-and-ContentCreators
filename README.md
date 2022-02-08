# Movie-Recommender-BasedOn-Content-ContentCreators

## Contents

* [Abstract](#Abstract)
* [Problem Definition](#Problem-Definition)
* [Objectives](#Objectives)
	- [Requirements](#Requirements)
* [Challenges](#Challenges)
* [Deliverables ](#html-attributes)
	- [Image / Screenshots of WEB Interface](#links-href-property)
* [Discription of the Dataset Item](#active-item)
* [Proposed Methodology](#inserting-a-separator)
* [Experimental Results](#append-and-prepend)
* [Conclusion](#meta-data)
* [References](#manipulating-the-items)


## Abstract
The main aim of this project is to recommend the best movies that gives the same vibe as the movie the user likes. The movie that user likes will be taken as the input and the best movies will be shown to the user from the database which are similar to the input movie, this process happens using knowledge graphs and natural language processing. In this process the recommendation happens based on content and content creators i.e., genre of the movie, the main plot of the movie, directors, and writers of the movie. 

## Problem Definition
The problem that this project trying to solve is to recommend the accurate movies to the persons who are interested to watch the movies that are similar to the movies that they liked. So, based on these liked movies the suitable movies will be recommended to the users using an interface like web in which all the information about the movie is also shown.

## Objectives
To make a project which has access to movies data and can perform various operations on the data to recommend the user best suited movies based on the one’s he liked based on content and content creators.
### Requirements
1.	The dataset that contains all the movies along with some information about the movie like genre, ratings, directors, and writers.
2.	Best database which uses knowledge graph as a data structure to retrieve data fast based on the relations between the data.
3.	Selecting the suitable web framework which can communicate with graph database and with the web program.
4.	Best natural language processing library which can generate contextual embeddings of a word.
5.	A GPU to make the debugging process fast.

## Challenges
The main challenge in this project is to get data of the movies that is sufficient to make accurate recommendations. 

The ways to get this data are:
1.	Scraping the web to get each movie and its corresponding data. I tested with Wikipedia site to scrape the data but most of the movie’s data is impossible to get because of inconsistence position and tags used in the site.
2.	Using IMDB datasets. I downloaded the IMDb dataset which has all the data of the movies since 1911 to 2020. But the main problem in this method is that the data is inconsistent. Data cleaning is needed to this process. Also, all the necessary data about the content creators are not found in this dataset.
3.	The other method is to use the IMDB library which is available to python to get the necessary data of the movie using movie’s IMDB id. This id can be found from the previous method.
4.	The last and useful method that worked is that combining the methods 2 and 3. The ids from the second method can be used to retrieve the data from the IMDB library which is third method.

