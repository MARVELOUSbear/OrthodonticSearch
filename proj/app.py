import re
import timeit

from elasticsearch import Elasticsearch
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    start = timeit.default_timer()
    s = ""
    tokenize_pattern = "[\w'-]+"
    not_pattern = "[Nn]{1}[Oo]{1}[Tt]{1}\[.*?\]"
    must_pattern = "\".*?\""
    if request.method == 'POST':
        query = request.form['searchText']
        if "choose" in request.form.keys() and request.form["choose"] != "Category" and request.form["choose"] != "All":
            categories = {"wire", "bracket", "clear aligner", "implant", "gear", "surgery"}
            query += ' "' + request.form["choose"].lower() + '"'
            categories.remove(request.form["choose"].lower())
            for c in categories:
                query += " NOT[" + c + "]"
        if "original_search" in request.form.keys():
            original = request.form["original_search"]
            original = original.replace('*', '"')
            original = original.replace("+", " ")
            query += " " + original
        else:
            original = query
        print(query)
        not_part = [w[4:-1] for w in re.findall(not_pattern, query)]
        must_part = [w.strip("\"") for w in re.findall(must_pattern, query)]
        common_part = re.findall(tokenize_pattern, query)
        common_q = " ".join(common_part).replace("NOT", "").replace("not", "")
        query_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": common_q,
                                "type": "cross_fields",
                                "fields": ["title^2.0", "abstract", "authors"]
                            }
                        },
                        {
                            "multi_match": {
                                "query": common_q,
                                "type": "best_fields",
                                "fields": ["pmid", "doi"]
                            }
                        }
                    ],
                    "minimum_should_match": 1,
                }
            }
        }
        if len(not_part) > 0:
            query_body["query"]["bool"]["must_not"] = []
            for not_p in not_part:
                query_body["query"]["bool"]["must_not"].append(
                    {
                        "multi_match": {
                            "query": not_p,
                            "type": "phrase",
                            "fields": ["title", "abstract", "authors", "pmid", "doi"]
                        }
                    }
                )
        if len(must_part) > 0:
            query_body["query"]["bool"]["filter"] = []
            for must_p in must_part:
                query_body["query"]["bool"]["filter"].append(
                    {
                        "multi_match": {
                            "query": must_p,
                            "type": "phrase",
                            "fields": ["title", "abstract", "authors", "pmid", "doi"]
                        }
                    }
                )
        if ('start-year' in request.form.keys() and request.form["start-year"]) or ('end-year' in request.form.keys()
                                                                                    and request.form["end-year"]):
            date_q = {"range": {"date": {"format": "yyyy-MM-dd"}}}
            if 'start-year' in request.form.keys() and request.form["start-year"]:
                date_q["range"]["date"]["gte"] = request.form["start-year"] + "-01-01"
            if 'end-year' in request.form.keys() and request.form["end-year"]:
                date_q["range"]["date"]["lte"] = request.form["end-year"] + "-12-31"
            if "filter" not in query_body["query"]["bool"].keys():
                query_body["query"]["bool"]["filter"] = []
            query_body["query"]["bool"]["filter"].append(date_q)
        res = es.search(index="orthodontic", body=query_body, explain=True, size=10000)
        stop = timeit.default_timer()
        filtered_res = filter(res)
    return render_template("list.html", number=len(filtered_res), time="{:.2f}".format(stop - start),
                           original_q=original.replace('"', '*').replace(" ", "+"), res=filtered_res)


def filter(res):
    filtered = []
    for record in res['hits']['hits']:
        if record['_source']["title"] and record['_source']["abstract"] and len(record['_source']["abstract"]) > 0:
            record['_source']["title"] = record['_source']["title"].strip(".")
            record['_source']["title"] = record['_source']["title"].strip("[")
            record['_source']["title"] = record['_source']["title"].strip("]")
            if len(record['_source']["abstract"].split(" ")) > 100:
                record['_source']["abstract"] = " ".join(record['_source']["abstract"].split()[:100]) + "..."
            filtered.append(record)
    return filtered


@app.route('/detail', methods=['GET'])
def detail():
    res = es.search(index="orthodontic", body={"query": {"terms": {"_id": [request.args["id"]]}}}, explain=True,
                    size=10000)
    record = res['hits']['hits'][0]
    record['_source']["title"] = record['_source']["title"].strip(".")
    record['_source']["title"] = record['_source']["title"].strip("[")
    record['_source']["title"] = record['_source']["title"].strip("]")
    return render_template("detail.html", r=record)


if __name__ == '__main__':
    es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
    es.indices.refresh(index="orthodontic")
    app.run()
