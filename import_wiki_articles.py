import os
import sys
import time 
import json
import pickle
import indexed_bzip2
import hashlib
import subprocess 
import multiprocessing
import threading
import queue
import psutil
import bz2
import tempfile
import tqdm 

def import_articles(block):
    fa=open(block["file"],"rb")
    fa.seek(block["start"])
    dec=bz2.BZ2Decompressor()
    block_size=128*1024
    text=b""
    while True:
        comp = fa.read(block_size)
        try:
            text += dec.decompress(comp)
        except EOFError:
            break
        if comp == '':
            break
    if not dec.eof:
        raise Exception("Failed to read a complete stream")
    fa.close()
    temp = tempfile.NamedTemporaryFile(delete=False,mode="wt")
    text=text.decode("utf-8")
    text=text.replace(".svg|",".svg.png|")
    text=text.replace(".gif|",".gif.png|")
    text=text.replace(".svg</title>",".svg.png</title>")
    text=text.replace(".gif</title>",".gif.png</title>")
    temp.write('<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.11/ http://www.mediawiki.org/xml/export-0.11.xsd" version="0.11" xml:lang="en">\n')
    temp.write(text)
    temp.write('</mediawiki>\n')
    temp.close()
    result = subprocess.run("php /usr/share/mediawiki/maintenance/importDump.php < "+temp.name, capture_output = True, shell = True)
    s=str(result.stdout)
    os.remove(temp.name)

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

nproc=psutil.cpu_count(logical=False)

index=sys.argv[1]
articles=sys.argv[2]

findex = indexed_bzip2.open( index, parallelization = nproc)

print("reading index")
blocks=[]
plast=-1
while line := findex.readline():
    p=int(line.decode("utf-8").split(":")[0])
    if p!=plast and plast!=-1:
        blocks.append({"start":plast,"end":p,"file":articles})
    plast=p
findex.close()

print(len(blocks),"blocks of 100 pages each")

print("import articles")

nproc=psutil.cpu_count(logical=True)

pool = multiprocessing.Pool(processes=nproc)
for _ in tqdm.tqdm(pool.imap_unordered(import_articles, blocks), total=len(blocks),unit="pages",unit_scale=100):
    pass
