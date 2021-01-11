#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(500))    
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))    
    shows = db.relationship('Show', backref='show_venue', cascade="all, delete-orphan", lazy=True)

    def as_dict(self):
      return {c.name: getattr(self, c.name) for c in self.__table__.columns}    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='show_artist', cascade="all, delete-orphan", lazy='dynamic')

    def as_dict(self):
      return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def as_dict(self):
      return {c.name: getattr(self, c.name) for c in self.__table__.columns}


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  venues = Venue.query.group_by(Venue.id, Venue.state).all()
  current_state = ""
  current_city = ""
  data = []
  main_dictionary = {}
  venue_dictionary = {}
  num_upcoming_shows = 0
  print (len(venues))
  
  for venue in venues: 
    print (venues.index(venue))
    if (current_state != venue.state):
      if (current_state != ""):
        data.append(main_dictionary)
        main_dictionary = {}
        venue_dictionary = {}
        num_upcoming_shows = 0
      else:
        main_dictionary = {}
        venue_dictionary = {}
        num_upcoming_shows = 0        

      current_state = venue.state   
      current_city = venue.city

      main_dictionary["city"] = venue.city     
      main_dictionary["state"] = venue.state
      main_dictionary["venues"] = []


      venue_dictionary["id"] = venue.id
      venue_dictionary["name"] = venue.name

      venue_show=Show.query.filter_by(venue_id=venue.id)
      if (venue_show.first()): 
        for show in venue_show:
          if (show.start_time > datetime.today()):
            num_upcoming_shows += 1
      venue_dictionary["num_upcoming_shows"] = num_upcoming_shows
      
      main_dictionary["venues"].append(venue_dictionary)

      if (venues.index(venue) == len(venues)-1):
        data.append(main_dictionary)

    else:
      venue_dictionary = {}
      venue_dictionary["id"] = venue.id
      venue_dictionary["name"] = venue.name

      venue_show=Show.query.filter_by(venue_id=venue.id)
      if (venue_show.first()): 
        for show in venue_show:
          if (show.start_time > datetime.today()):
            num_upcoming_shows += 1
      venue_dictionary["num_upcoming_shows"] = num_upcoming_shows

      main_dictionary["venues"].append(venue_dictionary)
      
 
      
      

  """   data=[{
      "city": "San Francisco",
      "state": "CA",
      "venues": [{
        "id": 1,
        "name": "The Musical Hop",
        "num_upcoming_shows": 0,
      }, {
        "id": 3,
        "name": "Park Square Live Music & Coffee",
        "num_upcoming_shows": 1,
      }]
    }, {
      "city": "New York",
      "state": "NY",
      "venues": [{
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "num_upcoming_shows": 0,
      }]
    }] """
  #print (data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  responce = {}
  data_list = []
  venue_dictionary = {}
  num_upcoming_shows = 0

  search_term = request.form["search_term"]
  search = "%{}%".format(search_term)
  venues = Venue.query.filter(Venue.name.ilike(search))

  responce["count"] = venues.count()
  responce["data"] = []

  for venue in venues:
    venue_dictionary = {}
    num_upcoming_shows = 0
    venue_dictionary["id"] = venue.id
    venue_dictionary["name"] = venue.name

    venue_show=Show.query.filter_by(venue_id=venue.id)
    if (venue_show.first()): 
      for show in venue_show:
        if (show.start_time > datetime.today()):
          num_upcoming_shows += 1
    venue_dictionary["num_upcoming_shows"] = num_upcoming_shows

    data_list.append(venue_dictionary)

  responce["data"] = data_list

  """   response={
      "count": 1,
      "data": [{
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "num_upcoming_shows": 0,
      }]
    } """
  return render_template('pages/search_venues.html', results=responce, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue_show=Show.query.filter_by(venue_id=venue_id)
  venue = Venue.query.filter_by(id=venue_id).first()
  upcoming_shows = []
  past_shows = []

  if (venue_show.first()): 
    for show in venue_show: 
      if (show.start_time < datetime.today()):
        artist_show = Artist.query.filter_by(id=show.artist_id).first()
        show_dictionary = {
          "artist_id" : artist_show.id, 
          "artist_name" : artist_show.name,
          "artist_image_link" : artist_show.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        }
        past_shows.append(show_dictionary)
      else:
        artist_show = Artist.query.filter_by(id=show.artist_id).first()
        show_dictionary = {
          "artist_id" : artist_show.id, 
          "artist_name" : artist_show.name,
          "artist_image_link" : artist_show.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        }
        upcoming_shows.append(show_dictionary)
  
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.replace("{","").replace("}","").split(","),
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }  

  """   data1={
      "id": 1,
      "name": "The Musical Hop",
      "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
      "address": "1015 Folsom Street",
      "city": "San Francisco",
      "state": "CA",
      "phone": "123-123-1234",
      "website": "https://www.themusicalhop.com",
      "facebook_link": "https://www.facebook.com/TheMusicalHop",
      "seeking_talent": True,
      "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
      "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "past_shows": [{
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
      }],
      "upcoming_shows": [],
      "past_shows_count": 1,
      "upcoming_shows_count": 0,
    }
    data2={
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "genres": ["Classical", "R&B", "Hip-Hop"],
      "address": "335 Delancey Street",
      "city": "New York",
      "state": "NY",
      "phone": "914-003-1132",
      "website": "https://www.theduelingpianos.com",
      "facebook_link": "https://www.facebook.com/theduelingpianos",
      "seeking_talent": False,
      "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
      "past_shows": [],
      "upcoming_shows": [],
      "past_shows_count": 0,
      "upcoming_shows_count": 0,
    }
    data3={
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
      "address": "34 Whiskey Moore Ave",
      "city": "San Francisco",
      "state": "CA",
      "phone": "415-000-1234",
      "website": "https://www.parksquarelivemusicandcoffee.com",
      "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
      "seeking_talent": False,
      "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "past_shows": [{
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
      }],
      "upcoming_shows": [{
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
      }, {
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
      }, {
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
      }],
      "past_shows_count": 1,
      "upcoming_shows_count": 1,
    }
    data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0] """
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  image_link = request.form['image_link']
  website = request.form['website']
  seeking_description = request.form['seeking_description']
  if (request.form['seeking_talent'] == "y"):
    seeking_talent = True
  else:
    seeking_talent = False
  facebook_link = request.form['facebook_link']
  genres = request.form.getlist('genres')
  try:
    venue = Venue(name=name,city=city,state=state,image_link=image_link, website=website,seeking_description=seeking_description,seeking_talent=seeking_talent,address=address,phone=phone,facebook_link=facebook_link, genres=genres)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def post_venue(venue_id):
  if (request.form['method'] == "DELETE"):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash('Venue ' + venue_id + ' was successfully deleted!')
    except:
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      db.session.rollback()
      flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
    finally:
      db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()
  #print (data)
  """   data=[{
      "id": 4,
      "name": "Guns N Petals",
    }, {
      "id": 5,
      "name": "Matt Quevedo",
    }, {
      "id": 6,
      "name": "The Wild Sax Band",
    }] """
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  responce = {}
  data_list = []
  artist_dictionary = {}
  num_upcoming_shows = 0

  search_term = request.form["search_term"]
  search = "%{}%".format(search_term)
  artists = Artist.query.filter(Artist.name.ilike(search))

  responce["count"] = artists.count()
  responce["data"] = []

  for artist in artists:
    artist_dictionary = {}
    num_upcoming_shows = 0
    artist_dictionary["id"] = artist.id
    artist_dictionary["name"] = artist.name

    artist_show=Show.query.filter_by(artist_id=artist.id)
    if (artist_show.first()): 
      for show in artist_show:
        if (show.start_time > datetime.today()):
          num_upcoming_shows += 1
    artist_dictionary["num_upcoming_shows"] = num_upcoming_shows

    data_list.append(artist_dictionary)

  responce["data"] = data_list

  """   response={
      "count": 1,
      "data": [{
        "id": 4,
        "name": "Guns N Petals",
        "num_upcoming_shows": 0,
      }]
    } """
  return render_template('pages/search_artists.html', results=responce, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist_show=Show.query.filter_by(artist_id=artist_id)
  artist = Artist.query.filter_by(id=artist_id).first()
  upcoming_shows = []
  past_shows = []

  if (artist_show.first()): 
    for show in artist_show: 
      if (show.start_time < datetime.today()):
        venue_show = Venue.query.filter_by(id=show.venue_id).first()
        show_dictionary = {
          "venue_id" : venue_show.id, 
          "venue_name" : venue_show.name,
          "venue_image_link" : venue_show.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        }
        past_shows.append(show_dictionary)
      else:
        venue_show = Venue.query.filter_by(id=show.venue_id).first()
        show_dictionary = {
          "venue_id" : venue_show.id, 
          "venue_name" : venue_show.name,
          "venue_image_link" : venue_show.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        }
        upcoming_shows.append(show_dictionary)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.replace("{","").replace("}","").split(","),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }  

  """   data1={
      "id": 4,
      "name": "Guns N Petals",
      "genres": ["Rock n Roll"],
      "city": "San Francisco",
      "state": "CA",
      "phone": "326-123-5000",
      "website": "https://www.gunsnpetalsband.com",
      "facebook_link": "https://www.facebook.com/GunsNPetals",
      "seeking_venue": True,
      "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
      "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "past_shows": [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "start_time": "2019-05-21T21:30:00.000Z"
      }],
      "upcoming_shows": [],
      "past_shows_count": 1,
      "upcoming_shows_count": 0,
    }
    data2={
      "id": 5,
      "name": "Matt Quevedo",
      "genres": ["Jazz"],
      "city": "New York",
      "state": "NY",
      "phone": "300-400-5000",
      "facebook_link": "https://www.facebook.com/mattquevedo923251523",
      "seeking_venue": False,
      "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "past_shows": [{
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
      }],
      "upcoming_shows": [],
      "past_shows_count": 1,
      "upcoming_shows_count": 0,
    }
    data3={
      "id": 6,
      "name": "The Wild Sax Band",
      "genres": ["Jazz", "Classical"],
      "city": "San Francisco",
      "state": "CA",
      "phone": "432-325-5432",
      "seeking_venue": False,
      "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "past_shows": [],
      "upcoming_shows": [{
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
      }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
      }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
      }],
      "past_shows_count": 0,
      "upcoming_shows_count": 3,
    }
    data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0] """
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id).as_dict()
  
  """   artist={
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
      }  """
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    artist.genres = request.form.getlist('genres')   
    artist.website = request.form['website']   
    artist.image_link = request.form['image_link']
    artist.seeking_description = request.form['seeking_description']
    if (request.form['seeking_venue'] == "y"):
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False
    db.session.commit()
    flash('Artist ' + str(artist_id) + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + str(artist_id) + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id).as_dict()
  """   venue={
      "id": 1,
      "name": "The Musical Hop",
      "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
      "address": "1015 Folsom Street",
      "city": "San Francisco",
      "state": "CA",
      "phone": "123-123-1234",
      "website": "https://www.themusicalhop.com",
      "facebook_link": "https://www.facebook.com/TheMusicalHop",
      "seeking_talent": True,
      "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
      "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    } """
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    venue.genres = request.form.getlist('genres')  
    venue.website = request.form['website']   
    venue.image_link = request.form['image_link']
    venue.seeking_description = request.form['seeking_description']
    if (request.form['seeking_talent'] == "y"):
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False
    db.session.commit()
    flash('Venue ' + str(venue_id) + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + str(venue_id) + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  website = request.form['website']
  seeking_description = request.form['seeking_description']
  if (request.form['seeking_venue'] == "y"):
    seeking_venue = True
  else:
    seeking_venue = False  
  try:
    artist = Artist(name=name,city=city,state=state,website=website,seeking_description=seeking_description,seeking_venue=seeking_venue, phone=phone,facebook_link=facebook_link, image_link=image_link, genres=genres)
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = Show.query.all()
  data = []
  show_dictionary = {}

  for show in shows: 
    show_dictionary["venue_id"] = show.venue_id     
    show_dictionary["venue_name"] = Venue.query.get(show.venue_id).name
    show_dictionary["artist_id"] = show.artist_id
    show_dictionary["artist_name"] = Artist.query.get(show.artist_id).name
    show_dictionary["artist_image_link"] = Artist.query.get(show.artist_id).image_link
    show_dictionary["start_time"] = str(show.start_time)
    data.append(show_dictionary)  
  
  """   data=[{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }] """
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
  try:
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
   app.run(host='192.168.1.21')

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='192.168.1.21', port=port)
'''
