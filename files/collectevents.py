import elasticsearch
import argparse
import datetime
from time import mktime


def ts(d):
    return int(mktime((d).timetuple())) * 1000


parser = argparse.ArgumentParser()
parser.add_argument('hosts', nargs='*', default=[])
args = parser.parse_args()

e = elasticsearch.Elasticsearch(args.hosts)


def installIdPerVersion(range1, range2, version):
    body = {
        "query": {
            "range": {
                "@timestamp": {
                    "format": "epoch_millis",
                    "gte": range1,
                    "lte": range2
                }
            }
        },
        "aggs": {
            "2": {
                "aggs": {
                    "1": {
                        "cardinality": {
                            "field": "installid.raw"
                        }
                    }
                },
                "terms": {
                    "order": {
                        "1": "desc"
                    },
                    "field": "versions." + version + ".raw",
                    "size": 20
                }
            }
        },
        "size": 0
    }
    result = e.search(index='logstash-*', body=body)
    ret = {}
    for r in result['aggregations']['2']['buckets']:
        ret[r['key'].replace(".", "_")] = r['1']['value']
    return ret


def installId(range1, range2):
    body = {
        "query": {
            "range": {
                "@timestamp": {
                    "format": "epoch_millis",
                    "gte": range1,
                    "lte": range2
                }
            }
        },
        "aggs": {
            "1": {
                "cardinality": {
                    "field": "installid.raw"
                }
            }
        },
        "size": 0
    }
    result = e.search(index='logstash-*', body=body)
    return result['aggregations']['1']['value']


now = datetime.date.today()
for i in xrange(10):
    then = now - datetime.timedelta(days=i)
    data = dict(
        timestamp=then,
        total=installId(
            ts(then - datetime.timedelta(days=1)), ts(then)),
        total_cumul=installId(0, ts(then)))
    for version in ['Buildbot', 'Python']:
        data['per' + version] = installIdPerVersion(
            ts(then - datetime.timedelta(days=1)), ts(then), version)
        data['per' + version + '_cumul'] = installIdPerVersion(0, ts(then),
                                                               version)
    e.index(
        index="postprocess-index",
        doc_type='aggregations',
        id=ts(then),
        body=data)
