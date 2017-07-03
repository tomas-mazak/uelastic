µElastic - Elastic Stack Home Edition
=====================================

**!! WORK IN PROGRESS REPO !!**

If you've ever tried to extract some statistics from http access logs and used commands like:
```
grep -F '.php HTT' access.log | grep POST | cut -d '"' -f 2 | cut -d " " -f 2 | sort | uniq -c | sort -n
```
... and felt there must be a better way, you might be interested in this :)


Elastic Stack, formerly known as ELK (Elastic-Logstash-Kibana) is an awsome toolchain which usually (in real-time):

1. collects the logs from webservers,
2. parses and enriches them (e.g. adding GeoIP data),
2. stores them in Elasticsearch document database and
3. presents them via awsome search API and Kibana web UI.

Using Elastic Stack, answers to following questions, and many more, are just a few clicks away:

- How does the request rate change in time?
- What is the source country distribution for all POST request?
- What are top 10 visited URIs between 13:37:37 and 16:06:06?
- What average, mean, or 98 percentile request time and how does it change in time?
- ... and many more


Sadly, not every webite yom might need to deal with uses these awsome realtime tools, but that can't stop you from 
building a small local Elastic Stack and feeding the text access logs in it ad-hoc, whenever you need to get some insight.


How to get there:
-----------------
- Install docker and docker-compose (Ubuntu):
```
apt-get update
apt-get install docker.io docker-compose
```
- Clone this repo:
```
git clone git@github.rackspace.com:toma0716/elasticlogs.git
cd elasticlogs
git submodule init
git submodule update
```
- Spawn the environment using docker-compose:
```
docker-compose up -d
```
- Create ingest pipeline (for parsing the logs):
```
curl -XPUT localhost:9200/_ingest/pipeline/apache2combined?pretty -d '
{
  "description" : "Parse Apache2 Combined log format",
  "processors": [
    {
      "grok": {
        "field": "message",
        "patterns": ["%{COMBINEDAPACHELOG}"]
      }
    },
    {
      "remove": {
        "field": "message"
      }
    }
  ]
}'
```
- Create the index (Elasticsearch indices is what we would call databases):
```
curl -XPUT localhost:9200/myindex?pretty -d '
{
    "mappings": {
        "accesslog": {
            "dynamic_templates": [
                {
                    "ignoreunknown": {
                        "match": "*",
                        "mapping": {
                            "enabled": false
                        }
                    }
                }
            ],
            "properties": {
                "clientip": { "type": "ip" },
                "auth": { "type": "keyword" },
                "timestamp": { "type": "date", "format": "dd/MMM/YYY:HH:mm:ss Z" },
                "verb": { "type": "keyword" },
                "request": { "type": "keyword" },
                "httpversion": { "type": "keyword" },
                "response": { "type": "keyword" },
                "bytes": { "type": "integer" },
                "referrer": { "type": "keyword" },
                "agent": { "type": "keyword" }
            }
        }
    }
}'
```
- Feed the log files in:
```
./feed.py apache2combined myindex < access.log
```
- Log into Kibana: http://localhost:5601 and have a look around
