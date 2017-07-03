#!/usr/bin/env python

#
# Feed stdin into elasticsearch line-by-line
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#

import sys
import elasticsearch, elasticsearch.helpers

def _index_stdin_lines(index):
    line = sys.stdin.readline()
    while line:
        yield {
                "_index": index,
                "_type": "accesslog",
                "_source": {
                    "message": line.strip(),
                }
              }
        line = sys.stdin.readline()

if __name__ == '__main__':
    
    if len(sys.argv) != 3:
        print "USAGE: %s <pipeline> <target_index>"
        sys.exit(1)
    pipeline, index = sys.argv[1:]

    es = elasticsearch.Elasticsearch('localhost')
    docs = 0
    errors = 0
    errlog = []

    for (success, res) in elasticsearch.helpers.parallel_bulk(es,
            _index_stdin_lines(index),
            pipeline=pipeline, raise_on_error=False):
        if not success:
            errors += 1
            err = res['index']['error']
            while 'caused_by' in err:
                err = err['caused_by']
            errlog.append(err['reason'])
        docs += 1
        if (docs % 10000) == 0:
            print "%7d documents processed, %5d errors" % (docs, errors)

    print "========================================="
    print "All done."
    print "Total # documents: %d, total # errors: %d" % (docs,errors)
    print
    print "ERRORS:"
    print "======="
    for err in errlog:
        print err
