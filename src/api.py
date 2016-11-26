from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import requests
import MySQLdb
import xml.etree.ElementTree as ET
import xmltodict, json
import time

app = Flask(__name__)
api = Api(app)

agency = 'sf-muni'

db_hostname = 'mysql'
db_username = 'thousandEyes'
db_password = 'sup3rs3cr3t'
db_name = 'thousandEyes'

commands = {
    "agencyList": "http://webservices.nextbus.com/service/publicXMLFeed?command=agencyList",
    "routeList": "http://webservices.nextbus.com/service/publicXMLFeed?command=routeList",
    "routeConfig": "http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig",
    "predictions": "http://webservices.nextbus.com/service/publicXMLFeed?command=predictions",
    "predictionsForMultiStops": "http://webservices.nextbus.com/service/publicXMLFeed?command=predictionsForMultiStops",
    "schedule": "http://webservices.nextbus.com/service/publicXMLFeed?command=schedule",
    "messages": "http://webservices.nextbus.com/service/publicXMLFeed?command=messages",
    "vehicleLocations": "http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations"
}

def getArgs(r, e):
    try:
        p = reqparse.RequestParser()
        p.add_argument(e)
        args = p.parse_args()
    except Exception as err:
        raise err.args
    return args.get(e)

def convertToJson(xml):
    o = xmltodict.parse(xml)
    return o

def getUrl(url):
    req_time = time.time()
    try:
        response = requests.get(url)
    except Exception as error:
        raise error.args
    resp_time = time.time()
    return response

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
    def dbInsert(self, e, trq, trs):
        try:
            self.conn.cursor.execute('INSERT INTO statistics (endpoint, timerequest, timeresponse) VALUES (e, trq, trs)')
            self.conn.dbDisconnect()
            return True
        except Exception as err:
            raise err.args

class DbTest(Resource):
    def get(self):
        try:
            connection = DbWrapper()
            query = connection.selectAll()
        except ValueError as err:
            return err.args
        return query

class Test(Resource):
    def get(self):
        r = getArgs(self, 'r')
        response = getUrl(commands['schedule'] + "&a=" + agency + "&r=" + r)
        return convertToJson(response.content)

class RouteList(Resource):
    def get(self):
        response = getUrl(commands['routeList'] + "&a=" + agency)
        return convertToJson(response.content)


class DumpServices(Resource):
    def get(self):
        return commands

api.add_resource(DumpServices, '/dumpServices')
api.add_resource(DbTest, '/db')
api.add_resource(Test, '/test')
api.add_resource(RouteList, '/routes')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
