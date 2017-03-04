#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import  urllib
from google.appengine.api import users
from google.appengine.ext import ndb

import  jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

GENRE_NAMES=["Rap","Jazz","Reggae"]

def genre_key(genre_name=GENRE_NAMES[0]):
    return ndb.Key('Genre', genre_name)


class Song(ndb.Model):
    name = ndb.StringProperty()
    artist = ndb.StringProperty()
    album = ndb.StringProperty()
    genre = ndb.StringProperty()
    price = ndb.FloatProperty()

class Purchase(ndb.Model):
    Identity =
    date = ndb.DateTimeProperty()
    songs = ndb.StructuredProperty(Song)


class CartItem(ndb.Model):
    Identity =







class MainPage(webapp2.RequestHandler):
    def get(self):
        url = self.request.uri
        template_values = {
            'genres': GENRE_NAMES,
            'genre':GENRE_NAMES[0],
            'url': url,
            'url_linktext' : "Trial",

        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Genre(webapp2.RequestHandler):
    def get(self):
        genre_name = self.request.get('genre',GENRE_NAMES[0])
        song_query = Song.query(ancestor=genre_key(genre_name.lower()))
        songs = song_query.fetch()
        # url = self.request.uri

        template_values = {
            'genre': genre_name,
            'songs':songs

        }

        template = JINJA_ENVIRONMENT.get_template('genre.html')
        self.response.write(template.render(template_values))


class SongTest(webapp2.RequestHandler):
    def get(self):
        genre = self.request.get('genre',GENRE_NAMES[0])

        template_values = {
            'genre': genre,

        }

        template = JINJA_ENVIRONMENT.get_template('song.html')
        self.response.write(template.render(template_values))

    def post(self):
        genre_name = self.request.get('genre', GENRE_NAMES[0])
        song = Song(parent=genre_key(genre_name.lower()))
        song.genre = genre_name
        song.album = self.request.get('albumName')
        song.name = self.request.get('title')
        song.artist = self.request.get('artist')
        song.price = self.request.get('price')
        song.put()



        self.redirect('/')

class Search(webapp2.RequestHandler):
    def get(self):
        print self.request.uri
        if 'artist' in self.request.uri:
            genre = self.request.get('genre',GENRE_NAMES[0])
            artist_name = self.request.get('artist','')
            if artist_name=='':
                songs = "Error enter artist name"
            else:
                print "Searching"
                songs=[]
                song_query = Song.query(ancestor=genre_key(genre.lower()))
                songTest = song_query.fetch()
                for song in songTest:
                    if artist_name.lower() in song.artist.lower():
                        songs.append(song)

                # song_query = song_query.filter(Song.artist==artist_name)
                # songs = song_query.fetch()
                if len(songs)==0:
                    songs="No entries match that artist"
        else:
            genre = self.request.get('genre',GENRE_NAMES[0])
            songs =''

        template_values = {
            'genres' : GENRE_NAMES,
            'genre': genre,
            'songs':songs,

        }

        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))
    def post(self):
        genre = self.request.get('genre')
        artist = self.request.get('artist')

        query_params = {'genre': genre,'artist':artist}
        self.redirect('/search?' + urllib.urlencode(query_params))

class Cart(webapp2.RequestHandler):
    def get(self):
        user = users.create_login_url(self.request.uri)

        pass
    def post(self):
        pass
    def delete(self):
        pass
    def update(self):
        pass





app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/genre',Genre),
    ('/song',SongTest),
    ('/search',Search),
], debug=True)