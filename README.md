# wikizim
Guide and scripts for creating up-to-date ZIM files for the Wikipedias

# Requirements
* a Linux system with several TB of fast storage
* probably at least 32-64 GB of RAM
* stuff to run mediawiki (apache2, php, mariadb, imagemagick,...)

# Test setup
* AMD 3950X, 16 core
* 128 GB RAM
* 2x Samsung 980 Pro 2TB SSDs
* Debian testing
* Mediawiki 1.39.10
* Mariadb 11.4.3
* Python 3.12.7

# Mediawiki setup
1. Set up mediawiki as usual.
2. Install required extensions. The required extensions can be found in the template mediawiki configuration file `mediawiki/LocalSettings.php`.

# Wikidata
1. Configure the Mediawiki extensions for Wikibase repo and client. It can be found in the template mediawiki configuration file `mediawiki/LocalSettings.php`.
2. Test wikibase setup:
    1. Export one item from Wikidata as xml: `wget https://www.wikidata.org/wiki/Special:Export/Q2971 -O Q2971.xml`
    2. Change namespace: 
        a. `<ns>0</ns>` to `<ns>120</ns>` (wikdata uses namespace 0 for items but we want to use 120)
        b. `<namespace key="120" case="first-letter">Property</namespace>` to `<namespace key="120" case="first-letter">Item</namespace>`
    3. Import by running `php /usr/share/mediawiki/maintenance/importDump.php < Q2971.xml`
    4. Check that the import successeded by visiting http://localhost/w/index.php/Item:Q2971 of your wiki.
3. Download `latest-all.json.bz2` from https://dumps.wikimedia.org/wikidatawiki/entities/
4. Import of Properties:
  * 
5. Import of Items:

# Wikipedia
## Text


## Images


# ZIM build
