# for VS Code install packages using `py -m pip install arrapi` and `py -m pip install plexapi`
from arrapi import SonarrAPI
from plexapi.server import PlexServer
import re
import configparser

config = configparser.ConfigParser()
config.read('set-label-labels.ini')

# Plex
plex_url = config['plex']['url']
plex_token = config['plex']['token']
plex_library = config['plex']['library']

# Sonarr
sonarr_url = config['sonarr']['url']
sonarr_api_key = config['sonarr']['apikey']

plex = PlexServer(plex_url, plex_token)
sonarr = SonarrAPI(sonarr_url, sonarr_api_key)

tvdb_id_to_process = None
libraryName = plex_library

# label statuses
COMPLETE = 'Complete'
INCOMPLETE = 'Incomplete'
INPROGRESS = 'InProgress'

# Icons used for printing output while processing shows
labelIcons = {
    COMPLETE : '🟢',
    INCOMPLETE : '🔴',
    INPROGRESS : '🔵'
}


def getTvdbId(series):
    tvdb = next((obj for obj in series.guids if obj.id.startswith("tvdb")), None)
    match = re.search(r'\d+', tvdb.id)
    return int(match.group()) if match else 0


def setLabel(mediaItem, label):
    mediaItem.addLabel(label)

    # Remove all other label labels
    if label == COMPLETE:
        mediaItem.removeLabel(INPROGRESS).removeLabel(INCOMPLETE)
    elif label == INCOMPLETE:
        mediaItem.removeLabel(INPROGRESS).removeLabel(COMPLETE)
    elif label == INPROGRESS:
        mediaItem.removeLabel(INCOMPLETE).removeLabel(COMPLETE)
    
    mediaItemTitle = mediaItem.title

    # If the media item has a property named "seasonNumber" then we want to display it
    if hasattr(mediaItem, 'seasonNumber'):
        mediaItemTitle = mediaItem.parentTitle + ' - ' + mediaItemTitle

    print(labelIcons[label] + ' ' + mediaItemTitle)  


# Get all shows from the Plex library
plex_shows = plex.library.section(libraryName).all()
for plex_series in plex_shows:
    # Get the TvDB ID for the show
    tvdb_id = getTvdbId(plex_series)
    # If a TvDB ID has been specified to process a specific show
    # then only continue when we find the show we want to process
    if tvdb_id_to_process is not None and tvdb_id != tvdb_id_to_process:
        continue

    try:
        sonarr_series = sonarr.get_series(tvdb_id=tvdb_id)
    except:
        print(plex_series.title + ' not found on Sonarr')

    # Some series return 0 episodes so ensure that we actually have episodes to check against
    if sonarr_series is not None and sonarr_series.totalEpisodeCount > 0:

        # Assume the series is complete
        complete_series = True

        # Because Sonarr uses an online source to retrieve series details we'll use
        # Sonarr to identify available seasons for this show (some shows might not have
        # all seasons loaded in Plex due to them being unavailable)
        for sonarr_season in sonarr_series.seasons:
            if sonarr_season.seasonNumber > 0 and sonarr_season.totalEpisodeCount > 0:    
                plex_season = next((obj for obj in plex_series.seasons() if int(obj.seasonNumber) == sonarr_season.seasonNumber), None)
                if plex_season:
                    complete_season = sonarr_season.percentOfEpisodes == 100.0
                    if sonarr_season.seasonNumber >= sonarr_series.seasonCount:
                        if sonarr_season.episodeFileCount < sonarr_season.totalEpisodeCount:
                            if sonarr_series.status == 'continuing':
                                setLabel(plex_season, INPROGRESS)

                                if complete_series == True: 
                                    setLabel(plex_series, INPROGRESS) 
                                    complete_season = None
                                    break
                            else:
                                setLabel(plex_season, INCOMPLETE) 
                                complete_series = False
                        else:
                            complete_season = True
                            setLabel(plex_season, COMPLETE)
                    else:
                        if complete_season:
                            setLabel(plex_season, COMPLETE)
                        else:
                            setLabel(plex_season, INCOMPLETE) 
                            complete_series = False
                else:
                    complete_series = False

        if complete_season is not None:
            if complete_series == True:
                setLabel(plex_series, COMPLETE) 
            else:
                setLabel(plex_series, INCOMPLETE)

print('Done')

