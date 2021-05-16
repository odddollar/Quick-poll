import bottle
import redis

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

@app.route("/create/<options:re:[0-9]+>")
def create(options):
    return bottle.template("create.html", options=options)

@app.route("/create", method="POST")
def create_submit():
    data = {}
    for field in bottle.request.forms.keys():
        data[field] = bottle.request.forms.get(field)

    with open("test.txt", "w") as file:
        file.write(str(data))

bottle.run(app, host="0.0.0.0", port=8080, debug=True)
