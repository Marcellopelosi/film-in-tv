import streamlit
import requests
import re

def from_url_to_r(url):

  try:
      r = requests.get(url)
      return r
  except:
      return("ERROR!")

st.title("Film di stasera in tv con rating")

r = from_url_to_r("https://www.staseraintv.com/film_in_tv_stasera.html")

films_pattern = r'(?<=;">).*?(?=Film)'
films = re.findall(films_pattern, r.text)
films = [f[:-2].encode('latin-1').decode('utf-8') for f in films]

time_pattern = r'(?<=>).*?(?=</span></span></big></big><br>)'
time = re.findall(time_pattern, r.text)

channel_pattern = r'(?<=stb1">).*?(?=</a>)'
channels = re.findall(channel_pattern, r.text)
channels = channels[channels.index('Stasera In TV Android')+1:]
channels = channels[:channels.index('Film')]

r = from_url_to_r("https://www.staseraintv.com/film_in_tv_stasera_secondaserata.html")

films_2 = re.findall(films_pattern, r.text)
films_2 = [f[:-2].encode('latin-1').decode('utf-8') for f in films_2]

time_2 = re.findall(time_pattern, r.text)

channels_2 = re.findall(channel_pattern, r.text)
channels_2 = channels_2[channels_2.index('Stasera In TV Android')+1:]
channels_2 = channels_2[:channels_2.index('Film')]

time = time + time_2
films = films + films_2
channels = channels + channels_2

import pandas as pd

df = pd.DataFrame({"Orario inizio":time, "Titolo film": films, "Canale": channels})

df = df.loc[[False if "Sky" in ch else True for ch in df["Canale"]]]
df.index = df["Orario inizio"]
df.drop(inplace = True, columns = ["Orario inizio"])

def filmtv_rating(titolo_film):

  r = from_url_to_r("https://www.filmtv.it/cerca/?q=" + "+".join(titolo_film.split()))
  url = "http://www.filmtv.it/film/" + re.findall(r'\d+', re.findall(r'(?<=href=").*?(?="  title)', r.text.split("- FILM -")[1])[0])[0]
  r = from_url_to_r(url)
  pattern_valutazione = r'(?<=<meter max="10" min="0" value=").*?(?=" data-updval)'
  return float(re.findall(pattern_valutazione, r.text)[0])

import time

ratings = []
for titolo_film in df["Titolo film"]:
  ratings.append(filmtv_rating(titolo_film))
  time.sleep(0.2)

df["ratings"]= ratings

df = df.sort_values(by = "ratings", ascending = False)

st.dataframe(df)
