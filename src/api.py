from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
import requests
import MySQLdb
import xml.etree.ElementTree as ET
import xmltodict, json
import unicodedata
import time
import datetime as dt

app = Flask(__name__)
api = Api(app)

agency = 'sf-muni'

db_hostname = 'mysql'
db_username = 'thousandEyes'
db_password = 'sup3rs3cr3t'
db_name = 'thousandEyes'

queryThreshold = "5"

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

def getArgs(e):
    try:
        p = reqparse.RequestParser()
        p.add_argument(e)
        args = p.parse_args()
    except Exception as err:
        raise err.args
    return args.get(e)

def getAllArgs(args):
    string = ""
    try:
       for k, v in args.iteritems():
            string += string.join(k) + "=" + string.join(v) + "&"
    except Exception as err:
        raise ValueError(err.args)
    app.logger.info("Args are: " + string)
    return string 

def convertToJson(xml):
    try:
        o = xmltodict.parse(xml)
        return o
    except Exception as err:
        raise err.args

def secondsDiff(t1, t2):
    a = dt.datetime.fromtimestamp(t1)
    b = dt.datetime.fromtimestamp(t2)
    total = (b - a).total_seconds()
    app.logger.info("This request took %s seconds", total)
    return total

def getUrl(url, conn):
    req_time = time.time()
    try:
        response = requests.get(url)
    except Exception as error:
        raise error.args
    resp_time = time.time()
    try:
        tot_sec = secondsDiff(req_time, resp_time)
    except Exception as err:
        raise ValueError(err.args)
    conn.dbInsert(url, req_time, resp_time, tot_sec)
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

class DbTest(Resource):
    def get(self):
        try:
            connection = DbWrapper()
            query = connection.selectAll()
        except ValueError as err:
            return err.args
        return jsonify(query)

class Test(Resource):
    def get(self):
        conn = DbWrapper()
        r = getArgs('r')
        response = getUrl(commands['schedule'] + "&a=" + agency + "&r=" + r, conn)
        return convertToJson(response.content)

class RouteList(Resource):
    def get(self):
        conn = DbWrapper()
        response = getUrl(commands['routeList'] + "&a=" + agency, conn)
        return convertToJson(response.content)

class AgencyList(Resource):
    def get(self):
        conn = DbWrapper()
        response = getUrl(commands['agencyList'], conn)
        return convertToJson(response.content)

class GenericUrl(Resource):
    def get(self, uri):
        conn = DbWrapper()
        args = getAllArgs(dict(request.args.lists()))
        response = getUrl(commands[uri] + "&a=" + agency + "&" + str(args), conn)
        return convertToJson(response.content)

class SlowQueries(Resource):
    def get(self):
        conn = DbWrapper()
        query = conn.dbSlowQueries()
        return jsonify(query)

class NumOfQueries(Resource):
    def get(self):
        conn = DbWrapper()
        query = conn.dbNumQueries()
        return jsonify(query)


class DumpServices(Resource):
    def get(self):
        return commands

api.add_resource(DumpServices, '/dumpServices')
api.add_resource(DbTest, '/db')
api.add_resource(Test, '/test')
api.add_resource(AgencyList, '/agencyList')
api.add_resource(RouteList, '/routeList')
api.add_resource(GenericUrl, '/<string:uri>')
api.add_resource(SlowQueries, '/stats/slowQueries')
api.add_resource(NumOfQueries, '/stats/numOfQueries')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
