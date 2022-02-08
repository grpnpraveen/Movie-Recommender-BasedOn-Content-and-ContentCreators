from flask import Flask,render_template,Response,request,redirect,url_for,jsonify
from mainfunctionforneo4j import automate,getmovieinfo
app = Flask(__name__, template_folder='./templates')

# Main Code
global searchText,paraStart
searchText=None
paraStart=None
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showResults',methods=['POST','GET'])
def showResults():
    global searchText,paraStart
    if request.method== 'POST':
        searchText=request.form.get('searchtext')
        paraStart=searchText.find("(")
        search_movie=searchText[:paraStart]
        search_year=searchText[paraStart+1:-1]
        search_year=int(search_year)
        print(search_movie)
        print(search_year)
        automate(search_movie,search_year)
        print("In side app.py")
    return render_template('results.html')

@app.route('/movieinfo/<id>')
def movieinfo(id):
    getmovieinfo(id)
    return render_template('movieinfo.html')


if (__name__=='__main__'):
    # dbname = get_database()
    app.run(debug=True)