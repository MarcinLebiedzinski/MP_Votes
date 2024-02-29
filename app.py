from flask import Flask, render_template, request
import base64

from utils.utils import get_term_details, get_club_list, get_member_list, get_vote_list, get_vote_details, get_membervote_details, get_photo
from utils.utils import save_term_details, save_club_details, save_member_details, save_membervote_details, save_vote_details

from utils.utils import load_term_list, load_member_list, load_club_list, load_vote_list, load_membervote_list
from utils.utils import load_member_name

app = Flask(__name__)


@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template('index.html')
    else:
        pass  
    

@app.route("/load_to_db", methods=["GET", "POST"])
def load_to_db():
    if request.method == "GET":
        view = 'load_to_db'
        return render_template('load_to_db_form.html', view=view)
    else:
        approve = request.form['approve']
        if approve == 'Yes':
        
            for term in range (2, 9):
                term_details = get_term_details(term)
                save_term_details(term_details)

            for term in range(9, 11):
                term_details = get_term_details(term)
                save_term_details(term_details)
                
                club_list = get_club_list(term)
                save_club_details(club_list, term)

                member_list = get_member_list(term)
                save_member_details(member_list, term)

                vote_list = get_vote_list(term)
                vote_details = get_vote_details(vote_list, term)
                save_vote_details(vote_details)
                vote_list = get_vote_list(term)
                print(vote_list)
                membervote_details = get_membervote_details(vote_list, term)
                save_membervote_details(membervote_details)

            return render_template('load_to_db.html')
        else:
            return render_template('index.html')
        

@app.route("/terms", methods=["GET", "POST"])
def terms():
    if request.method == "GET":
        terms = load_term_list()
        return render_template('terms.html', terms=terms)
    else:
        pass  


@app.route("/clubs", methods=["GET", "POST"])
def clubs():
    if request.method == "GET":
        view = 'clubs'
        terms = [9, 10]
        return render_template('term_form.html', terms=terms, view=view)
    else:
        term = request.form['term']
        clubs = load_club_list(term)
        return render_template('clubs.html', clubs=clubs)


@app.route("/members", methods=["GET", "POST"])
def members():
    if request.method == "GET":
        view = 'members'
        terms = [9, 10]
        return render_template('term_form.html', terms=terms, view=view)
    else:
        term = request.form['term']
        members = load_member_list(term)
        return render_template('members.html', members=members, term=term)


@app.route("/votes", methods=["GET", "POST"])
def votes():
    if request.method == "GET":
        view = 'votes'
        terms = [9, 10]
        return render_template('term_form.html', terms=terms, view=view)
    else:
        term = request.form['term']
        votes = load_vote_list(term)
        return render_template('votes.html', votes=votes)
    
@app.route("/membervote", methods=["GET", "POST"])
def membervote():
    if request.method == "GET":
        view = 'membervote'
        terms = [9, 10]
        return render_template('term_form.html', terms=terms, view=view)
    else:
        term = request.form['term']
        members = load_member_list(term)
        return render_template('membervote.html', members=members, term=term)

@app.route("/voting/<term_id>/<member_id>", methods=["GET", "POST"])
def voting(term_id, member_id):
    if request.method == "GET":
        member = load_member_name(term_id, member_id)
        votes = load_membervote_list(term_id, member_id)
        return render_template('membervote_result.html', votes=votes, member=member, term=term_id)
    else:
        pass

@app.route("/member_details/<term_id>/<member_id>", methods=["GET", "POST"])
def member_details(term_id, member_id):
    if request.method == "GET":
        member = load_member_name(term_id, member_id)
        
        photo = get_photo(term_id, member_id)
        if photo is not None:
                photo_data = base64.b64encode(photo.photo).decode('ascii')

        return render_template('member_details.html', member=member, term=term_id, photo_data=photo_data)
    else:
        pass


if __name__ == "__main__":
    app.run(debug=True)


to_do = """
Proponowane raporty:
    - dodać zdjęcie posła
    - widok z raportem ile dany poseł odpuścił głosowań
    - widok z 
    - widok a ilością posłów wg wykształcenia (diagram)  w danej partii 
    - widok ze średnią wieku posłów  danej partii (diagram)
    - na widoku klubów diagram z ilością posłów w partiach
    - do widoku szczegółów posła dodać zdjęcie posła (ewentualnie link do API)
    - widok listy klubów - albo dodać szczegóły klubu albo usunąć link
    """



    
    