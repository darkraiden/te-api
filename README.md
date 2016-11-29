# Thousand Eyes API

An API developed in Python that retrieves data from NextBus API.

## Requirements

* Docker
* Docker Compose

## Docker Stack

### Up and running

To start the entire stack, just type in your terminal:

```
$ docker-compose up -d
```

The above will spin up 3 different docker containers in a daemonised mode:

* api - built on a python image;
* mysql; and 
* redis.

All the containers share their ports with the host:

* api - 5000:5000;
* mysql - 3306:3306; and
* redis - 6379:6379.

#### API Address

To connect to the endpoint, use this IP: `127.0.0.1:5000`

### Stop the stack

To stop the docker stack, just type in your terminal:

```
$ docker-compose down
```

## Endpoints

All the endpoints below will work with `sf-muni` agency only, which will be added automatically to the url.

### Expose NextBus Endpoints

The ThousandEyes API allows you to get the result of any get request to NextBus API. To see which endpoints are available, you can interrogate `127.0.0.1:5000/dumpServices` which will return a Json with all the endpoint available to add as URI.
eg

```
127.0.0.1:5000/schedule?r=6
```

The above will return all the schedules for the Route 6.

If want to show all the available commands, try to interrogate `127.0.0.1:5000/dumpServices` - it'll return a list of NextBus endpoints.

### Statistics

#### Slow queries

`/stats/slowQueries` will return back a list of all the queries that took longer than 5 seconds. The threshold can be changed - a `queryThreshold` variable is provided within [mysql](./src/mysql.py) module.

#### Number Of queries

`/stats/numOfQueries` will return back a list of all the HTTP requests made to NextBus API with their recurrences.

### Not Running

`/notRunning?t=<time in epoch>` - This endpoint will return a list of all the service which are not running at a given time. It accepts one parameter, `t`, that must be in `epoch time` format! 
