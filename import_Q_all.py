import os
import sys
import time 
import compress_pickle
import json
import pickle
import indexed_bzip2
import hashlib
import subprocess 
import multiprocessing
import threading
import queue
import psutil

def worker():
    while True:
        item = q.get()
        upload(item)
        q.task_done()

def upload(items):
    init=False
    for line in items:
        l=line#.replace("&","&amp;").replace(">","&gt;").replace("<","&lt;")
        data=json.loads(line)
        q=data["id"]
        if not init:
            fn="Q/"+q+".xml"
            f2=open(fn,"w")
            f2.write('<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.11/ http://www.mediawiki.org/xml/export-0.11.xsd" version="0.11" xml:lang="en">\n')
            f2.write('<siteinfo><namespaces><namespace key="120" case="first-letter">Item</namespace></namespaces></siteinfo>\n')
            init=True
        f2.write('<page>\n')
        f2.write('<title>'+q+'</title>\n')
        f2.write('<ns>120</ns>\n')
        f2.write('<id>'+str(data["pageid"])+'</id>\n')
        f2.write('<revision>')
        f2.write('<id>'+str(data["lastrevid"])+"</id>\n")
        #f2.write('<parentid>'+parentid+"</parentid>\n")
        f2.write('<timestamp>'+data["modified"]+"</timestamp>\n")
        f2.write('<origin>'+str(data["lastrevid"])+"</origin>\n")
        f2.write('<model>wikibase-item</model>\n')
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
    result = subprocess.run("php /usr/share/mediawiki/maintenance/importDump.php < "+fn+" 2>&1 > "+fn+".out", capture_output = True, shell = True)
    s=str(result.stdout)
    os.remove(fn)
    q2.put(fn)

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

print("seeking to end of compressed file to find uncompressed size")
file.seek(0, os.SEEK_END)
tot = file.tell()
print(tot)

step=1000

bindex=0

nproc=psutil.cpu_count(logical=True)
q = queue.Queue(maxsize=4*nproc)
q2 = queue.Queue()

threads=[]
for i in range(nproc):
    t=threading.Thread(target=worker, daemon=True)
    t.start()
    threads.append(t)

file.seek(0)
line=file.readline().decode("utf-8")
plast=-1
items=[]
t0=time.time()

pnot=0
while True:
    p=file.tell()
    line=file.readline().decode("utf-8")
    if p==plast:
        break
    i0=find_nth(line,"\"",6)+1
    i1=find_nth(line,"\"",7)
    item=line[i0:i1]
    if not item.startswith("Q"):
        i0=find_nth(line,"\"",10)+1
        i1=find_nth(line,"\"",11)
        item=line[i0:i1]
        if not item.startswith("P"):
            try:
                item=json.loads(line.strip()[:-1])["id"]
            except:
                print("not using pos",p)
                pass
    if item.startswith("Q"):
        items.append(line.strip()[:-1])
    if len(items)==step or p==plast:
        while q.full():
            time.sleep(0.1)
        last=""
        while not q2.empty():
            last=q2.get()
            bindex=bindex+1
            q2.task_done()
        item=json.loads(items[0])["id"]
        done=False
        if os.path.isfile("Q/"+item+".xml.out"):
            fout=open("Q/"+item+".xml.out")
            try:
                if fout.read().splitlines()[0].startswith("Done"):
                    done=True
            except:
                pass
            fout.close()
        if not done:    
            q.put(items)
        else:
            pnot=pnot+(p-plast)
        items=[]
        
        p2=p-pnot
        r=bindex*step/(time.time()-t0)
        r2=p2/(time.time()-t0)+0.00000000001
        print(p/tot*100,"% done,",last,r,"items per second,",(tot-p)/r2/3600,"h remaining,",step*(bindex),"elements done,",q.qsize(),"in queue                                       ", end="")
        print("\r", end="")
    if plast==p:
        break
    plast=p
q.join()
