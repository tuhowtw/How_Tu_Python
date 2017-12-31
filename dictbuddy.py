from bs4 import BeautifulSoup as bs
import re
import requests
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



source_path = os.getcwd()
os.chdir(os.pardir)
if not os.path.isdir('output'):
    os.mkdir('output')
path_out = os.path.join(os.getcwd(),'output')
os.chdir(source_path)

serviceurl = 'http://dictionary.cambridge.org/dictionary/english/'
header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

pos_short = {'noun':'n.',
"verb":'v.',
"adjective":'adj.',
"adverb":'adv.',
"pronoun":"pron.",
"preposition":"prep.",
"conjunction":'conj.',
"interjection":'inter.'}

running = False


def getVocabs():
    os.chdir(source_path)
    with open('Vocab.txt','r') as vocabs:
        os.chdir(path_out)
        if os.path.isfile('output.txt'): os.remove('output.txt')
        with open('output.txt','w',encoding="utf-8") as output:
            request_count = 0
            for vocab in vocabs:
                vocab = vocab.strip().lower()
                print('===Getting {}==='.format(vocab))

                request_count += 1
                page = requests.get(serviceurl+vocab,headers=header)
                if not page.status_code is requests.codes.ok:
                    print('===Not in Dict===')
                    continue
                soup = bs(page.content,'html.parser')

                poses = [tag for tag in soup.find_all(class_='pos-header') if "runon-head" not in tag.parent['class']]
                for pos in poses:
                    try:
                        part_of_speech = '('+pos_short[pos.find(class_="pos").text]+' )'
                    except:
                        print("Something Weird Happened")
                        continue
                    pos_bodys = pos.find_next_siblings()[0]
                    senses = [tag for tag in pos_bodys.find_all(class_='sense-block') if 'british' in tag['id']]    #sense means a definition, and I only apply for english def
                    for sense in senses:
                        defin = sense.find(class_="def").text #get definition
                        defin = defin.replace(':','')
                        try:
                            examp = sense.find_all(class_="examp emphasized")[0].text
                        except:
                            print("===No Example===")
                            output.write(vocab+part_of_speech+'\t'+part_of_speech+defin+';')
                            continue

                        output.write(vocab+part_of_speech+'\t'+part_of_speech+defin+'\n\ne.g. '+examp+';')
                time.sleep(0.05)
                if request_count >= 100:
                    print("Take a break")
                    time.sleep(5)
                    request_count = 0
                print('--------------')
    running = False
    print("End\n\n")

class MyHandler(FileSystemEventHandler):
        def on_modified(self, event):
            print("\n\nStart Fetching:")
            getVocabs()

import time,sys
hand = MyHandler()
observer = Observer()
observer.schedule(hand,path=source_path,recursive=False)
observer.start()

while True:
    blah="\|/-\|/-"

    try:
        for l in blah:
            if not running:
                sys.stdout.write(l)
                sys.stdout.flush()
                sys.stdout.write('\b')
                time.sleep(0.2)
            else:
                sys.stdout.flush()
                sys.stdout.write('\b')
    except KeyboardInterrupt:
        observer.stop()
        quit()
