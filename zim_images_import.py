import sys
import os
import subprocess
import tqdm
import multiprocessing
from os import listdir
from os.path import isfile, join
import psutil
import tempfile
import time
import os
from urllib.parse import unquote


def conv(fb):
    temp_dir = tempfile.TemporaryDirectory()
    for f in fb:
        f2=unquote(f[1])
        cmd = "/usr/bin/convert \'"+f[0]+"\' \'"+temp_dir.name+"/"+f2+"\'"
        o=subprocess.run(cmd, shell=True,capture_output=True, text=True)
        os.remove(f[0])
    cmd="php /usr/share/mediawiki/maintenance/importImages.php "+temp_dir.name
    o=subprocess.run(cmd, shell=True,capture_output=True, text=True)
    temp_dir.cleanup()

d=sys.argv[1]
nproc=psutil.cpu_count(logical=True)
#nproc=1

onlyfiles = [f for f in listdir(d) if isfile(join(d, f))]

batch=100

webps=[]
webp=[]
endings={}
for f in onlyfiles:
    if f.endswith(".webp"):
        f2=f.replace(".webp","")
        if len(webp)==batch:
            webps.append(webp)
            webp=[]
        webp.append([d+"/"+f,f2])
    e=f.split(".")[-1]
    if not (e in endings):
        endings[e]=0
    endings[e]=endings[e]+1
webps.append(webp)

print("counts of file extensions in dump")
for e in endings:
    print(e,endings[e])

pool = multiprocessing.Pool(processes=nproc)
for _ in tqdm.tqdm(pool.imap_unordered(conv, webps), total=len(webps)):
    pass


