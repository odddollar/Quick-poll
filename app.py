import bottle
import redis
from random import choice
from string import ascii_letters, digits
from os import environ
from datetime import timedelta

# create bottle app and redis connection
app = bottle.Bottle()

# check if running on heroku
heroku = True if environ.get("APP_LOCATION") == "heroku" else False

# connect to required redis
if heroku:
    # connect to heroku redis
    con = redis.from_url(environ.get("REDIS_URL"))
else:
    # connect to local docker server
    con = redis.Redis(host="redis", port=6379)

# show home page with number of options for poll
@app.route("/")
def home():
    # ensure that https is used
    url = bottle.request.url
    if "https" not in url and heroku:
        return bottle.HTTPResponse(status=301, headers={"Location": url.replace("http", "https")})

    return bottle.template("home.html")

# handle postback and redirect to appropriate options page
@app.route("/", method="POST")
def home_submit():
    # change length of id
    id_length = 7

    # get all data from page and append to dictionary
    data = {}
    for field in bottle.request.forms.keys():
        # dont add expiration data to data dictionary
        if field != "expire":
            data[field] = bottle.request.forms.get(field)

    # add "secret" field if not present
    if "secret" not in data.keys():
        data["secret"] = "False"

    # create id and check that it isnt in use
    id = ''.join(choice(ascii_letters + digits) for _ in range(id_length))
    while id in con.keys():
        id = ''.join(choice(ascii_letters + digits) for _ in range(id_length))

    # iterate through keys in data dictionary and append to redis server
    for field in data.keys():
        con.hset(id, field, data[field])
        
        # if the current field is an option field create corresponding field to keep track of tally
        if "option" in field:
            con.hset(id, f"{field}_tally", 0)

    # create total field to keep track of total votes
    con.hset(id, "total", 0)

    # set key to auto-delete after X amount of time
    con.expire(id, timedelta(minutes=int(bottle.request.forms.expire)))

    # render completed page with link to new poll
    return bottle.template("created.html", id=id, url=bottle.request.url)

# show poll based on id
@app.route("/poll/<id:re:[0-9a-zA-Z]+>")
def poll(id):
    # ensure that https is used
    url = bottle.request.url
    if "https" not in url and heroku:
        return bottle.HTTPResponse(status=301, headers={"Location": url.replace("http", "https")})

    # get all data from redis and render template
    data = con.hgetall(id)

    # check that poll is valid
    if len(data.keys()) == 0:
        raise bottle.HTTPError(status=404, body=f"Not found '{'/'+'/'.join(str(bottle.request.url).split('/')[-2:])}'")

    # get voted cookie information
    voted = bottle.request.get_cookie(f"{id}_voted", default=False)

    return bottle.template("poll.html", data=data, id=id, voted=voted)

@app.route("/poll/<id:re:[0-9a-zA-Z]+>", method="POST")
def poll_submit(id):
    # get option selection
    selection = bottle.request.forms.option

    # check that valid data has been entered
    if selection != "":
        # increment value at the id hash and selection key
        con.hincrby(id, f"{selection}_tally", 1)

        # increment total field
        con.hincrby(id, "total", 1)

        # save cookie to prevent multiple votes
        bottle.response.set_cookie(f"{id}_voted", "True")

    # redirect to page to reload
    return bottle.redirect(f"/poll/{id}")

# show list of public polls
@app.route("/poll")
def poll_list():
    # ensure that https is used
    url = bottle.request.url
    if "https" not in url and heroku:
        return bottle.HTTPResponse(status=301, headers={"Location": url.replace("http", "https")})

    # get list of keys
    keys = con.keys()

    # create data dictionary
    data = {}

    # iterate through keys and get "secret" field from each
    for key in keys:
        secret = con.hget(key, "secret")

        # check if poll is secret, add if not
        if secret == b"False":
            data[key] = con.hgetall(key)

    # pass poll data to template
    return bottle.template("poll_list.html", data=data)

# run 404 error page
@app.error(404)
def error_404(error):
    return bottle.template("error.html", error=error)

# run 500 error page
@app.error(500)
def error_500(error):
    return bottle.template("error.html", error=error)

# host static files
@app.route("/static/<filename:re:.*\.(js|png|jpg|ico|css)>")
def static(filename):
    # ensure that https is used
    url = bottle.request.url
    if "https" not in url and heroku:
        return bottle.HTTPResponse(status=301, headers={"Location": url.replace("http", "https")})

    return bottle.static_file(filename, root="static/")

# run app
if heroku:
    bottle.run(app, host="0.0.0.0", port=int(environ.get("PORT", 5000)))
else:
    bottle.run(app, host="0.0.0.0", port=8080, debug=True)
