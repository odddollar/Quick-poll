import bottle
import redis
import random
import string

# create bottle app and redis connection
app = bottle.Bottle()
con = redis.Redis(host="redis", port=6379)

@app.route("/")
def home():
    option_data = {"option1": con.get("option1") if con.get("option1") != None else 0, 
                   "option2": con.get("option2") if con.get("option2") != None else 0, 
                   "option3": con.get("option3") if con.get("option3") != None else 0, 
                   "option4": con.get("option4") if con.get("option4") != None else 0}

    return bottle.template("home.html", submitted=bottle.request.get_cookie("visited"), **option_data)

@app.route("/", method="POST")
def home_submit():
    option = bottle.request.forms.options

    con.incr(option)

    bottle.response.set_cookie("visited", "true")
    return bottle.redirect("/")

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
    id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(id_length))
    while id in con.keys():
        id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(id_length))

    # iterate through keys in data dictionary and append to redis server
    for field in data.keys():
        con.hset(id, field, data[field])
        
        # if the current field is an option field create corresponding field to keep track of tally
        if "option" in field:
            con.hset(id, f"{field}_tally", 0)

    # render completed page with link to new poll
    return bottle.template("created.html", id=id)

# run app
bottle.run(app, host="0.0.0.0", port=8080, debug=True)
