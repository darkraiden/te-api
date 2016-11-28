import MySQLdb

db_hostname = 'mysql'
db_username = 'thousandEyes'
db_password = 'sup3rs3cr3t'
db_name = 'thousandEyes'

queryThreshold = "5"

# Class for DB interactions
class Connection():
    def __init__(self):
        try:
            self.connection = MySQLdb.connect(host=db_hostname, user=db_username, passwd=db_password, db=db_name)
            self.cursor = self.connection.cursor()
        except Exception as error:
            raise ValueError("Error! Unable to connect to the Database!")
    def dbDisconnect(self):
        try:
            self.connection.close()
        except:
            raise ValueError("Error! Unable to close the DB connection")

    def dbCommit(self):
        try:
            self.connection.commit()
        except:
            raise ValueError("Error! Unable to commit your query!")

class DbWrapper():
    def __init__(self):
        self.conn = Connection()
    def selectAll(self):
        try:
            self.conn.cursor.execute('SELECT * FROM statistics')
            result = self.conn.cursor.fetchall()
            self.conn.dbDisconnect()
            return result
        except:
            raise ValueError("Error! Unable to fetch data!")
    def dbInsert(self, e, trq, trs, tsc):
        try:
            self.conn.cursor.execute("INSERT INTO statistics (endpoint, timerequest, timeresponse, totaltime) VALUES (%s, %s, %s, %s)", (e, trq, trs, tsc))
            self.conn.dbCommit()
            self.conn.dbDisconnect()
        except Exception as err:
            self.conn.dbDisconnect()
            raise ValueError(err.args)
    def dbSlowQueries(self):
        try:
            self.conn.cursor.execute("SELECT endpoint, totaltime FROM statistics WHERE statistics.totaltime > %s", queryThreshold)
            result = self.conn.cursor.fetchall()
            self.conn.dbDisconnect()
        except Exception as err:
            self.conn.dbDisconnect()
            raise ValueError(err.args)
        return result

    def dbNumQueries(self):
        try:
            self.conn.cursor.execute("SELECT endpoint, count(*) AS tot FROM statistics GROUP BY endpoint")
            result = self.conn.cursor.fetchall()
            self.conn.dbDisconnect()
        except Exception as err:
            self.conn.dbDisconnect()
            raise ValueError(err.args)
        return result

    def dbGetLastEndpoint(self, e):
        try:
            self.conn.cursor.execute("SELECT timerequest FROM statistics WHERE endpoint = '" + e + "' ORDER BY ID DESC LIMIT 1")
            result = list(self.conn.cursor.fetchall())
        except Exception as err:
            self.conn.dbDisconnect()
            raise ValueError(err.args)
        self.conn.dbDisconnect()
        return str(result)
