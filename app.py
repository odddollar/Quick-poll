import bottle
import redis
import random
import string

# create bottle app and redis connection
app = bottle.Bottle()
con = redis.Redis(host="redis", port=6379)

# show home page with number of options for poll
@app.route("/")
def home():
    return bottle.template("home.html")

# handle postback and redirect to appropriate options page
@app.route("/", method="POST")
def home_submit():
    # get number of options and redirect
    options = bottle.request.forms.optnum

    return bottle.redirect(f"/create/{options}")

# show poll based on id
@app.route("/poll/<id:re:[0-9a-zA-Z]+>")
def poll(id):
    # get all data from redis and render template
    data = con.hgetall(id)

    return bottle.template("poll.html", data=data, id=id)

@app.route("/poll/<id:re:[0-9a-zA-Z]+>", method="POST")
def poll_submit(id):
    # get option selection
    selection = bottle.request.forms.option

    # increment value at the id hash and selection key
    con.hincrby(id, f"{selection}_tally", 1)

    # increment total field
    con.hincrby(id, "total", 1)

    # redirect to page to reload
    return bottle.redirect(f"/poll/{id}")

# show creation page with number of options specified
@app.route("/create/<options:re:[0-9]+>")
def create(options):
    return bottle.template("create.html", options=options)

# handle postback from creation page
@app.route("/create", method="POST")
def create_submit():
    # change length of id
    id_length = 7

    # get all data from page and append to dictionary
    data = {}
    for field in bottle.request.forms.keys():
        data[field] = bottle.request.forms.get(field)

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

# run app
bottle.run(app, host="0.0.0.0", port=8080, debug=True)
