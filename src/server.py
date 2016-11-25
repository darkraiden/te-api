from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import pycurl
from StringIO import StringIO

app = Flask(__name__)
api = Api(app)

agency = 'sf-muni'

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



def getUrl(url):
    buffer = StringIO()
    c = pycurl.Curl()
    c.stopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.perform
    c.close
    return buffer.getvalue()


parser = reqparse.RequestParser()


class AgencyList(Resource):
    def get(self):
        # return getUrl(commands['agencyList'])
        buffer = StringIO()
        c = pycurl.Curl()
        c.stopt(c.URL, commands['agencyList'])
        c.setopt(c.WRITEDATA, buffer)
        c.perform
        c.close
        body = buffer.getvalue()
        return body
		

class Services(Resource):
    def get(self):
#         body = buffer.getvalue()
        return commands

api.add_resource(Services, '/services')
api.add_resource(AgencyList, '/agency-list')

if __name__ == '__main__':
    app.run(debug=True)
