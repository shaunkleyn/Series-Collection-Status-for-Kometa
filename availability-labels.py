# for VS Code install packages using `py -m pip install arrapi` and `py -m pip install plexapi`
from arrapi import SonarrAPI
from plexapi.server import PlexServer
import re
import configparser
import sys
import logging

config = configparser.ConfigParser()
config.read('availability-labels.ini')

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
library_name = plex_library

# label statuses
COMPLETE = 'Complete'
INCOMPLETE = 'Incomplete'
INPROGRESS = 'InProgress'

# Icons used for printing output while processing shows
label_icons = {
    COMPLETE : '🟢',
    INCOMPLETE : '🔴',
    INPROGRESS : '🔵'
}

season_labels = []



#############
## LOGGING ##
#############
logging.basicConfig(filename='log.txt', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
# create logger
logger = logging.getLogger('')
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)



def getTvdbId(series):
    logger.debug('Extracting TVDB ID')
    tvdb = next((guid for guid in series.guids if guid.id.startswith("tvdb")), None)
    match = re.search(r'\d+', tvdb.id)
    return int(match.group()) if match else 0

def setLabel(media_item, label):
    # Remove all labels that were added prior to changing the casing
    media_item.removeLabel('inprogress').removeLabel('incomplete').removeLabel('complete')

    media_item.addLabel(label)
    season_labels.append(label)

    # Remove all other label labels
    if label == COMPLETE:
        media_item.removeLabel(INPROGRESS).removeLabel(INCOMPLETE)
    elif label == INCOMPLETE:
        media_item.removeLabel(INPROGRESS).removeLabel(COMPLETE)
        incomplete_seasons = True
    elif label == INPROGRESS:
        media_item.removeLabel(INCOMPLETE).removeLabel(COMPLETE)
    
    media_item_title = media_item.title

    # If the media item has a property named "seasonNumber" then we want to display it
    if hasattr(media_item, 'seasonNumber'):
        media_item_title = media_item.parentTitle + ' - ' + media_item_title

    logger.debug('Setting ' + media_item_title + ' as "'  + label + '"')
    logger.info(label_icons[label] + ' ' + label + ' ' + media_item_title)


def getPercentOfEpisodes(sonarr_season):
    logger.debug('Getting episode percentage')
    # If Sonarr says that we have 100% of the episodes then it must mean we have all the aired episodes
    # That doesn't mean we have the entire season as there might still be episodes that are still being aired
    # Sonarr will also report that we have 100% of the season if it's not monitored so if it's not monitored we'll
    # calculate the percentage ourself
    percent_of_episodes = sonarr_season.percentOfEpisodes
    if sonarr_season.monitored == False:
        logger.debug('Season not being monitored')
        logger.debug('Calculating percent of episodes')
        percent_of_episodes = (sonarr_season.episodeFileCount / sonarr_season.totalEpisodeCount) * 100

    logger.debug('Using ' + str(percent_of_episodes) + ' instead of ' + str(sonarr_season.percentOfEpisodes))
    return percent_of_episodes

def getSeasonFromPlex(plex_series, episode_number): 
    logger.debug('Getting season from plex')
    return next((season for season in plex_series.seasons() if int(season.seasonNumber) == episode_number), None)

def isLatestSeason(sonarr_season):
    logger.debug('Check if this is the latest season')
    # Some shows, such as Ancient Aliens, have have seasons missing in Sonarr (for instance it jumps from Season 8 to Season 11)
    # resulting in the `seasonCount` being less than the actual number of seasons, therefore we check if the current 
    # `seasonNumber` is greater or equal to the `seasonCount` to determine if we're looking at the latest season
    return sonarr_season.seasonNumber >= sonarr_series.seasonCount

def contains(array, value):
    for item in array:
        if item == value:
            return True
    return False

if len(sys.argv) > 1:
    logger.debug('TVDB ID "' + str(sys.argv[1]) + '" passed as argument')
    tvdb_id_to_process = sys.argv[1]

