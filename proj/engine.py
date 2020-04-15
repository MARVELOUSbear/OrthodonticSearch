import json

import requests
from elasticsearch import Elasticsearch

'''
curl -XPOST 'localhost:9200/orthodontic/_close'

curl -X PUT "localhost:9200/orthodontic/_settings?pretty" -H 'Content-Type: application/json' -d'
{
    "index": {
      "similarity": {
        "default": {
          "type": "BM25",
          "k1": "1.1",
          "b": "0.7"
        }
      }
    }
}
'

curl -X PUT "localhost:9200/orthodontic/_settings" -H 'Content-Type: application/json' -d'
{
    "settings": {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "synonym" : {
                        "tokenizer" : "whitespace",
                        "filter" : ["synonym"]
                    }
                },
                "filter" : {
                    "synonym" : {
                        "type" : "synonym",
                        "lenient": true,
                        "synonyms" : [
                            "brace => fixed appliance",
                            "invisalign => clear aligner",
                            "clear aligner => invisalign",
                            "invisalign => removable orthodontic appliances",
                            "Damon => self-ligating",
                            "clear bracket => ceramic bracket",
                            "arch expansion => palatal expansion",
                            "wire => archwire",
                            "archwire => wire",
                            "Acceledent => vibration device"
                        ]
                    }
                }
            }
        }
    }
}
'

curl -XPOST 'localhost:9200/orthodontic/_open'

'''
res = requests.get('http://localhost:9200')
print(res.content)

es_client = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

drop_index = es_client.indices.create(index='orthodontic', ignore=400)
create_index = es_client.indices.delete(index='orthodontic', ignore=[400, 404])
with open("data/fulljson2.json", "rb") as f:
    data = json.loads(f.read())
print("data loading complete")
for item in data:
    res = es_client.index(index="orthodontic", doc_type="article", body=item)
    print(res['result'])
