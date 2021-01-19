#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  jsonify, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import db,Venue,Artist,Show
from sqlalchemy import func
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)


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
  venues = db.session.query(Venue.id, Venue.name, Venue.city, Venue.state,Show.start_time).outerjoin(Show, Venue.id == Show.venue_id).group_by(Venue.id, Venue.name,Venue.city, Show.start_time).order_by(Venue.city,Venue.name).all()
 
  data = []
  main_dictionary = {}
  venue_dictionary = {}
  current_city = ""
  current_venue = ""
  num_upcoming_shows = 0


  for venue in venues:
    if (current_city != venue.city):
      if (current_city != ""): 
        main_dictionary["venues"].append(venue_dictionary)
        data.append(main_dictionary)
        main_dictionary = {}
        venue_dictionary = {}
        current_city = ""
        current_venue = ""
        num_upcoming_shows = 0      
        
        current_city = venue.city
        current_venue = venue.name
        
        main_dictionary["city"] = venue.city     
        main_dictionary["state"] = venue.state
        main_dictionary["venues"] = []

        venue_dictionary["id"] = venue.id
        venue_dictionary["name"] = venue.name

        if (venue.start_time is None):
          num_upcoming_shows = 0
        else:
          if (venue.start_time > datetime.now()): 
            num_upcoming_shows += 1
        
        venue_dictionary["num_upcoming_shows"] = num_upcoming_shows 
      else:
        current_city = venue.city
        current_venue = venue.name
        
        main_dictionary["city"] = venue.city     
        main_dictionary["state"] = venue.state
        main_dictionary["venues"] = []

        venue_dictionary["id"] = venue.id
        venue_dictionary["name"] = venue.name

        if (venue.start_time is None):
          num_upcoming_shows = 0

        else:
          if (venue.start_time > datetime.now()): 
            num_upcoming_shows += 1    
        
        venue_dictionary["num_upcoming_shows"] = num_upcoming_shows    
    else:
      if (current_venue != venue.name):
        venue_dictionary["num_upcoming_shows"] = num_upcoming_shows
        main_dictionary["venues"].append(venue_dictionary)
        venue_dictionary = {}
        current_venue = ""
        num_upcoming_shows = 0     
        
        current_venue = venue.name
        
        venue_dictionary["id"] = venue.id
        venue_dictionary["name"] = venue.name         

        if (venue.start_time is None):
          num_upcoming_shows = 0
        else:
          if (venue.start_time > datetime.now()): 
            num_upcoming_shows += 1    
        
        venue_dictionary["num_upcoming_shows"] = num_upcoming_shows
      
      else:
        if (venue.start_time is None):
          num_upcoming_shows = 0
        else:
          if (venue.start_time > datetime.now()): 
            num_upcoming_shows += 1    
                     
        venue_dictionary["num_upcoming_shows"] = num_upcoming_shows

  main_dictionary["venues"].append(venue_dictionary)
  data.append(main_dictionary)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  responce = {}


  search_term = request.form["search_term"]
  search = "%{}%".format(search_term)
  venues = db.session.query(Venue.id, Venue.name, Venue.city, Venue.state, Show.start_time).filter(Venue.name.ilike(search)).outerjoin(Show, Venue.id == Show.venue_id).group_by(Venue.id, Venue.state, Show.start_time).order_by(Venue.state)

  data = []
  venue_dictionary = {}
  current_venue = ""
  num_upcoming_shows = 0
  venues_count = 0

  for venue in venues.all():

    if (current_venue != venue.name):
      if (current_venue == ""):
        venues_count += 1
        current_venue = venue.name
        venue_dictionary["id"] = venue.id
        venue_dictionary["name"] = venue.name  

        if (venue.start_time is None):
          num_upcoming_shows = 0
        else:
          if (venue.start_time > datetime.now()): 
            num_upcoming_shows += 1    
          
        venue_dictionary["num_upcoming_shows"] = num_upcoming_shows
      
      else:
        venues_count += 1
        data.append(venue_dictionary)
        venue_dictionary = {}
        
        current_venue = venue.name
        
        venue_dictionary["id"] = venue.id
        venue_dictionary["name"] = venue.name  

        if (venue.start_time is None):
          num_upcoming_shows = 0
        else:
          if (venue.start_time > datetime.now()): 
            num_upcoming_shows += 1    
          
        venue_dictionary["num_upcoming_shows"] = num_upcoming_shows

    else:

      if (venue.start_time is None):
        num_upcoming_shows = 0
      else:
        if (venue.start_time > datetime.now()): 
          num_upcoming_shows += 1    
          
      venue_dictionary["num_upcoming_shows"] = num_upcoming_shows
 
    
  data.append(venue_dictionary)
  responce["data"] = data
  responce["count"] = venues_count
  return render_template('pages/search_venues.html', results=responce, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()

  if (venue): 
    venue_show = db.session.query(Artist.id, Artist.name, Artist.image_link, Show.venue_id, Show.start_time).outerjoin(Show, Artist.id == Show.artist_id).filter(Show.venue_id == venue_id)
    upcoming_shows = []
    past_shows = []
    for show in venue_show: 
      if (show.start_time < datetime.now()):
        show_dictionary = {
          "artist_id" : show.id, 
          "artist_name" : show.name,
          "artist_image_link" : show.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        }
        past_shows.append(show_dictionary)
      else:
        show_dictionary = {
          "artist_id" :show.id, 
          "artist_name" : show.name,
          "artist_image_link" : show.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        }
        upcoming_shows.append(show_dictionary)
    
    data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.replace("{","").replace("}","").split(","),
      "address": venue.address,
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
    return render_template('pages/show_venue.html', venue=data)        
  else:
    return render_template('errors/404.html')

  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  form = VenueForm(request.form)
  try:
      venue = Venue()
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
  finally:
      db.session.close()
  
  return render_template('pages/home.html')


@app.route('/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
  if (request.form['method'] == "DELETE"):
    try:
      artist = Artist.query.get(artist_id)
      db.session.delete(artist)
      db.session.commit()
      flash('Artist ' + artist_id + ' was successfully deleted!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + artist_id + ' could not be deleted.')
    finally:
      db.session.close()

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def post_venue(venue_id):
  if (request.form['method'] == "DELETE"):
    try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash('Venue ' + venue_id + ' was successfully deleted!')
    except:

      db.session.rollback()
      flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
    finally:
      db.session.close()

    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data= Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  responce = {}

  search_term = request.form["search_term"]
  search = "%{}%".format(search_term)
  
  artists = db.session.query(Artist.id, Artist.name, Show.start_time).filter(Artist.name.ilike(search)).outerjoin(Show, Artist.id == Show.artist_id).group_by(Artist.id, Show.id, Show.start_time)  
  
  
  data = []
  artist_dictionary = {}
  current_artist = ""
  num_upcoming_shows = 0
  artists_count = 0

  for artist in artists.all():

    if (current_artist != artist.name):
      if (current_artist == ""):
        artists_count += 1
        current_artist = artist.name
        artist_dictionary["id"] = artist.id
        artist_dictionary["name"] = artist.name  

        if (artist.start_time is None):
          num_upcoming_shows = 0
        else:
          if (artist.start_time > datetime.now()): 
            num_upcoming_shows += 1    
          
        artist_dictionary["num_upcoming_shows"] = num_upcoming_shows
      
      else:
        artists_count += 1
        data.append(artist_dictionary)
        artist_dictionary = {}
        
        current_artist = artist.name
        
        artist_dictionary["id"] = artist.id
        artist_dictionary["name"] = artist.name  

        if (artist.start_time is None):
          num_upcoming_shows = 0
        else:
          if (artist.start_time > datetime.now()): 
            num_upcoming_shows += 1    
          
        artist_dictionary["num_upcoming_shows"] = num_upcoming_shows

    else:

      if (artist.start_time is None):
        num_upcoming_shows = 0
      else:
        if (artist.start_time > datetime.now()): 
          num_upcoming_shows += 1    
          
      artist_dictionary["num_upcoming_shows"] = num_upcoming_shows
 
    
  data.append(artist_dictionary)
  responce["data"] = data
  responce["count"] = artists_count

  return render_template('pages/search_artists.html', results=responce, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()

  if (artist): 
    artist_show = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.artist_id, Show.start_time).outerjoin(Show, Venue.id == Show.venue_id).filter(Show.artist_id == artist_id).all()
    upcoming_shows = []
    past_shows = []
    for show in artist_show: 
      if (show.start_time < datetime.now()):
        show_dictionary = {
          "venue_id" : show.id, 
          "venue_name" : show.name,
          "venue_image_link" : show.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        }
        past_shows.append(show_dictionary)
      else:
        show_dictionary = {
          "venue_id" :show.id, 
          "venue_name" : show.name,
          "venue_image_link" : show.image_link,
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
    return render_template('pages/show_artist.html', artist=data)        
  else:
    return render_template('errors/404.html')


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id).as_dict()
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  try:
    artist = Artist.query.get(artist_id)
    if ('name' in request.form): artist.name = request.form['name']
    if ('city' in request.form): artist.city = request.form['city']
    if ('state' in request.form): artist.state = request.form['state']
    if ('phone' in request.form): artist.phone = request.form['phone']
    if ('facebook_link' in request.form): artist.facebook_link = request.form['facebook_link']
    if ('genres' in request.form): artist.genres = request.form.getlist('genres')   
    if ('website' in request.form): artist.website = request.form['website']   
    if ('image_link' in request.form): artist.image_link = request.form['image_link']
    if ('seeking_description' in request.form): artist.seeking_description = request.form['seeking_description']
    if ('seeking_venue' in request.form):
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

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  try:
    venue = Venue.query.get(venue_id)
    if ('name' in request.form): venue.name = request.form['name']  
    if ('city' in request.form): venue.city = request.form['city']
    if ('state' in request.form): venue.state = request.form['state']
    if ('phone' in request.form): venue.phone = request.form['phone']
    if ('facebook_link' in request.form): venue.facebook_link = request.form['facebook_link']
    if ('genres' in request.form): venue.genres = request.form.getlist('genres')  
    if ('website' in request.form): venue.website = request.form['website']   
    if ('image_link' in request.form): venue.image_link = request.form['image_link']
    if ('seeking_description' in request.form): venue.seeking_description = request.form['seeking_description']
    if ('seeking_talent' in request.form):
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

  form = ArtistForm(request.form)
  try:
      artist = Artist()
      form.populate_obj(artist)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
  finally:
      db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows = Show.query.all()
  data = []
  
  for show in shows: 
    show_dictionary = {}
    show_dictionary["venue_id"] = show.venue_id     
    show_dictionary["venue_name"] = Venue.query.get(show.venue_id).name
    show_dictionary["artist_id"] = show.artist_id
    show_dictionary["artist_name"] = Artist.query.get(show.artist_id).name
    show_dictionary["artist_image_link"] = Artist.query.get(show.artist_id).image_link
    show_dictionary["start_time"] = str(show.start_time)
    data.append(show_dictionary)  
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm(request.form)
  try:
      show = Show()
      form.populate_obj(show)
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
  except:
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
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
