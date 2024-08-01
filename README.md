# Series Collection Status in Plex using Kometa
<img  alt="Screenshot 2024-08-01 at 18 34 46-min" src="https://github.com/user-attachments/assets/ffda5919-1d2c-4953-be22-02818469214f">


## Background
I wanted to be able to easily see on Plex if a show has been downloaded in full or if there are missing episodes or seasons. After searching around for days for something that can do it I finally asked for some help from the guys on the [Kometa Discord group](https://discord.gg/NfH6mGFuAB) and SirGareth [confirmed](https://discord.com/channels/822460010649878528/822460010649878531/1061099419153469571) that [Kometa](https://metamanager.wiki/en/latest/index.html) (formaly know as PMM) would not be able to do it but that I'd be able to do it using a few API's to add labels to Plex and then use Kometa to add overlays using those labels.

Being a newbie to both Python and Kometa I am sure there are neater and better ways to accomplish this but this is the script and configs I came up with that is currently working for me.  

**NOTE:**
I created this for my own personal use and sharing it so that anyone can change it to their liking and requirements.


## The script
The script is far from perfect and there are a few bugs but thus far it's working for most of the shows. It makes use of [ArrApi](https://arrapi.metamanager.wiki/en/latest/index.html) and [Python PlexAPI](https://python-plexapi.readthedocs.io/en/latest/introduction.html) to check whether a show or season is complete and then adds a Plex label to it that can then later be used by Kometa to create overlays.

## The Kometa configs
There are 2 configs (I'm sure there's a way to only use 1 but still have a lot to learn), one to create the overlays for Shows and the other to create overlays for Seasons. 

## How to use this
(Basic Python and Kometa knowledge required)
1. Download all files in this repo
2. Copy the Python script to a folder of your preference (I suggest creating a dedicated folder for the script as we'll be using a Python virtual environemt to run it)
3. Configure your URL's and API key & token in the `set-availability-labels.ini` file
4. Using a terminal / command prompt, `cd` to the script's directory
5. Run the following to create a virtual environment `python -m venv .venv` or `python3 -m venv .venv` (check which one works for you)
6. Activate the virtual environment using `.venv\Scripts\activate`
7. Install ArrAPI using `pip install arrapi`
8. Install Python PlexAPI using `pip install plexapi`
9. Run the script using `python set-availability-labels.py`
10. Update your Kometa config to include the "availability.yml" configs and copy the overlays to your overlays folder
11. Run Kometa

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

<img  alt="Screenshot 2024-08-01 at 18 34 46-min" src="https://github.com/user-attachments/assets/8074cca6-a63c-4496-a38c-82ccb827bf1a">

You can see that "Dr Who" is incomplete (by the orange border).  If I go into "Dr Who" you can see that Season 1 and Season 2 is complete (green border), Season 3 has missing episodes and Season 4 and Season 5 are also complete.

<img  alt="Screenshot 2024-08-01 at 18 33 53-min" src="https://github.com/user-attachments/assets/896bcc4b-6a58-44c6-a254-b26de154dfc5">



