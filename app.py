import bottle
import redis
import random
import string
import os

# create bottle app and redis connection
app = bottle.Bottle()

# check if running on heroku
heroku = True if os.environ.get("APP_LOCATION") == "heroku" else False

# connect to required redis
if heroku:
    # connect to heroku redis
    con = redis.from_url(os.environ.get("REDIS_URL"))
else:
    # connect to local docker server
    con = redis.Redis(host="redis", port=6379)

# show home page with number of options for poll
@app.route("/")
def home():
    return bottle.template("home.html")

# handle postback and redirect to appropriate options page
@app.route("/", method="POST")
def home_submit():
    # change length of id
    id_length = 7

    # get all data from page and append to dictionary
    data = {}
    for field in bottle.request.forms.keys():
        data[field] = bottle.request.forms.get(field)

    # check all data is present
    for field in data.keys():
        if data[field] == "":
            return bottle.redirect(f"/create/{len(data)-1}")

    # create id and check that it isnt in use
    id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(id_length))
    while id in con.keys():
        id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(id_length))

    # iterate through keys in data dictionary and append to redis server
    for field in data.keys():
        con.hset(id, field, data[field])
        
        # if the current field is an option field create corresponding field to keep track of tally
        if "option" in field:
            con.hset(id, f"{field}_tally", 0)

    # create total field to keep track of total votes
    con.hset(id, "total", 0)

    # render completed page with link to new poll
    return bottle.template("created.html", id=id)

# show poll based on id
@app.route("/poll/<id:re:[0-9a-zA-Z]+>")
def poll(id):
    # get all data from redis and render template
    data = con.hgetall(id)

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

# host static javascript
@app.route("/static/main.js")
def static_js():
    return bottle.static_file("main.js", root="static/")

# run app
if heroku:
    bottle.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    bottle.run(app, host="0.0.0.0", port=8080, debug=True)
