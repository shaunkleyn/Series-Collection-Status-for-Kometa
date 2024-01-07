# ⇧⌘P) To set interpreter - 3.8.2 - Global
# for VS Code install packages using `py -m pip install arrapi` and `py -m pip install plexapi`
from arrapi import SonarrAPI
from plexapi.server import PlexServer, NotFound
#from dotenv import load_dotenv
import re
import configparser
import sys
import logging
from datetime import datetime
from os import environ
import os
import traceback
import pathlib
import inspect
from ruamel.yaml import YAML

# current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parent_dir = os.path.dirname(current_dir)
# sys.path.insert(0, parent_dir)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
#fldr = sys.path.append(os.path.dirname(SCRIPT_DIR))

PACKAGE_PARENT = pathlib.Path(__file__).parent
#PACKAGE_PARENT = pathlib.Path.cwd().parent # if on jupyter notebook
SCRIPT_DIR = PACKAGE_PARENT / "my_Folder_where_the_package_lives"
fldr = sys.path.append(str(SCRIPT_DIR))


current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)
default_dir = parent_dir

with open(os.path.join(default_dir, 'config', 'config.yml')) as f:
    yaml = YAML()
    data = yaml.load(f)
    print(type(data))
    print("all: ", data)
    print(dict(data)) 


# from modules.builder import CollectionBuilder
# from modules import util, radarr, sonarr, operations
# from modules.logs import MyLogger
# from plex_meta_manager import run_args, util, final_vars, ConfigFile
# logger = MyLogger("Plex Meta Manager", default_dir, run_args["width"], run_args["divider"][0], run_args["ignore-ghost"],
#                   run_args["tests"] or run_args["debug"], run_args["trace"], run_args["log-requests"])
# util.logger = logger
# from modules.config import ConfigFile



#default_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'config'))
#default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
#load_dotenv(os.path.join(default_dir, ".env"))
# config = ConfigFile.get()
#config = ConfigFile

config = configparser.ConfigParser()
config.read('availability-labels.ini')

# Plex
plex_url = dict(data)['plex']['url'] #config['plex']['url']
plex_token = dict(data)['plex']['token'] #config['plex']['token']
#plex_library = dict(data)['plex']['url'] #config['plex']['library']
plex_library = ''

# Sonarr
sonarr_url = dict(data)['sonarr']['url'] #config['sonarr']['url']
sonarr_api_key = dict(data)['sonarr']['token'] #config['sonarr']['apikey']

libraries = []

plex = PlexServer(plex_url, plex_token,timeout=120)
seriesId = ""
# library_name = plex_library

for library in dict(data)['libraries']:
    try:
        if plex.library.section(library).type == 'show':
            libraries.append(library)
    except NotFound:
        continue

sonarr = SonarrAPI(sonarr_url, sonarr_api_key)

# label statuses
COMPLETE = 'Complete'
INCOMPLETE = 'Incomplete'
INPROGRESS = 'InProgress'
RETURNING = 'Returning'

# Icons used for printing output while processing shows
label_icons = {
    COMPLETE : '🟢',
    INCOMPLETE : '🔴',
    INPROGRESS : '🔵',
    RETURNING : '🔵'
}

#############
## LOGGING ##
#############
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log.txt')

logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
# create logger
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

logger.info('Checking configuration')

season_labels = []

