import bottle
import redis

app = bottle.Bottle()
con = redis.Redis(host="redis", port=6379)

@app.route("/")
def home():
    if bottle.request.get_cookie("visited"):
        return bottle.template("home.html", submitted=True)
    else:
        option_data = {"option1": con.get("option1"), "option2": con.get("option2"), "option3": con.get("option3"), "option4": con.get("option4"),}
        return bottle.template("home.html", submitted=False, **option_data)

@app.route("/", method="POST")
def home_submit():
    bottle.response.set_cookie("visited", "true")
    return bottle.redirect("/")

bottle.run(app, host="0.0.0.0", port=8080, debug=True)
