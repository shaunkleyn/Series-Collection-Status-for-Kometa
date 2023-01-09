# PMM-Config for Series Availability borders in Plex

## Background
I wanted to be able to easily see on Plex if a show has been downloaded in full or if there are missing episodes or seasons. After searching around for days for something that can do it I finally asked for some help from the guys on the [Plex Meta Manager Discord group](https://discord.gg/NfH6mGFuAB) and SirGareth [confirmed](https://discord.com/channels/822460010649878528/822460010649878531/1061099419153469571) that [Plex Meta Manager](https://metamanager.wiki/en/latest/index.html) (PMM) would not be able to do it but that I'd be able to do it using a few API's to add labels to Plex and then use PMM to add overlays using those labels.

**NOTE:** 
I created this for personal use and sharing it so that anyone can change it to their liking and requirements. 

Being a newbie to both Python and PMM I am sure there are neater and better ways to accomplish this but this is the script and configs I came up with that is currently working for me.  

## The script
The script is far from perfect and there are a few bugs but thus far it's working for most of the shows. It makes use of [ArrApi](https://arrapi.metamanager.wiki/en/latest/index.html) and [Python PlexAPI](https://python-plexapi.readthedocs.io/en/latest/introduction.html) to check whether a show or season is complete and then adds a Plex label to it that can then later be used by PMM to create overlays.

## The PMM configs
There are 2 configs (I'm sure there's a way to only use 1 but still have a lot to learn), one to create the overlays for Shows and the other to create overlays for Seasons. 

## How to use this
(Basic Python and PMM knowledge required)
1. Download all files in this repo
2. Copy the Python script to a folder of your preference (I suggest creating a dedicated folder for the script as we'll be using a Python virtual environemt to run it)
3. Configure your URL's and API key & token in the `set-availability-labels.ini` file
4. Using a terminal / command prompt, `cd` to the script's directory
5. Run the following to create a virtual environment `python -m venv pmm-venv` or `python3 -m venv pmm-venv` (check which one works for you)
6. Activate the virtual environment using `pmm-venv\Scripts\activate`
7. Install ArrAPI using `pip install arrapi`
8. Install Python PlexAPI using `pip install plexapi`
9. Run the script using `python set-availability-labels.py`
10. Update your PMM config to include the "availability.yml" configs and copy the overlays to your overlays folder
11. Run PMM

## The Plex labels
Show can either be complete, meaning all the seasons and episodes are availabe on disk, or incomplete, meaning some seasons or episodes are missing.  However, if there's a new show or season that are being aired not all episodes will be available yet and I don't want to label it as "incomplete" because the missing episodes aren't available yet.  Due to this I had to an "In progress" label.

In short the labels are:
* Complete: All seasons and episodes have been downloaded
* Incomplete: Some episodes or entire seasons are missing and should still be downloaded
* In Progress: All seasons and episodes have been downloaded but the latest season is still being aired

## Todo / bugs
- Allow usage with Sonarr so that it can pass an ID of a series.  The script should then only update that specific series.
- Show is incorrectly being labeled as "In Progress" when all episodes have already been aired, its status is "Continuing" on Sonarr but yet episodes from last season is missing.  The show should actually be labeled as "Incomplete" then.
- Probably more to come...

## What it looks like
I decided to use borders to display the availability of shows and seasons.  The border overlays are as follows:
* Green = Complete
* Orange = Incomplete
* Blue = In Progress

![image](https://user-images.githubusercontent.com/10231893/211212798-9be5abac-8728-4a53-a714-565f23663623.png)

You can see that "Evil Online" is incomplete (by the orange border).  If I go into "Evil Online" you can see that Season 1 is complete (green border), Season 2 is missing and Season 3 has episodes missing (orange border).

<img src="https://user-images.githubusercontent.com/10231893/211212821-0181fa2b-9ba1-4e49-aa53-592e6ea205ac.png" alt="drawing" height="300"/>



