from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
import requests
import mysql as mysql
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import xmltodict, json
import unicodedata
import time
import datetime as dt
import redis as redis

app = Flask(__name__)
api = Api(app)

agency = 'sf-muni'

redis_host = 'redis'
redis_port = '6379'

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

def getAllRoutes(r):
    p = []
    soup = BeautifulSoup(r, 'xml')
    routes = soup.body.find_all('route')
    for route in routes:
        p.append(route['tag'])
    return p[:]

def getMinMax(p):
    return min(p), max(p)

def convertEpoch(t):
    return time.strftime('%H:%M:%S', time.localtime(t))

def getNotRunning(routes, t):
    not_running = []
    inbound = []
    outbound = []
    time = convertEpoch(t)
    for route in routes:
        schedule = requests.get(commands['schedule'] + "&a=" + agency + "&r=" + route)
        inbound, outbound = getTimes(schedule.content)
        start = max(min(inbound), min(outbound))
        end = min(max(inbound), max(outbound))
        if time > start and time < end:
            not_running.append(route)
    return not_running[:]

def getStopTimes(route, direction, p):
    if route['direction'] == direction and route['serviceClass'] == 'wkd':
        trs = route.find_all('tr')
        for tr in trs:
            stops = tr.find_all('stop')
            for stop in stops:
                if stop['epochTime'] != "-1":
                    p.append(int(stop['epochTime']))
    return p[:]

def getTimes(t):
    in_times = []
    out_times = []
    soup = BeautifulSoup(t, 'xml')
    routes = soup.body.find_all('route')
    for route in routes:
        getStopTimes(route, 'Inbound', in_times)
        getStopTimes(route, 'Outbound', out_times)
    return sorted(in_times[:]), sorted(out_times[:])


def parseString(s):
    return s.replace("(", "").replace(")", "").replace(",", "").replace("[", "").replace("]", "")

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

def convertTimestamp(x):
    return dt.datetime.fromtimestamp(x)

def secondsDiff(t1, t2):
    a = convertTimestamp(t1)
    b = convertTimestamp(t2)
    total = (b - a).total_seconds()
    app.logger.info("This request took %s seconds", total)
    return total

def getUrl(url, conn):
    r = Redis()
    if r.getKey(url) != None:
        raise ValueError("Don't stress NextBus API too much: only one request every 30 seconds allowed!")
    r.setKey(url)
    r.setExpire(url)
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

# Class for Redis Interactions
class Redis():
    def __init__(self):
        try:
            self.r = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
        except Exception as err:
            raise ValueError(err.args)
    def setKey(self, k):
        try:
            self.r.set(k, True)
        except Exception as err:
            raise ValueError(err.args)
        app.logger.info('Set Redis key: %s', k)
    def getKey(self, k):
        try:
            result = self.r.get(k)
        except Exception as err:
            raise ValueError(err.args)
        app.logger.info('Redis value of %s is %s', k, result)
        return result
    def setExpire(self, k):
        try:
            self.r.expire(k, 30)
        except Exception as err:
            raise ValueError(err.args)
        
class DbTest(Resource):
    def get(self):
        try:
            connection = mysql.DbWrapper()
            query = connection.selectAll()
        except ValueError as err:
            return err.args
        return jsonify(query)

# class Test(Resource):
#     def get(self):
#         conn = mysql.DbWrapper()
#         res = getArgs('r')
#         r = Redis()
#         response = getUrl(commands['schedule'] + "&a=" + agency, conn)
#         r.setKey('test')
#         app.logger.info(r.getKey('test') == 'True')
#         r.setExpire('test')
#         return convertToJson(response.content)

class Test(Resource):
    def get(self):
        inbound = []
        outbound = []
        conn = mysql.DbWrapper()
        response = getUrl(commands['schedule'] + "&a=" + agency + "&r=6", conn)
        r_json = convertToJson(response.content)
        inbound, outbound = getTimes(response.content)
        return inbound
        # return getTimes(response.content)

class RouteList(Resource):
    def get(self):
        conn = mysql.DbWrapper()
        response = getUrl(commands['routeList'] + "&a=" + agency, conn)
        return convertToJson(response.content)

class AgencyList(Resource):
    def get(self):
        conn = mysql.DbWrapper()
        response = getUrl(commands['agencyList'], conn)
        return convertToJson(response.content)

class GenericUrl(Resource):
    def get(self, uri):
        conn = mysql.DbWrapper()
        args = getAllArgs(dict(request.args.lists()))
        response = getUrl(commands[uri] + "&a=" + agency + "&" + str(args), conn)
        return convertToJson(response.content)

class SlowQueries(Resource):
    def get(self):
        conn = mysql.DbWrapper()
        query = conn.dbSlowQueries()
        return jsonify(query)

class NumOfQueries(Resource):
    def get(self):
        conn = mysql.DbWrapper()
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
