import os
import compress_pickle
import sys
import pickle
import indexed_bzip2
import hashlib
from os import listdir
from os.path import isfile, join
import json
import tqdm
import psutil
import bz2

def find_nth(s, x, n=0, overlap=False):
    l = 1 if overlap else len(x)
    i = -l
    for c in range(n + 1):
        i = s.find(x, i + l)
        if i < 0:
            break
    return i

nproc=psutil.cpu_count(logical=False)

file = indexed_bzip2.open( sys.argv[1], parallelization = nproc )
if os.path.isfile(sys.argv[1]+".offsets"):
    with open( "offsets.dat", 'rb' ) as offsets_file:
        block_offsets = pickle.load( offsets_file )
        file.set_block_offsets( block_offsets )
else:
    block_offsets = file.block_offsets()
    with open( sys.argv[1]+".offsets", 'wb' ) as offsets_file:
        pickle.dump( block_offsets, offsets_file )

#file=bz2.open(sys.argv[1], "rt")
    
count=0
f2=open("P.xml","w")
f2.write('<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.11/ http://www.mediawiki.org/xml/export-0.11.xsd" version="0.11" xml:lang="en">\n')

file.seek(0)
line=file.readline().decode("utf-8")

#file.seek(1712165880080)

plast=-1
while True:
    p=file.tell()
    line=file.readline().decode("utf-8").strip()[0:-1]
    if p==plast:
        break
    i0=find_nth(line,"\"",6)+1
    i1=find_nth(line,"\"",7)
    item=line[i0:i1]
    if not item.startswith("Q"):
        i0=find_nth(line,"\"",10)+1
        i1=find_nth(line,"\"",11)
        item=line[i0:i1]
#        if not item.startswith("P"):
#            try:
#                item=json.loads(line.strip()[:-1])["id"]
#            except:
#                print("not using pos",p)
#                pass
    plast=p
    if item.startswith("P"):
        print(item,p,count)
        count=count+1
        data=json.loads(line)
        f2.write('<page>\n')
        f2.write('<title>Property:'+item+'</title>\n')
        f2.write('<ns>122</ns>\n')
        f2.write('<id>'+str(data["pageid"])+'</id>\n')
        f2.write('<revision>')
        f2.write('<id>'+str(data["lastrevid"])+"</id>\n")
#                f2.write('<parentid>'+parentid+"</parentid>\n")
        f2.write('<timestamp>'+data["modified"]+"</timestamp>\n")
        f2.write('<origin>'+str(data["lastrevid"])+"</origin>\n")
        f2.write('<model>wikibase-property</model>\n')
        f2.write('<format>application/json</format>\n')
        l=line.replace("&","&amp;").replace(">","&gt;").replace("<","&lt;")
        sha1=hashlib.sha1(l.encode()).hexdigest()
        f2.write('<text bytes="'+str(len(l.encode()))+'" sha1="'+sha1+'" xml:space="preserve">\n')
        f2.write(l)
        f2.write('</text>\n')
        f2.write('<sha1>'+sha1+'</sha1>\n')
        f2.write('</revision>\n')
        f2.write('</page>\n')
f2.write('</mediawiki>\n')
f2.close()



                         

