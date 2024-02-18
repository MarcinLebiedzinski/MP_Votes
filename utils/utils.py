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
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in values)})"
        self.cursor.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in values)})", values)
        self.connection.commit()

    def sqlexecute(self, sql):
        self.cursor.execute(sql)
        self.connection.commit()

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
    FOREIGN KEY(term) REFERENCES term(term_id),
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
        FOREIGN KEY(club, term) REFERENCES club(club_id, term),
        FOREIGN KEY(term) REFERENCES term(term_id),
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

def votes():
    pass


def drop_table_vote():
    db_term = DataBase('db_member')
    db_term.connection
    db_term.sqlexecute("DROP TABLE IF EXISTS TestDB.dbo.member;")
    db_term.connection.commit()
    return



# drop_table_member()
# drop_table_club()
# drop_table_term()
# create_table_term()
# create_table_club()
# create_table_member()

# term_list = get_term_list()
# for term in range(9, 11):
#     term_details = get_term_details(term)
#     save_term_details(term_details)
    
#     club_list = get_club_list(term)
#     save_club_details(club_list, term)

#     member_list = get_member_list(term)
#     save_member_details(member_list, term)





