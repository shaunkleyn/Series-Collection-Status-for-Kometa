# PMM-Config

## Background
I wanted to be able to easily see on Plex if a show has been downloaded in full or if there are missing episodes or seasons. After searching around for days for something that can do it I finally asked for some help from the guys on the PMM Discord group and they confirmed that PMM would not be able to do it but that I'd be able to do it using a few API's to add labels to Plex and then use PMM to add overlays using those labels.

Being a newbie to both Python and PMM I am sure there are neater and better ways to accomplish this but this is the script and configs I came up with that is currently working for me.  

## The script
The script is far from perfect and I'm expecting a few bugs but thus far it's working for most of the shows. It makes use of [ArrApi](https://arrapi.metamanager.wiki/en/latest/index.html) and [Python PlexAPI](https://python-plexapi.readthedocs.io/en/latest/introduction.html) to check whether a show / season is complete and then adds a Plex label to it that can later then be used by PMM to create overlays.

## The PMM configs
There are 2 configs (I'm sure there's a way to only use 1 but still have a lot to learn), one to create the overlays for Shows and the other to create overlays for Seasons. 

## The Plex labels
Show can either be complete, meaning all the seasons and episodes are availabe on disk, or incomplete, meaning some seasons or episodes are missing.  However, if there's a new show or season that are being aired not all episodes will be available yet and I don't want to label it as "incomplete" because the missing episodes aren't available yet.  Due to this I had to an "In progress" label.

In short the labels are:
* Complete: All seasons and episodes have been downloaded
* Incomplete: Some episodes or entire seasons are missing and should still be downloaded
* In Progress: All seasons and episodes have been downloaded but the latest season is still being aired
