#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#imports all the needed methods
from Bio import Entrez
from Bio import Medline
from bs4 import BeautifulSoup
import requests
import urllib
import pandas as pd


# In[126]:


#gets the IDs of the articles; max of 50 articles; takes a query, in this case machine learning; database is pubmed
def search(query):      
    Entrez.email = 'eli.krasnoff@gmail.com'
    handle = Entrez.esearch(db="pubmed", term=query, retmax=100)
    record = Entrez.read(handle)
    handle.close()
    return record

#from the IDs of the articles that meet the parameters efetch gets all the details associated with the papers and
#stores the list as a dictionary with the key being the ID
def fetchDetails(IdList):
    handle = Entrez.efetch(db="pubmed", id=IdList, rettype="medline", retmode="text")
    details = Medline.parse(handle)
    detailsDict = {}
    for detail in details:
        detailsDict[detail['PMID']] = detail
    return detailsDict #contains 50 papers

#a function to remove [doi] from a string
def removeSubstring(originalString):
    newString = originalString.replace(' [doi]', '')
    return newString
   
#creates a dictionary with all the DOIs connected to the key of the article; stores it under doiDict
def getDOI(detailsDict):
    for idl, detail in detailsDict.items():
        lid = detail['LID']
        if '[doi]' in lid:
            if '[pii]' in lid:
                lid = lid.split('[pii] ', 1)
                if len(lid) > 0:
                    lid = lid[1]
            lid = removeSubstring(lid)
        doiDict[idl] = lid
    return doiDict

#creates a dictionary of the amount of times each term you want to search for pops up; stores the terms as two dictionaries
#with the key being the term and those dictionaries are under the key of the associated ID
def getCount(terms, doiDict):
    countDict = {}
    for idl, doi in doiDict.items():
        url = f"https://doi.org/{doi}" #creates the full url with the specific doi for each term
        headers = {'Accept-Encoding': 'identity'} #tells the server not to compress it
        html = requests.get(url, headers=headers)
        html = html.text
        htmlParse = BeautifulSoup(html, 'html.parser')
        res = htmlParse.get_text()
        countDict[idl] = {}
        for term in terms:
            countDict[idl][term] = res.count(term)
    return countDict

#creates a dictionary of the titles associated with the IDs of the articles
def getTitle(detailsDict):
    titleDict = {}
    for idl, detail in detailsDict.items():
        titleDict[idl] = detail['TI']
    return titleDict


# In[137]:


record = search('machine learning[title/abstract] AND 2021/01/01:2021/12/31[EDAT]') #the title of the paper and date constraints
terms = ['code', 'github'] #the desired tearms to be searched for in each paper

IdList = record['IdList'] #list of all the IDs
detailsDict = fetchDetails(IdList) #dictionary of all necessary details surrounding the paper
titleDict = getTitle(detailsDict) #dictionary with titles
doiDict = getDOI(detailsDict) #dictionary with DOIs
countDict = getCount(terms, doiDict) #dictionary with amount of hits per term

df = pd.DataFrame()

#assings values to the columns
df['ID'] = titleDict.keys()
df['Title'] = titleDict.values()
df['DOI'] = doiDict.values()
for term in terms:
    df[term + ' count'] = [x[term] for x in countDict.values()]


display(df)

df.to_csv('pubmed_searcher.csv') #saves data to a csv file named pubmed_searcher.csv

