from flask import Flask,render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
# from config import Config
from collections import OrderedDict
import pymongo

app = Flask(__name__)
# db = SQLAlchemy(app)

@app.route('/', methods=["GET","POST"])
def index():
    return render_template('./index.html')

@app.route('/login', methods=["GET","POST"])
def login():
    # print("Fuck me")
    username = request.form['username']
    password = request.form['password']
    client = pymongo.MongoClient("mongodb+srv://ynyhxfo:ynyhxfozdm@cluster0-vnoyt.mongodb.net/test?retryWrites=true")
    db = client.web
    movieList = [movie for movie in db.movie.find()]
    musicList = [music for music in db.music.find()]
    collection = db.user
    userInf = collection.find_one({"username":username,"password":password})
    if userInf:
        movie_with_genre = userInf['movie_with_genre']
        music_with_type = userInf['music_with_type']
        movie_scores=[]
        music_scores=[]
        movie_history_scores=[]
        music_history_scores=[]
        userInf = dict(userInf)
        for movie in movieList:
            score = movie['IMDB_Score']/3
            if movie['Date']>=1995:
                time = 'vintage'
            else:
                time = 'modern'
            if time in userInf['movie_time']:
                score+=1
            if movie['Duration']>=140:
                Duration = 'long'
            elif movie['Duration']>=120:
                Duration = 'medium'
            else:
                Duration = 'short'
            if Duration in userInf['duration']:
                score+=1
            for genre in movie['genre']:
                if genre in userInf['movie_genre']:
                    score+=1
            if movie['Language'].lower() in [each.lower() for each in userInf['movie_language']]:
                score+=1
            movie_scores.append(([movie['Title']], float(round(score,1))))
        for music in musicList:
            score = music['score']/3
            if music['Language'].lower() in [each.lower() for each in userInf['music_language']]:
                score+=2
            if music['type'] in userInf['music_type']:
                score+=1
            music_scores.append(([music['Song']], float(round(score,1))))            
        for movie in movieList:
            score = movie['IMDB_Score']/3
            for genre in movie['genre']:
                if genre in userInf['movie_history']:
                    score+=2
            movie_history_scores.append(([movie['Title']], float(round(score,1))))
        for music in musicList:
            score = music['score']/3
            if music['type'] in userInf['music_history']:
                score+=2
            music_history_scores.append(([music['Song']], float(round(score,1))))
        movie_scores = sorted(movie_scores,key=lambda x:x[1], reverse=True)
        music_scores = sorted(music_scores,key=lambda x:x[1], reverse=True)
        movie_history_scores = sorted(movie_history_scores,key=lambda x:x[1], reverse=True)
        music_history_scores = sorted(music_history_scores,key=lambda x:x[1], reverse=True)
        # print(music_scores)
        # print(music_history_scores)
        guess_you_like_movie = []
        guess_you_like_music = []
        guess_you_like_movie_history = []
        guess_you_like_music_history = []
        for i in range(20):
            if movie_scores[i][1]>4.5 or i<=4:
                guess_you_like_movie.append(movie_scores[i])
            else:
                break
        for i in range(40):
            if music_scores[i][1]>5 or i<=6:
                guess_you_like_music.append(music_scores[i])
            else:
                break
        for i in range(20):
            if movie_history_scores[i][1]>4.5 or i<=4:
                guess_you_like_movie_history.append(movie_history_scores[i])
            else:
                break
        for i in range(40):
            if music_history_scores[i][1]>5 or i<=6:
                guess_you_like_music_history.append(music_history_scores[i])
            else:
                break
        return render_template('./main.html',userInf = userInf, movieList = movieList, musicList = musicList, guess_you_like_movie = guess_you_like_movie, guess_you_like_music=guess_you_like_music, guess_you_like_movie_history=guess_you_like_movie_history, guess_you_like_music_history=guess_you_like_music_history,movie_with_genre=movie_with_genre,music_with_type = music_with_type)
    else:
        return render_template('./wrong_pass.html')

@app.route('/sign_up')
def sign_up():
    return render_template('./sign_up.html')

@app.route('/create_user', methods=["GET","POST"])
def create_user():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    re_password = request.form['re_password']
    cur_user = {'username':username,'password':password,'email':email,'movie_history':[],'music_history':[],'movie_with_genre':[], 'music_with_type':[]}
    client = pymongo.MongoClient("mongodb+srv://ynyhxfo:ynyhxfozdm@cluster0-vnoyt.mongodb.net/test?retryWrites=true")
    db = client.web
    collection = db.user
    if collection.find_one({'username':username}):
        return 'Username is already exist'
    if password!=re_password:
        return 'please check the password'
    collection.insert_one(cur_user)
    return render_template('./success_signup.html')

@app.route('/insert_preference', methods=["GET","POST"])
def insert_preference():
    dataDict = dict(request.form)
    username = request.form['username']
    dataDict['username'] = username
    client = pymongo.MongoClient("mongodb+srv://ynyhxfo:ynyhxfozdm@cluster0-vnoyt.mongodb.net/test?retryWrites=true")
    db = client.web
    collection = db.user
    collection.update_one({'username':username},{'$set':dataDict})
    # return render_template('./index.html')

@app.route('/movie/<movie>/<user>',methods=["GET","POST"])
def movie(movie,user):
    client = pymongo.MongoClient("mongodb+srv://ynyhxfo:ynyhxfozdm@cluster0-vnoyt.mongodb.net/test?retryWrites=true")
    db = client.web
    collection = db.movie
    genre = collection.find_one({'Title':movie})['genre'][0]
    userD = db.user.find_one({'username':user})
    if len(userD['movie_with_genre']) == 10:
        userD['movie_with_genre'].pop()
    userD['movie_with_genre'] = [(movie,genre)]+userD['movie_with_genre']
    # print(userD['movie_with_genre'])
    if genre in userD['movie_history']:
        pass
    if genre not in userD['movie_history']:
        if len(userD['movie_history']) == 2:
            userD['movie_history'].pop(0)
        userD['movie_history'].append(genre)
    db.user.update_one({'username':user},{'$set':userD})
    # print(db.user.find_one({'username':user}))
    return render_template('./movie.html',movie=movie, background = genre)

@app.route('/music/<music>/<user>',methods=["GET","POST"])
def music(music,user):
    client = pymongo.MongoClient("mongodb+srv://ynyhxfo:ynyhxfozdm@cluster0-vnoyt.mongodb.net/test?retryWrites=true")
    db = client.web
    collection = db.music
    type = collection.find_one({'Song':music})['type']
    background = db.Background.find_one({'Music':type})['Movie']
    # print(type)
    userD = db.user.find_one({'username':user})
    if len(userD['music_with_type']) == 10:
        userD['music_with_type'].pop()
    userD['music_with_type'] = [(music,type)]+userD['music_with_type']
    # print(userD['movie_with_genre'])
    if type in userD['music_history']:
        pass
    if type not in userD['music_history']:
        if len(userD['music_history']) == 2:
            userD['music_history'].pop(0)
        userD['music_history'].append(type)
    db.user.update_one({'username':user},{'$set':userD})
    # print(db.user.find_one({'username':user}))
    return render_template('./music.html',music=music,background=background)

if __name__ == '__main__':
    app.run(debug=True)