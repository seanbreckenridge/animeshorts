from flask import Flask, render_template, redirect, request

templates_dir = "templates"

app = Flask(__name__, template_folder=templates_dir)


@app.route("/", methods=["GET"])
def index():
    if not request.args:
        return render_template("index_rec.html")
    else:
        if "sort" in request.args and request.args["sort"] == "Date Added":
            return render_template("index_newest.html")
        else:
            return render_template("index_rec.html")


@app.route("/people")
def people():
    return render_template("people.html")


@app.route("/list")
def route_to_list():
    return redirect("./", code=302)


if __name__ == "__main__":
    app.run(debug=False)
