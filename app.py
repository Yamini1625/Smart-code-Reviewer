from flask import Flask, render_template, request
from analyzer import analyze_code

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    analysis_result = []
    code = ""

    if request.method == "POST":
        code = request.form["code"]
        analysis_result = analyze_code(code)

    return render_template("index.html", result=analysis_result, code=code)

if __name__ == "__main__":
    app.run(debug=True)
