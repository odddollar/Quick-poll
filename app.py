import bottle
import redis

app = bottle.Bottle()
redis_con = redis.Redis(host="redis", port=6379)

@app.route("/")
def home():
    if bottle.request.get_cookie("visited"):
        return bottle.template("home.html", submitted=True)
    else:
        return bottle.template("home.html", submitted=False)

@app.route("/", method="POST")
def home_submit():
    bottle.response.set_cookie("visited", "true")
    return bottle.redirect("/")

bottle.run(app, host="0.0.0.0", port=8080, debug=True)
