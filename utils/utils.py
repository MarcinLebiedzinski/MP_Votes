import pyodbc
import requests

class DataBase():
    def __init__(self, name):
        self.name = name
        self.server = 'localhost'
        self.database = 'TestDB'
        self.username = 'sa'
        self.password = 'SQLServerTest1!'
        self.connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+self.server+';DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        self.cursor = self.connection.cursor()
    
    def __del__(self):
        self.connection.close()

    def insert_into_table(self, table, columns, values):
        self.cursor.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in values)})", values)
        self.connection.commit()

    def sqlexecute(self, sql):
        self.cursor.execute(sql)
        self.connection.commit()

    def fetch_table(self, sql):
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows
    
    def fetch_photo(self, sql):
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        return row

class ApiConnector:
    def __init__(self, url):
        self.url = url

    def get(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("Something went wrong",err)

    def get_image(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("Something went wrong",err)

    def get_status_code(self):
        try:
            response = requests.get(self.url)
            return response.status_code
        except requests.exceptions.RequestException as err:
            print ("Something went wrong",err)
    def __del__(self):
        return


def get_term_list():
    term_list = []
    term_counter = 2
    while True:
        url = 'https://api.sejm.gov.pl/sejm/term' + f'{term_counter}'
        api = ApiConnector(url)
        if int(api.get_status_code()) == 200:
            term_list.append(term_counter)
            term_counter += 1
            url = 'https://api.sejm.gov.pl/sejm/term'
        else:
            break
    return term_list

def get_term_details(term):
    url = 'https://api.sejm.gov.pl/sejm/term' + f'{term}'
    api = ApiConnector(url)
    term_details = api.get()
    return term_details

def drop_table_term():
    db_term = DataBase('db_term')
    db_term.connection
    db_term.sqlexecute("DROP TABLE IF EXISTS TestDB.dbo.term;")
    db_term.connection.commit()
    return

def create_table_term():
    db_term = DataBase('db_term')
    db_term.connection
    sql = """
        CREATE TABLE TestDB.dbo.term (
        term_id SMALLINT PRIMARY KEY,
        from_date DATE,
        is_current BIT,
        );"""
    db_term.sqlexecute(sql)
    db_term.connection.commit()
    return

def save_term_details(term_details):
    db_term = DataBase('db_term')
    db_term.connection
    term_id = term_details['num']
    from_date = term_details['from']
    if term_details['current']:
        is_current = 1
    else:
        is_current = 0
    table = 'TestDB.dbo.term'
    columns = ['term_id', 'from_date', 'is_current']
    values = [term_id, from_date, is_current]
    db_term.insert_into_table(table, columns, values)
    return

def get_club_list(term):
    url = f'https://api.sejm.gov.pl/sejm/term{term}/clubs'
    print(url)
    api = ApiConnector(url)
    club_list = api.get()
    return club_list

def drop_table_club():
    db_term = DataBase('db_club')
    db_term.connection
    db_term.sqlexecute("DROP TABLE IF EXISTS TestDB.dbo.club;")
    db_term.connection.commit()
    return

def create_table_club():
    db_term = DataBase('db_club')
    db_term.connection
    sql = """
    CREATE TABLE TestDB.dbo.club (
    club_id NVARCHAR(64),
    club_name VARCHAR(255),
    members_count SMALLINT,
    term SMALLINT,
    PRIMARY KEY (club_id, term),
    FOREIGN KEY(term) REFERENCES TestDB.dbo.term(term_id),
    );"""
    db_term.sqlexecute(sql)
    db_term.connection.commit()
    return

def save_club_details(club_list, term):
    db_club = DataBase('db_club')
    db_club.connection
    for club in club_list:
        club_id = club['id']
        club_name = club['name']
        term = term
        members_count = club['membersCount']
        table = 'TestDB.dbo.club'
        columns = ['club_id', 'club_name', 'members_count', 'term']
        values = [club_id, club_name, members_count, term]

        db_club.insert_into_table(table, columns, values)

def get_member_list(term):
    url = f'https://api.sejm.gov.pl/sejm/term{term}/MP'
    api = ApiConnector(url)
    member_list = api.get()
    return member_list

def drop_table_member():
    db_term = DataBase('db_member')
    db_term.connection
    db_term.sqlexecute("DROP TABLE IF EXISTS TestDB.dbo.member;")
    db_term.connection.commit()
    return

def create_table_member():
    db_member = DataBase('db_member')
    db_member.connection
    sql = """
        CREATE TABLE TestDB.dbo.member (
        member_id SMALLINT,
        active BIT,
        birth_date DATE,
        birth_location VARCHAR(64),
        club NVARCHAR(64),
        district_name VARCHAR(64),
        district_number SMALLINT,
        education_level VARCHAR(64),
        first_name VARCHAR(64),
        second_name VARCHAR(64),
        last_name VARCHAR(64),
        number_of_votes INT,
        profession VARCHAR(128),
        voivodeship VARCHAR(128),
        term SMALLINT,
        PRIMARY KEY(member_id, term),
        FOREIGN KEY(club, term) REFERENCES TestDB.dbo.club(club_id, term),
        FOREIGN KEY(term) REFERENCES TestDB.dbo.term(term_id),
        );"""
    db_member.sqlexecute(sql)
    return

def save_member_details(member_list, term):
    db_member = DataBase('db_member')
    db_member.connection
    for member in member_list:
        term = term
        member_id = active = birth_date = birth_location = club = None
        district_name = district_number = education_level = first_name = second_name = None
        last_name = number_of_votes = profession = voivodeship = None
        columns = ['member_id', 'active', 'birth_date', 'birth_location', 'club', 'district_name', 
                    'district_number', 'education_level', 'first_name', 'second_name', 
                    'last_name', 'number_of_votes', 'profession', 'voivodeship']
        member_key_list = ['id', 'active', 'birthDate', 'birthLocation', 'club', 'districtName', 'districtNum', 
                    'educationLevel', 'firstName', 'secondName', 'lastName', 'numberOfVotes', 
                    'profession', 'voivodeship']
        values = [member_id, active, birth_date, birth_location, club, district_name, 
                    district_number, education_level, first_name, second_name, 
                    last_name, number_of_votes, profession, voivodeship]
        for i in range(0, len(columns)):
            try:
                values[i] = member[member_key_list[i]]
            except KeyError:
                print("KeyError - data not found")
        for element in values:
            if element == True:
                element = 1
            else:
                element = 0    
        columns.append('term')
        values.append(term)
        table = 'TestDB.dbo.member'
        db_member.insert_into_table(table, columns, values)
    return

def drop_table_vote():
    db_term = DataBase('db_vote')
    db_term.connection
    db_term.sqlexecute("DROP TABLE IF EXISTS TestDB.dbo.vote;")
    db_term.connection.commit()
    return

def create_table_vote():
    db_member = DataBase('db_vote')
    db_member.connection
    sql = """
        CREATE TABLE TestDB.dbo.vote (
        voting_number SMALLINT,
        sitting SMALLINT,
        sitting_day SMALLINT,
        term SMALLINT,
        date DATE,
        kind VARCHAR(64),
        description VARCHAR(512),
        title TEXT,
        topic TEXT,
        total_voted SMALLINT,
        abstain SMALLINT,
        yes SMALLINT,
        no SMALLINT,
        PRIMARY KEY(voting_number, sitting, term),
        FOREIGN KEY(term) REFERENCES TestDB.dbo.term(term_id),
        );"""
    db_member.sqlexecute(sql)
    return


def get_vote_list(term):
    vote_list = []
    sitting = 1
    while True:
        url = f'https://api.sejm.gov.pl/sejm/term{term}/votings/{sitting}' 
        api = ApiConnector(url)
        if int(api.get_status_code()) == 200 and api.get():
            votes = api.get()
            amount_of_votes_in_sitting = len(votes)
            vote_list.append((sitting, amount_of_votes_in_sitting))
            sitting += 1
        else:
            break
    return vote_list

# W funkcji poniżej rozważyć aby usunąć warunek statusu HTTP i pustej listy
def get_vote_details(vote_list, term):
    vote_details = []
    for sitting in vote_list:
        votes = sitting[1]
        for voting in range(1, votes+1):
            url = f'https://api.sejm.gov.pl/sejm/term{term}/votings/{sitting[0]}/{voting}'
            print(url)
            api = ApiConnector(url)
            if int(api.get_status_code()) == 200 and api.get():
                api_vote_dict = api.get()

                voting_number = sitting_day = date = kind = description = None
                title = topic = total_voted = abstain = yes = no = None
                sitting_number = term_number = None

                columns = ['voting_number', 'sitting', 'term', 'sitting_day' ,'date', 'kind','description', 
                            'title', 'topic', 'total_voted', 'abstain', 'yes', 'no']
                api_vote_key_list = ['votingNumber', 'sitting', 'term', 'sittingDay', 'date', 'kind','description', 
                                        'title', 'topic', 'totalVoted', 'abstain', 'yes', 'no']

                values = [voting_number, sitting_number, term_number, sitting_day, date, kind, description, 
                            title, topic, total_voted, abstain, yes, no]


                for i in range(0 ,len(columns)):
                    try:
                        values[i] = api_vote_dict[api_vote_key_list[i]]
                    except KeyError:
                        print("Exception occured - blank field in api json")
                
                vote_details.append([columns, values])
            else:
                break
    return vote_details

def save_vote_details(vote_details):
    db_vote = DataBase('db_vote')
    db_vote.connection
    for vote in vote_details:
        table = 'TestDB.dbo.vote'
        columns = vote[0]
        values = vote[1]
        db_vote.insert_into_table(table, columns, values)
    return


def drop_table_membervote():
    db_membervote = DataBase('db_membervote')
    db_membervote.connection
    db_membervote.sqlexecute("DROP TABLE IF EXISTS TestDB.dbo.membervote;")
    db_membervote.connection.commit()
    return

def create_table_membervote():
    db_membervote = DataBase('db_vote')
    db_membervote.connection
    sql = """
        CREATE TABLE TestDB.dbo.membervote (
        id INT IDENTITY(1,1),
        member SMALLINT,
        voting_number SMALLINT,
        sitting SMALLINT,
        term SMALLINT,
        vote VARCHAR(16),
        PRIMARY KEY(id),
        FOREIGN KEY(member, term) REFERENCES TestDB.dbo.member(member_id, term),
        FOREIGN KEY(term) REFERENCES TestDB.dbo.term(term_id),
        FOREIGN KEY(voting_number, sitting, term) REFERENCES TestDB.dbo.vote(voting_number, sitting, term)
        );"""
    db_membervote.sqlexecute(sql)


def get_membervote_details(vote_list, term):
    membervote_details = []
    for sitting in vote_list:
        votes = sitting[1]
        for voting in range(1, votes+1):
            url = f'https://api.sejm.gov.pl/sejm/term{term}/votings/{sitting[0]}/{voting}'
            print(url)
            api = ApiConnector(url)
            if int(api.get_status_code()) == 200 and api.get():
                api_membervote_dict = api.get()

                for element in api_membervote_dict['votes']:
                    member = element['MP']
                    voting_number = api_membervote_dict['votingNumber']
                    sitting_number = api_membervote_dict['sitting']
                    term_number = api_membervote_dict['term']
                    vote = element['vote']

                    columns = ['member', 'voting_number', 'sitting', 'term', 'vote']
                    values = [member, voting_number, sitting_number, term_number, vote]
                    print(values)
                    membervote_details.append([columns, values])
            else:
                break
    return membervote_details


def save_membervote_details(membervote_details):
    db_membervote = DataBase('db_membervote')
    db_membervote.connection
    for membervote in membervote_details:
        table = 'TestDB.dbo.membervote'
        columns = membervote[0]
        values = membervote[1]
        try:
            db_membervote.insert_into_table(table, columns, values)
        except:
            print(f"Sth went wrong with {columns} - {values}")
    return

def load_term_list():
    db_term = DataBase('db_term')
    db_term.connection
    sql = "SELECT * FROM TestDB.dbo.term"
    terms = db_term.fetch_table(sql)
    return terms

def load_club_list(term):
    db_club = DataBase('db_club')
    db_club.connection
    sql = f"SELECT * FROM TestDB.dbo.club WHERE term={term};"
    clubs = db_club.fetch_table(sql)
    return clubs

def load_member_list(term):
    db_term = DataBase('db_term')
    db_term.connection
    sql = f"SELECT * FROM TestDB.dbo.member WHERE term={term};"
    terms = db_term.fetch_table(sql)
    return terms

def load_vote_list(term):
    db_vote = DataBase('db_vote')
    db_vote.connection
    sql = f"SELECT * FROM TestDB.dbo.vote WHERE term={term} AND kind = 'electronic';"
    votes = db_vote.fetch_table(sql)
    return votes

def load_membervote_list(term, member):
    db_membervote = DataBase('db_membervote')
    db_membervote.connection
    sql=f"""
    SELECT TestDB.dbo.membervote.voting_number, 
    TestDB.dbo.membervote.sitting, 
    TestDB.dbo.vote.date, 
    TestDB.dbo.vote.title,
    TestDB.dbo.vote.topic,
    TestDB.dbo.membervote.vote
    FROM TestDB.dbo.membervote
    JOIN TestDB.dbo.vote
    ON TestDB.dbo.membervote.voting_number=TestDB.dbo.vote.voting_number 
    AND TestDB.dbo.membervote.sitting=TestDB.dbo.vote.sitting 
    AND TestDB.dbo.membervote.term =TestDB.dbo.vote.term
    WHERE TestDB.dbo.membervote.member={member}
    AND TestDB.dbo.membervote.term={term}
    ORDER BY TestDB.dbo.membervote.sitting
    ;"""
  
    votes = db_membervote.fetch_table(sql)
    return votes

def load_member_name(term, member_id):
    db_member = DataBase('db_member')
    db_member.connection
    sql = f"""
    SELECT * FROM TestDB.dbo.member 
    WHERE TestDB.dbo.member.member_id={member_id} 
    AND TestDB.dbo.member.term={term};"""
    member = db_member.fetch_table(sql)
    return member

def drop_table_photo():
    db_photo = DataBase('db_photo')
    db_photo.connection
    db_photo.sqlexecute("DROP TABLE IF EXISTS TestDB.dbo.photo;")
    db_photo.connection.commit()
    return

def create_table_photo():
    db_photo = DataBase('db_photo')
    db_photo.connection
    sql = """
        CREATE TABLE TestDB.dbo.photo (
        member_id SMALLINT,
        term SMALLINT,
        photo VARBINARY(MAX),
        PRIMARY KEY (member_id, term),
        FOREIGN KEY (member_id, term) REFERENCES TestDB.dbo.member(member_id, term),
        FOREIGN KEY (term) REFERENCES TestDB.dbo.term(term_id)
        );"""
    db_photo.sqlexecute(sql)
    return

def get_photo(term, member_id):
    url = f'https://api.sejm.gov.pl/sejm/term{term}/MP/{member_id}/photo'
    api = ApiConnector(url)
    photo = api.get_image()
    return photo

def save_photo(term, member_id, photo):
    db_photo = DataBase('db_photo')
    table = 'TestDB.dbo.photo'
    columns = ['member_id', 'term', 'photo']
    values = [member_id, term, photo]
    db_photo.insert_into_table(table, columns, values)
    return

def get_photo(term, member_id):
    db_photo = DataBase('db_photo')
    sql = f"SELECT photo FROM TestDB.dbo.photo WHERE member_id = {member_id} AND term = {term};"
    photo = db_photo.fetch_photo(sql)
    return photo

# drop_table_photo()
# create_table_photo()
# for term in range(9,11):
#     members = get_member_list(term)
#     for member in members:
#         member_id = member['id']
#         photo = get_photo(term, member_id)
#         save_photo(term, member_id, photo)

# drop_table_term()
# drop_table_club()
# drop_table_member()
# drop_table_vote()
# drop_table_membervote()
    
# create_table_term()
# create_table_club()
# create_table_member()
# create_table_vote()
# create_table_membervote()

# term_list = get_term_list()

# for term in range(9, 11):
#     term_details = get_term_details(term)
#     save_term_details(term_details)
    
#     club_list = get_club_list(term)
#     save_club_details(club_list, term)

#     member_list = get_member_list(term)
#     save_member_details(member_list, term)

#     vote_list = get_vote_list(term)
#     vote_details = get_vote_details(vote_list, term)
#     save_vote_details(vote_details)
#     vote_list = get_vote_list(term)
#     print(vote_list)
#     membervote_details = get_membervote_details(vote_list, term)
#     save_membervote_details(membervote_details)

# for term in range (2, 9):
#     term_details = get_term_details(term)
#     save_term_details(term_details)
