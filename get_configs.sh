mkdir mediawiki
cat /etc/mediawiki/LocalSettings.php | grep -v wgSecretKey | grep -v wgUpgradeKey | grep -v wgDBpassword > mediawiki/LocalSettings.php
