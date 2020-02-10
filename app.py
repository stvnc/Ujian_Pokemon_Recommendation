from flask import Flask, abort, jsonify, render_template,url_for, request,send_from_directory,redirect
import numpy as np
import pandas as pd
import requests

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv('Pokemon.csv')
print(df.head(5))

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

pokemonDf = pd.read_csv('Pokemon.csv')
print(pokemonDf.head(5))

def combine(i):
    return str(i['Type 1'])+ ',' +str(i['Generation'])+','+str(i['Legendary'])

pokemonDf['Attribute']= pokemonDf.apply(combine, axis=1)
pokemonDf['Name']= pokemonDf['Name'].apply(lambda i: i.lower())

extractor = CountVectorizer()
exfit = extractor.fit_transform(pokemonDf['Attribute'])
extractor.get_feature_names()

exfit = exfit.toarray()

cosScore = cosine_similarity(exfit)
cosScore

pokemonName = "pikachu"
indexSuka = pokemonDf[pokemonDf['Name'] == pokemonName].index[0]
indexSuka

recommendedPokemon = list(enumerate(cosScore[indexSuka]))
recommendedPokemon = list(filter(lambda x: x[1] > 0.5, recommendedPokemon))
recommendedPokemon = recommendedPokemon[:6]

recommendedList = []
for i in recommendedPokemon:
    recommendedList.append(pokemonDf.iloc[i[0]][:-1])

recommendation = pd.DataFrame(recommendedList)

pokemonIndex = recommendation.index
print(recommendation)

image = []

for i in pokemonIndex:
    image.append(f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{i}.png')

recommendation['image'] = image

print(recommendation)

@app.route('/FindPokemon', methods=['GET','POST'])
def Cari():
    body = request.form
    pokesuka = body['Pokemon']
    pokesuka = pokesuka.lower()
    if pokesuka not in list(pokemonDf['Name']):
        return redirect('/NotFound')
    favorit = pokemonDf.iloc[indexSuka][["Name",'Type 1','Generation','Legendary']]
    url = 'https://pokeapi.co/api/v2/pokemon/'+ pokesuka
    url = requests.get(url)
    imageRecom = url.json()["sprites"]["front_default"]
    pokeSamaSortir = sorted(recommendedPokemon, key= lambda x:x[1], reverse= True)
    Rekom=[]
    for item in pokeSamaSortir[:7]:
        x={}
        if item[0] != indexSuka:
            nama = pokemonDf.iloc[item[0]]['Name'].capitalize()
            type = pokemonDf.iloc[item[0]]['Type 1']
            legend = pokemonDf.iloc[item[0]]['Legendary']
            gen = pokemonDf.iloc[item[0]]['Generation']
            url = 'https://pokeapi.co/api/v2/pokemon/'+ nama.lower()
            url = requests.get(url)
            pic = url.json()["sprites"]["front_default"] 
            x['Name']= nama
            x['Type']= type
            x['Legend']= legend
            x['Generation']= gen
            x["gambar"] = pic
            Rekom.append(x)
    return render_template('recommendation.html',rekomen= Rekom, favorit= favorit, pic=imageRecom)

#---------------------------------------------------------------------
@app.route('/NotFound')
def notFound():
    return render_template('notfound.html')
#--------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)