def main():
    tvdb_id_to_process = 0

    def getTvdbId(series):
        logger.debug('Extracting TVDB ID')
        tvdb = next((guid for guid in series.guids if guid.id.startswith("tvdb")), None)
        match = re.search(r'\d+', tvdb.id)
        
        return int(match.group()) if match else 0

    def setLabel(media_item, label):
        made_changes = False
        season_labels.append(label)
        if hasattr(media_item, 'labels'):
            if next((obj for obj in media_item.labels if obj.tag == label), None) is None:
                media_item.addLabel(label, False)
                made_changes = True
            labels_to_remove = []
            try:
                # Remove all other label labels
                if label == COMPLETE:
                    if next((obj for obj in media_item.labels if obj.tag == INPROGRESS), None):
                        labels_to_remove.append(INPROGRESS)
                    if next((obj for obj in media_item.labels if obj.tag == INCOMPLETE), None):
                        labels_to_remove.append(INCOMPLETE)
                    #media_item.removeLabel(INPROGRESS, INCOMPLETE)
                elif label == INCOMPLETE:
                    #media_item.removeLabel(INPROGRESS).removeLabel(COMPLETE)
                    if next((obj for obj in media_item.labels if obj.tag == INPROGRESS), None):
                        labels_to_remove.append(INPROGRESS)
                    if next((obj for obj in media_item.labels if obj.tag == COMPLETE), None):
                        labels_to_remove.append(COMPLETE)
                    incomplete_seasons = True
                elif label == INPROGRESS:
                    if next((obj for obj in media_item.labels if obj.tag == COMPLETE), None):
                        labels_to_remove.append(COMPLETE)
                    if next((obj for obj in media_item.labels if obj.tag == INCOMPLETE), None):
                        labels_to_remove.append(INCOMPLETE)
                    #media_item.removeLabel(INCOMPLETE).removeLabel(COMPLETE)
                
                if len(labels_to_remove) > 0:
                    made_changes = True
                    media_item.removeLabel(labels_to_remove)
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(f'Could not read all configurations: {e}')
        media_item_title = media_item.title

        # If the media item has a property named "seasonNumber" then we want to display it
        if hasattr(media_item, 'seasonNumber'):
            new_media_item_title = media_item.parentTitle + ' - ' + media_item_title

        logger.debug('Setting ' + media_item_title + ' as "'  + label + '"')
        logger.info(f'\t{label_icons[label]} {media_item_title}\t {label}')

        return made_changes

    def syncLabels(media_item, add_labels, remove_labels):
        made_changes = False
        logger.debug(f'Syncing labels...')
        logger.debug(f'\t To Add: {add_labels}')
        logger.debug(f'\t To Remove: {remove_labels}')
        if hasattr(media_item, 'labels'):
            for media_item_label in media_item.labels:
                item_to_remove = find(remove_labels, media_item_label.tag)
                if item_to_remove is not None:
                    logger.debug(f'Found potential label to remove: {item_to_remove}')
                    if not any(x.lower() == item_to_remove.lower() for x in add_labels):
                        media_item.removeLabel(item_to_remove)
                        made_changes = True
                    else:
                        logger.debug(f'Label to remove ({item_to_remove}) matches a label that should be added so not removing it')

            for new_label in add_labels:
                # if next((obj for obj in media_item.labels if obj.tag.lower == new_label.lower), None) == None:
                if not any(x.tag.lower() == new_label.lower() for x in media_item.labels):
                    media_item.addLabel(new_label)
                    logger.debug(f'Adding label: {new_label}')
                    made_changes = True
        if not made_changes:
            logger.debug('No changes changes maded to labels')
        else: 
            logger.info('Changes were made to labels')
        return made_changes


    def getPercentOfEpisodes(sonarr_season, sonarr_series):
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

        if sonarr_series.ended == True or (sonarr_series.nextAiring != None and sonarr_series.nextAiring.date() < datetime.today().date()):
            percent_of_episodes = (sonarr_season.episodeFileCount / sonarr_season.totalEpisodeCount) * 100
            logger.debug('Show has ended')
            return percent_of_episodes           
        
        logger.debug('Using ' + str(percent_of_episodes) + ' instead of ' + str(sonarr_season.percentOfEpisodes))
        return percent_of_episodes

    def getSeasonFromPlex(plex_series, episode_number): 
        logger.debug('Getting season from plex')
        return next((season for season in plex_series.seasons() if int(season.seasonNumber) == episode_number), None)


    def contains(array, value, exact_match = True):
        if isinstance(value, str):
            value = value.lower()
            
        for item in array:
            if isinstance(item, str):
                item = item.lower()

            if exact_match == True and item == value:
                return True
            elif exact_match == False and value in item:
                return True
        return False
    
    def find(array, value, exact_match = True):
        if isinstance(value, str):
            value = value.lower()

        for item in array:
            if isinstance(item, str):
                item = item.lower()

            exact_match = '%' not in item
            item = item.replace('%', '')

            if exact_match == True and item == value:
                return value
            elif exact_match == False and item in value:
                return value
        return None

    def isLatestSeason(sonarr_season):
        logger.debug('Check if this is the latest season')
        # Some shows, such as Ancient Aliens, have have seasons missing in Sonarr (for instance it jumps from Season 8 to Season 11)
        # resulting in the `seasonCount` being less than the actual number of seasons, therefore we check if the current 
        # `seasonNumber` is greater or equal to the `seasonCount` to determine if we're looking at the latest season
        return sonarr_season.seasonNumber >= sonarr_series.seasonCount
    
    for library in libraries:
        plex_series_list = []
        if len(sys.argv) > 1:
            logger.info('TVDB ID "' + str(sys.argv[1]) + '" passed as argument')
            tvdb_id_to_process = int(sys.argv[1])
        elif environ.get('sonarr_series_tvdbid') is not None:
            logger.info('TVDB ID "' + str(environ.get('sonarr_series_tvdbid')) + '" passed as argument from Sonarr')
            tvdb_id_to_process = int(environ.get('sonarr_series_tvdbid'))
        
        if tvdb_id_to_process > 0:
            try:
                item = plex.library.section(library).getGuid('tvdb://' + str(tvdb_id_to_process))
                plex_series_list.append(item)
            except:
                logger.warning(f'item {str(tvdb_id_to_process)} does not exist in {library} on Plex')
                return
        else:
            plex_series_list = plex.library.section(library).all()
        
        # Get all shows from the Plex library
        logger.debug('Using library ' + library)
        logger.debug(plex_series_list.count)
        for plex_series in plex_series_list:
            season_labels.clear()
            changes_made = []
            # Get the TvDB ID for the show
            try:
                tvdb_id = getTvdbId(plex_series)
            except:
                continue
            
            # If a TvDB ID has been specified to process a specific show
            # then only continue when we find the show we want to process
            
            if tvdb_id_to_process is not None and tvdb_id_to_process > 0 and tvdb_id != int(tvdb_id_to_process):
                continue
            try:
                sonarr_series = sonarr.get_series(tvdb_id=tvdb_id)
            except:
                logger.warn(plex_series.title + ' not found on Sonarr')

            logger.info(sonarr_series.title)
            # Some series return 0 episodes so ensure that we actually have episodes to check against
            if sonarr_series is not None and sonarr_series.totalEpisodeCount > 0:
                # Assume the series is complete
                complete_series = True
                
                logger.debug('Found ' + str(len(sonarr_series.seasons)) + ' seasons')
        
                # Because Sonarr uses an online source to retrieve series details we'll use
                # Sonarr to identify available seasons for this show (some shows might not have
                # all seasons loaded in Plex due to them being unavailable)
                for sonarr_season in sonarr_series.seasons:
                    logger.debug(sonarr_series.title + ' Season ' + str(sonarr_season.seasonNumber) + ' : Total Episodes ' + str(sonarr_season.totalEpisodeCount))
        
                    # We don't want to process "special" seasons
                    # Sometimes Sonarr would return 0 episodes for a season so we ignore those
                    if sonarr_season.seasonNumber > 0 and sonarr_season.totalEpisodeCount > 0:   
                        # Find the season on Plex 
                        plex_season = getSeasonFromPlex(plex_series, sonarr_season.seasonNumber)
                        if plex_season == None:
                            # Check if we're waiting for a new season to be released
                            if sonarr_series.nextAiring is not None and sonarr_series.nextAiring.date() > datetime.today().date()  and sonarr_season.sizeOnDisk == 0 and sonarr_season.monitored == True:
                                #changes_made.append(setLabel(plex_series, RETURNING))
                                # changes_made.append(setLabel(plex_series, f'RETURNING_{sonarr_series.nextAiring.strftime("%Y-%m-%d")}'))
                                changes_made.append(syncLabels(plex_series, [f'RETURNING_{sonarr_series.nextAiring.strftime("%Y-%m-%d")}'], ['RETURNING_%', 'ENDED', 'CONTINUING', 'CANCELED']))
                                complete_series = sonarr_series.percentOfEpisodes == 100
                                season_labels.append(RETURNING)
                            else: 
                                complete_series = False
                                logger.debug(sonarr_series.title + ' Season ' + str(sonarr_season.seasonNumber) + ' not found in Plex. Skipping this season')
                                changes_made.append(syncLabels(plex_season, [INCOMPLETE], [COMPLETE, INPROGRESS,'RETURNING_%']))
                                season_labels.append('INCOMPLETE')
                        else:
                            if getPercentOfEpisodes(sonarr_season, sonarr_series) == 100.0:
                                logger.debug('Episode percentage is 100')
                                if sonarr_season.episodeFileCount < sonarr_season.totalEpisodeCount:
                                    if sonarr_series.ended == False:
                                        logger.debug('episodeFileCount: ' + str(sonarr_season.episodeFileCount) + ' < totalEpisodeCount: ' + str(sonarr_season.totalEpisodeCount))
                                        # changes_made.append(setLabel(plex_season, INPROGRESS))
                                        changes_made.append(syncLabels(plex_season, [INPROGRESS], [COMPLETE, INCOMPLETE]))
                                        season_labels.append(INPROGRESS)
                                    else:
                                        
                                        # changes_made.append(setLabel(plex_season, INCOMPLETE))
                                        changes_made.append(syncLabels(plex_season, [INCOMPLETE], [COMPLETE, INCOMPLETE]))
                                        season_labels.append(INCOMPLETE)
                                else:
                                    # changes_made.append(setLabel(plex_season, COMPLETE))
                                    changes_made.append(syncLabels(plex_season, [COMPLETE], [INCOMPLETE, INPROGRESS]))
                                    season_labels.append(COMPLETE)
                                
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
                                        if missing_episodes > 0 and episodes_not_aired == 0:
                                            # changes_made.append(setLabel(plex_season, INCOMPLETE))
                                            changes_made.append(syncLabels(plex_season, [INCOMPLETE], [COMPLETE, INCOMPLETE]))
                                            season_labels.append(INCOMPLETE)
                                        else:
                                            # When there are more episodes missing than those that should still be aired then the season is missing old episodes
                                            changes_made.append(setLabel(plex_season, INPROGRESS))
                                            season_labels.append(INPROGRESS)
                                    else:
                                        logger.debug('Series has ended')
                                        # The show has ended so it's missing past episodes
                                        # changes_made.append(setLabel(plex_season, INCOMPLETE))
                                        changes_made.append(syncLabels(plex_season, [INCOMPLETE], [COMPLETE, INCOMPLETE]))
                                        season_labels.append(INCOMPLETE)
                                else:
                                    logger.debug('This is not the latest season')
                                    # We're missing episodes from an older season so we need to flag it as INCOMPLETE
                                    # changes_made.append(setLabel(plex_season, INCOMPLETE))
                                    changes_made.append(syncLabels(plex_season, [INCOMPLETE], [COMPLETE, INCOMPLETE]))
                                    season_labels.append(INCOMPLETE)

                    logger.debug('Season labels are: ' + ', '.join(season_labels))
                    
                if len(season_labels) > 0:              
                    # When any season was flagged as INCOMPLETE then we label the entire Show as INCOMPLETE
                    if contains(season_labels, INCOMPLETE):
                        logger.debug('Season labels contains INCOMPLETE')
                        logger.debug('Setting Series label INCOMPLETE')
                        #changes_made.append(setLabel(plex_series, INCOMPLETE))
                        changes_made.append(syncLabels(plex_series, [INCOMPLETE], [COMPLETE, INPROGRESS, RETURNING]))
                    elif season_labels[-1] == INPROGRESS:
                        logger.debug('Last season label is INPROGRESS')
                        logger.debug('Setting Series label INPROGRESS')
                        # When no season was flagged as INCOMPLETE and the last season is INPROGRESS then the Show is INPROGRESS
                        #changes_made.append(setLabel(plex_series, INPROGRESS))
                        changes_made.append(syncLabels(plex_series, [INPROGRESS], [COMPLETE, INCOMPLETE, RETURNING]))
                    else:
                        logger.debug('Season labels do not contain INCOMPLETE and last season is not INPROGRESS')
                        logger.debug('Setting Series label COMPLETE')
                        # When no season was flagged as INCOMPLETE and the last season is not INPROGRESS then the Show is COMPLETE
                        #changes_made.append(setLabel(plex_series, COMPLETE))
                        changes_made.append(syncLabels(plex_series, [COMPLETE], [RETURNING, INCOMPLETE, INPROGRESS]))

                    if season_labels[-1] == RETURNING:
                        logger.debug('Last season label is RETURNING')
                        logger.debug('Setting Series label RETURNING')
                        # When no season was flagged as INCOMPLETE and the last season is INPROGRESS then the Show is INPROGRESS
                        #changes_made.append(setLabel(plex_series, INPROGRESS))
                        changes_made.append(syncLabels(plex_series, [RETURNING], []))
                
                # set show status
                logger.debug(f'Set status to {sonarr_series.status}')

                # obj = next((obj for obj in plex_series.labels if 'sonarr_status_' in str(obj.tag).lower()), None)
                
                # if(obj is not None):
                #     if str(obj.tag).lower() == sonarr_status_tag.lower():
                #         logger.debug(f'Status is already set to {sonarr_series.status}')
                #         continue
                
                # plex_series.addLabel(sonarr_status_tag)
                monitored = 'unmonitored'
                if sonarr_series.monitored:
                    monitored = 'monitored'

                number_of_episodes = sum(i.episodeFileCount for i in sonarr_series.seasons if i.seasonNumber > 0) 
                total_episodes = sum(i.totalEpisodeCount for i in sonarr_series.seasons if i.seasonNumber > 0)
                syncLabels(plex_series, [f'sonarr_{monitored}'], [f'sonarr_unmonitored', 'sonarr_monitored'])
                syncLabels(plex_series, [f'sonarr_network_{sonarr_series.network}'], ['sonarr_network_%'])
                syncLabels(plex_series, [f'sonarr_number_of_episodes_{str(number_of_episodes)} / {str(total_episodes)}'], ['sonarr_number_of_episodes_%'])
                syncLabels(plex_series, [f'sonarr_percent_{int((number_of_episodes / total_episodes) * 100)}'], ['sonarr_percent_%'])
                syncLabels(plex_series, [f'sonarr_bar_width_{int((number_of_episodes / total_episodes) * 1000)}'], ['sonarr_bar_width_%'])

                # plex_series.addLabel(f'sonarr_monitored_{monitored}')
                # if plex_series.network is None:
                #     plex_series.network = sonarr_series.network

                if True in changes_made:
                    logger.info('Changes were made so refresh the series...')
                    plex_series.refresh()

if __name__ == "__main__":
    main()

logger.info('Done')

