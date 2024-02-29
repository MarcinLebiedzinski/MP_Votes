from utils import DataBase

def load_term_list():
    db_term = DataBase('db_term')
    db_term.connection
    sql = "SELECT * FROM TestDB.dbo.term"
    terms = db_term.fetch_table(sql)
    return terms

terms = load_term_list()
print(terms)
for term in terms:
    print(term)