# wikizim
Guide and scripts for creating up-to-date ZIM files for the Wikipedias

# THIS GUIDE IS WORK IN PROGRESS

# Requirements
* a Linux system with several TB of fast storage
* probably at least 32-64 GB of RAM
* stuff to run mediawiki (apache2, php, mariadb, imagemagick,...)
* ZIM tools (zimdump, Debian package `zim-tools`)
* Python

# Test Setup
* AMD 3950X, 16 core
* 128 GB RAM
* 2x Samsung 980 Pro 2TB SSDs im RAID0
* Debian testing
* Mediawiki 1.39.10
* Mariadb 11.4.3
* Python 3.12.7

# Mediawiki Setup
1. Configure Mariadb:
```
innodb_buffer_pool_size = 80G #assuming 128GB RAM, otherwise reduce
innodb_flush_log_at_trx_commit=0
innodb_flush_method=O_DIRECT_NO_FSYNC
innodb_file_per_table=ON
```
2. Set up mediawiki as usual.
3. Install required extensions. The required extensions can be found in the template mediawiki configuration file `mediawiki/LocalSettings.php`.

# Wikidata
1. Configure the Mediawiki extensions for Wikibase repo and client. It can be found in the template mediawiki configuration file `mediawiki/LocalSettings.php`.
2. Test wikibase setup:
    1. Export one item from Wikidata as xml: `wget https://www.wikidata.org/wiki/Special:Export/Q2971 -O Q2971.xml`
    2. Change namespace: 
        a. `<ns>0</ns>` to `<ns>120</ns>` (wikdata uses namespace 0 for items but we want to use 120)
        b. `<namespace key="120" case="first-letter">Property</namespace>` to `<namespace key="120" case="first-letter">Item</namespace>`
    3. Import by running `php /usr/share/mediawiki/maintenance/importDump.php < Q2971.xml`
    4. Check that the import successeded by visiting http://localhost/w/index.php/Item:Q2971 of your wiki.
3. Download `latest-all.json.bz2` from https://dumps.wikimedia.org/wikidatawiki/entities/. Do not decompress. All of the following will work directly with the compressed file.
4. Create Python environment for Pyhtons scripts by running `bash create_venv.sh`
5. Activate Python virtual environment by running `source venv/bin/activate`
6. Import of Properties:
    1. (a few minutes) run `python3 extract_P.py latest-all.json.bz2`
    2. (a few minutes) Import the resulting `P.xml` into mediawiki with `php /usr/share/mediawiki/maintenance/importDump.php < P.xml`.
7. Import of Items:
    1. run `mkdir Q` (state directory for items)
    2. (about two days, but can be interupted and continued) run `python3 import_Q_all.py latest-all.json.bz2`
        * On the setup described above, the import rate is about 600 items/s. The import of the full wikidata took about 2 days (December 2024).

# Wikipedia
## Images from ZIM
* Downloading all images from wiki commons will be problematic due to the load it causes. As a workaround we extract images from the existing wikipedia ZIM files that can be found at `https://download.kiwix.org/zim/wikipedia/`. They won't have all images that are needed but a huge fraction.
* Steps:
    1. Download recent ZIM file of a wikipedia that contains images, e.g. `wikipedia_de_all_maxi` or `wikipedia_en_all_maxi`
    2. Extract and import images from zim with `bash import_images_from_zim.sh [ZIM file]`
        * On the setup described above, the import rate is about 800 images/s. The import of all images from `wikipedia_en_all_maxi_2024-01.zim` took about 3 hours.

## Text
1. Download multistream xml dump and index from wikimedia ``or a mirror `https://dumps.wikimedia.org/mirrors.html`, i.e., `[lang]wiki-[data]-pages-articles-multistream.xml.bz2` and `[lang]wiki-[data]-pages-articles-multistream-index.txt.bz2`.
2. Run import `python3 import_wiki_articles.py [lang]wiki-[data]-pages-articles-multistream-index.txt.bz2 [lang]wiki-[data]-pages-articles-multistream.xml.bz2` 
    * On the setup described above, the import rate is about FIXME pages/s. The import of all pages from `enwiki-20241220-pages-articles-multistream.xml.bz2` took FIXME days.

## Missing Images and Files


# ZIM Build
