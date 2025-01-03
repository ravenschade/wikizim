#!/bin/bash
rm -rf zimdump
zimdump dump --dir=zimdump -- $1
rm -rf zimdump/A
rm -rf zimdump/X
rm -rf zimdump/M
rm -rf zimdump/_exceptions
rm -rf zimdump/-

python3 zim_images_import.py zimdump/I
rm -rf zimdump
