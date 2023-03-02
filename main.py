from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def main():
    cur = sqlite3.connect("/home/pi/projects/fartbot/fartstreak.db").cursor()
    res = cur.execute('SELECT * FROM fartstreak').fetchall()
    rend = sorted(res, key=lambda x: x[5])
    out = rend[::-1]
    #print(type(out))
    #print(type(rend))
    #rend = res.sort(key = lambda x: x[5])
    return render_template("main.html", Database = out)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000, url_scheme='https')
    #app.run( host='0.0.0.0', port=80)