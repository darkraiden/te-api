from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import pycurl
from StringIO import StringIO
import MySQLdb

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

def doQuery(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM statistics")
        result = cursor.fetchall()
        return result
    except:
        return "Error! Unable to fetch data!"

class DbTest(Resource):
    def get(self):
        try:
            connection = MySQLdb.connect(host=db_hostname,
                                         user=db_username,
                                         passwd=db_password,
                                         db=db_name)
        except:
            return "Error! Unable to connect to the Database!"
        query = doQuery(connection)
        connection.close()
        return query


class DumpServices(Resource):
    def get(self):
        return commands

api.add_resource(DumpServices, '/dumpServices')
api.add_resource(DbTest, '/db')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
