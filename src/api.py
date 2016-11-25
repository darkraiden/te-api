from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from StringIO import StringIO
import MySQLdb
import xml.etree.ElementTree as ET
import xmltodict, json

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

def convertToJson(xml):
    o = xmltodict.parse(xml)
    return o

# Class for DB interactions
class Connection():
    def __init__(self):
        try:
            self.connection = MySQLdb.connect(host=db_hostname, user=db_username, passwd=db_password, db=db_name)
        except Exception as error:
            raise ValueError("Error! Unable to connect to the Database!")
    def selectQuery(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM statistics")
            result = cursor.fetchall()
            return result
        except:
            raise ValueError("Error! Unable to fetch data!")
    def dbDisconnect(self):
        try:
            self.connection.close()
        except:
            raise ValueError("Error! Unable to close the DB connection")

class DbTest(Resource):
    def get(self):
        try:
            connection = Connection()
            query = connection.doQuery()
            connection.dbDisconnect()
        except ValueError as err:
            return err.args

        return query

class Test(Resource):
    def get(self):
        import requests
        response = requests.get(commands['agencyList'])

        # tree = ET.fromstring(response.content)
        return convertToJson(response.content)


class DumpServices(Resource):
    def get(self):
        return commands

api.add_resource(DumpServices, '/dumpServices')
api.add_resource(DbTest, '/db')
api.add_resource(Test, '/test')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
