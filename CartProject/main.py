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

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

GENRE_NAMES=["Rap","Jazz","Reggae"]

def genre_key(genre_name=GENRE_NAMES[0]):
    return ndb.Key('Genre', genre_name)

def cart_key(buyer_email=""):
    return ndb.Key('Buyer', buyer_email)

class Buyer(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    #email = ndb.StringProperty(indexed=True,required=True)
    key = ndb.StringProperty(indexed=True,required=True)


class Song(ndb.Model):
    name = ndb.StringProperty()
    artist = ndb.StringProperty()
    album = ndb.StringProperty()
    genre = ndb.StringProperty()
    price = ndb.StringProperty(default='$0.00')

class ShoppingCart(ndb.Model):
    buyer = ndb.StructuredProperty(Buyer,required=True)
    songs = ndb.StructuredProperty(Song,repeated=True)
    total = ndb.StringProperty()

class Purchase(ndb.Model):
    date = ndb.DateTimeProperty(auto_now_add=True)
    cart = ndb.StructuredProperty(ShoppingCart,required=True)




class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            urlLinktext = 'Logout'
            checkUser = Buyer.query().fetch()
            newBuyer = Buyer(identity = user.user_id(),key = user.email())


            if len(checkUser) == 0:
               newBuyer.put()
               newShoppingCart = ShoppingCart(parent=cart_key(newBuyer.key))
               newShoppingCart.buyer = newBuyer
               newShoppingCart.put()
            else:
                userExist = False
                for buy in checkUser:
                    if buy.key == newBuyer.key:
                        userExist = True
                        break
                if not userExist:
                        newBuyer.put()
                        newShoppingCart = ShoppingCart(parent=cart_key(newBuyer.key))
                        newShoppingCart.buyer = newBuyer
                        newShoppingCart.put()




        else:
            url = users.create_login_url(self.request.uri)
            urlLinktext = 'Login'
        template_values = {
            'genres': GENRE_NAMES,
            'genre':GENRE_NAMES[0],
            'url': url,
            'url_linktext' : urlLinktext

        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Genre(webapp2.RequestHandler):
    def get(self):
        genre_name = self.request.get('genre',GENRE_NAMES[0])
        song_query = Song.query(ancestor=genre_key(genre_name.lower()))
        songs = song_query.fetch()
        # print songs[0].key
        # test = songs[0].key.id()
        # print test
        # url = self.request.uri
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            urlLinktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            urlLinktext = 'Login'

        template_values = {
            'genre': genre_name,
            'songs':songs,
            'url': url,
            'url_linktext': urlLinktext

        }

        template = JINJA_ENVIRONMENT.get_template('genre.html')
        self.response.write(template.render(template_values))


class SongTest(webapp2.RequestHandler):
    def get(self):
        genre = self.request.get('genre',GENRE_NAMES[0])
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            urlLinktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            urlLinktext = 'Login'

        template_values = {
            'genre': genre,
            'url': url,
            'url_linktext': urlLinktext

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

        print '${:0,.2f}'.format(float(self.request.get('price')))

        song.price = '${:0,.2f}'.format(float(self.request.get('price')))

        song.put()
        self.redirect('/')

class Search(webapp2.RequestHandler):
    def get(self):
        # print self.request.uri
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            urlLinktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            urlLinktext = 'Login'
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
            'url': url,
            'url_linktext': urlLinktext

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
        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            urlLinktext = 'Logout'
            myCart = ShoppingCart.query(ancestor=cart_key(user.email())).fetch(1)
            cart = myCart[0]
            songs = myCart[0].songs
            newSongList = []
            for song in songs:
                songQuery = Song.query(ancestor=genre_key(song.genre.lower())).fetch()
                for songQ in songQuery:
                    if songQ.name == song.name:
                        newSongList.append(songQ)
                        break
            songs = newSongList


        else:
            url = users.create_login_url(self.request.uri)
            urlLinktext = 'Login'
            cart = None
            songs = []


        template_values = {
            'cart': cart,
            'cartSongs':songs,
            'url': url,
            'url_linktext': urlLinktext

        }
        template = JINJA_ENVIRONMENT.get_template('cart.html')
        self.response.write(template.render(template_values))

    def post(self):
        user = users.get_current_user()
        songs = self.request.params.items()
        myCart = ShoppingCart.query(ancestor=cart_key(user.email())).fetch(1)
        for song in songs:
            name = song[1]
            if 'add' in name:
                name = name.replace('add','',1)
                songSelected = ndb.Key(urlsafe=name).get()
                myCart[0].songs.append(songSelected)
                total = float(myCart[0].total.strip('$'))
                total += float(songSelected.price.strip('$'))

            else:
                name = name.replace('remove', '', 1)
                songSelected = ndb.Key(urlsafe=name).get()
                pos =0
                for currSongs in myCart[0].songs:
                    if currSongs.name == songSelected.name:
                        break
                    pos += 1
                del myCart[0].songs[pos]

                total = float(myCart[0].total.strip('$'))
                total -= float(songSelected.price.strip('$'))
            myCart[0].total = '${:0,.2f}'.format(total)


        myCart[0].put()

        self.redirect('/cart')

class Thanks(webapp2.RequestHandler):
    def get(self):
        url = users.create_logout_url(self.request.uri)
        urlLinktext = 'Logout'
        template_values = {
            'url': url,
            'url_linktext': urlLinktext
        }
        template = JINJA_ENVIRONMENT.get_template('thankYou.html')
        self.response.write(template.render(template_values))





app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/genre',Genre),
    ('/song',SongTest),
    ('/search',Search),
    ('/cart',Cart),
    ('/thankYou',Thanks)
], debug=True)