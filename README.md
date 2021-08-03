# CS50 final project - Gather Manager
#### Video demo: https://youtu.be/rgtzk0KJcn8

This project is a webapp that helps users to schedule meetings in such a manner that all invitees can meet without spreading COVID-19.This webapp has been implemented in Flask for the backend using Bootstrap for the frontend, building up the skills that CS50 has already taught me.<br/>

**Technologies used:**
1. Flask (for backend: requests and rendering webpages)
2. Jinja2 (for dynamically changing HTML files from within Python)
3. Werkzeug (for handling website security )
4. Flask-SQLAlchemy (for interfacing the webapp with the database)
5. Other miscellaneous libraries

##  How the website works

Using Gather Manager you have 4 main actions available:<br/>
1. Change your COVID status to one of the following (statuses can only be added in the past):
   - Vaccinated
   - Tested positive for COVID
   - Tested negative for COVID
2. Create a gathering and invite users. When adding the users to a meeting their statuses will be shown in order for the host to know which people can attend safely also having the ability to cancel if too few people can come.
3. Viewing the gatherings you're invited to, while also seeing the host's name and email to aid in planning the gathering.
4. Searching for users' profiles in order to view what gatherings the user is invited to, helping you plan around your invitees' availability.

### Routing
All routes (except for register and login) require the user to be logged in. There are 12 routes in total one of them (`/profile/<person_name>`) being dynamic in the sense that when a user navigates to a url of this type where `<person_name>` is the username of an actual user the user making the request will be presented with the profile page of the selected user.

### Session
When a user login his / her unique user id is stored in the session to verify the user identity when accessing specific routes. The session is also used as a cache for the create gathering functionality.<br/>
**The session is cleared when the user logs out.**

### Database
The database, powered by SQLite3 and interfaced with Python using Flask-SQLAlchemy, holds all the users' data. It is structured in 3 tables as follows:<br/>
1. `Users` table holds all of the users' information (id, username, email, gatherings to which the user received an invitation, user status history)
2. `User_history` table holds the users' COVID status history (id of status event, type of event, date of event, user id)
3. `Party` table hold all gathering information (gathering id, host name, host email, invitee id, gathering date)

### Future improvements
- Adding email notifications when a user is invited to gathering
- Adding the possibility to accept or reject an invitation
- Adding registration with Google account
- Adding ability to have a profile picture

## How to install
- Make sure you have Python3, Flask and Flask-SQLAlchemy installed on your computer
- Clone this repo `git clone https://github.com/victorbosneag/Gather_Manager.git`
- Run `python3 app.py`