# Get all shows from the Plex library
logger.debug('Using library ' + library_name)
plex_series_list = plex.library.section(library_name).all()
for plex_series in plex_series_list:
    season_labels.clear()

    # Get the TvDB ID for the show
    tvdb_id = getTvdbId(plex_series)

    # If a TvDB ID has been specified to process a specific show
    # then only continue when we find the show we want to process
    if tvdb_id_to_process is not None and tvdb_id != tvdb_id_to_process:
        continue
    try:
        sonarr_series = sonarr.get_series(tvdb_id=tvdb_id)
    except:
        logger.warn(plex_series.title + ' not found on Sonarr')
        print(plex_series.title + ' not found on Sonarr')

    logger.debug('Processing ' + sonarr_series.title)

    # Some series return 0 episodes so ensure that we actually have episodes to check against
    if sonarr_series is not None and sonarr_series.totalEpisodeCount > 0:
        # Assume the series is complete
        complete_series = True

        logger.debug('Found ' + str(len(sonarr_series.seasons)) + ' seasons')

        # Because Sonarr uses an online source to retrieve series details we'll use
        # Sonarr to identify available seasons for this show (some shows might not have
        # all seasons loaded in Plex due to them being unavailable)
        for sonarr_season in sonarr_series.seasons:
            logger.debug(sonarr_series.title + ' Season ' + str(sonarr_season.seasonNumber) + ' : Total Episodes' + str(sonarr_season.totalEpisodeCount))

            # We don't want to process "special" seasons
            # Sometimes Sonarr would return 0 episodes for a season so we ignore those
            if sonarr_season.seasonNumber > 0 and sonarr_season.totalEpisodeCount > 0:   
                # Find the season on Plex 
                plex_season = getSeasonFromPlex(plex_series, sonarr_season.seasonNumber)
                if plex_season == None:
                    logger.debug(sonarr_series.title + ' Season ' + str(sonarr_series.seasons.count) + ' not found in Plex. Skipping this season')
                    complete_series = False
                else:
                    if getPercentOfEpisodes(sonarr_season) == 100.0:
                        logger.debug('Episode percentage is 100')
                        if sonarr_season.episodeFileCount < sonarr_season.totalEpisodeCount:
                            logger.debug('episodeFileCount: ' + str(sonarr_season.episodeFileCount) + ' < totalEpisodeCount: ' + str(sonarr_season.totalEpisodeCount))
                            setLabel(plex_season, INPROGRESS)
                        else:
                            setLabel(plex_season, COMPLETE)
                    else:
                        # If we don't have the entire season it might be that it's still being aired so let's check for that
                        if isLatestSeason(sonarr_season):
                            logger.debug('This is the latest season')
                            #This is the latest season so we need to check if it's still being aired
                            if sonarr_series.ended == False:
                                logger.debug('Series is still ongoing')
                                # We need to check if we're missing future episodes or historic episodes
                                episodes_not_aired = sonarr_season.totalEpisodeCount - sonarr_season.episodeCount
                                missing_episodes = sonarr_season.episodeCount - sonarr_season.episodeFileCount

                                logger.debug('Episodes not aired: ' + str(episodes_not_aired))
                                logger.debug('Missing episodes: ' + str(missing_episodes))

                                # When there are more episodes missing than those that should still be aired then the season is missing old episodes
                                if episodes_not_aired + missing_episodes > episodes_not_aired:
                                     setLabel(plex_season, INCOMPLETE)
                                else:
                                    setLabel(plex_season, INPROGRESS)
                            else:
                                logger.debug('Series has ended')
                                # The show has ended so it's missing past episodes
                                setLabel(plex_season, INCOMPLETE)
                        else:
                            logger.debug('This is not the latest season')
                            # We're missing episodes from an older season so we need to flag it as INCOMPLETE
                            setLabel(plex_season, INCOMPLETE)

            logger.debug('Season labels are: ' + ', '.join(season_labels))

        if len(season_labels) > 0:              
            # When any season was flagged as INCOMPLETE then we label the entire Show as INCOMPLETE
            if contains(season_labels, INCOMPLETE):
                logger.debug('Season labels contains INCOMPLETE')
                logger.debug('Setting Series label INCOMPLETE')
                setLabel(plex_series, INCOMPLETE)
            elif season_labels.pop() == INPROGRESS:
                logger.debug('Last season label is INPROGRESS')
                logger.debug('Setting Series label INPROGRESS')
                # When no season was flagged as INCOMPLETE and the last season is INPROGRESS then the Show is INPROGRESS
                setLabel(plex_series, INPROGRESS)
            else:
                logger.debug('Season labels do not contain INCOMPLETE and last season is not INPROGRESS')
                logger.debug('Setting Series label COMPLETE')
                # When no season was flagged as INCOMPLETE and the last season is not INPROGRESS then the Show is COMPLETE
                setLabel(plex_series, COMPLETE)

print('Done')

