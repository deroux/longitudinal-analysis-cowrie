#!/usr/bin/python3

import multiprocessing
import string; 
import json;

from MapReduce import MapReduce

def tuples_to_dict(tuples):
    result = {}
    result.update(tuples)
    return result

"""
MAP
{ honeypot: "honeypotA",
  date: "2021-04-25",
  passwords: [ {user: "foo", password: "bar", count: 7}, ... /* top N attempts für den Tag */ ]}
"""
def file_to_lines(filename):
    """Read a file and return a sequence of (word, occurances) values.
    """
    print(multiprocessing.current_process().name, 'reading', filename)
    output = []

    with open(filename, 'rt') as f:
        for line in f:
            js = json.loads(line)
            r = js.get('eventid')
            
            if('cowrie.login.' in r):
                userpw = js.get('username') + ':' + js.get('password')
                output.append( (userpw, 1) )

            #if('cowrie.command.input' in r):
            #    command = js.get('input')
            #    output.append((command, 1))

        #print(output)
    
    return output


def process_file(file):
    tmp = []
    tmp.append(file)

    word_counts = mapper(tmp)
    word_counts.sort(key=operator.itemgetter(1))
    word_counts.reverse()

    #print('\nTOP 20 USER:PW COMBINATIONS BY FREQUENCY\n')
    top20 = word_counts[:20]
    #longest = max(len(word) for word, count in top20)
    #print(top20)
    #for word, count in top20:
    #    print('%-*s: %5s' % (longest+1, word, count))

    data = []
    for userpw, count in top20:
        obj = {}
        obj['username'] = userpw.split(':')[0]
        obj['password'] = userpw.split(':')[1]
        obj['count'] = count
        data.append(obj)

    log_file_date = file.split('.')[-1]
    json_obj = {}
    json_obj['date'] = log_file_date
    json_obj['passwords'] = data

    return json_obj

"""
REDUCE
[ {date: "2021-04-25",
  passwords: [ {user: "foo", password: "bar", count: 15}, ... ]},
  {date: "2021-04-26",
  passwords: [ {user: "foo", password: "bar", count: 6}, ... ]}]"""
def count_items(item):
    """Convert the partitioned data for a word to a
    tuple containing the word and the number of occurances.
    """
    key, occurances = item
    return (key, sum(occurances))


if __name__ == '__main__':
    import operator
    import glob

    input_files = glob.glob('**/*.json.*', recursive=True)
    
    mapper = MapReduce(file_to_lines, count_items)

    log_data = []     

    for file in sorted(input_files):
        data = process_file(file)
        log_data.append(data)


    with open('reduced.json', 'w') as f:
        json.dump(log_data, f, indent=2)
