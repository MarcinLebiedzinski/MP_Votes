from flask import Flask, render_template, request, url_for



app = Flask(__name__)


@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template('index.html')
    else:
        pass  
    
if __name__ == "__main__":
    app.run(debug=True)










    
    