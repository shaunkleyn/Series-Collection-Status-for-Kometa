from arrapi import SonarrAPI
from plexapi.server import PlexServer
import re

# Plex
plex_url = 'http://127.0.0.1:32400'
plex_token = 'PLEX_TOKEN'

# Sonarr
sonarr_url = "http://127.0.0.1:8989/"
sonarr_api_key = "SONARR_API_KEY"

plex = PlexServer(plex_url, plex_token)
sonarr = SonarrAPI(sonarr_url, sonarr_api_key)

tvdb_id_to_process = None
section = "TV Shows"

plex_shows = plex.library.section(section).all()

for plex_series in plex_shows:
    tvdb = next((obj for obj in plex_series.guids if obj.id.startswith("tvdb")), None)

    match = re.search(r'\d+', tvdb.id)
    tvdb_id = int(match.group()) if match else 0

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
                                plex_season.addLabel('inprogress').removeLabel('complete').removeLabel('incomplete')
                                print('🔵' + plex_series.title + ' - Season ' + str(sonarr_season.seasonNumber))  

                                if complete_series == True:
                                    plex_series.addLabel('inprogress').removeLabel('complete').removeLabel('incomplete')
                                    print('🔵' + plex_series.title)  
                                    complete_season = None
                                    break
                            else:
                                plex_season.addLabel('incomplete').removeLabel('complete').removeLabel('inprogress')
                                print('🔴' + plex_series.title + ' - Season ' + str(sonarr_season.seasonNumber)) 
                                complete_series = False
                        else:
                            complete_season = True
                            plex_season.addLabel('complete').removeLabel('incomplete').removeLabel('inprogress')
                            print('🟢' + plex_series.title + ' - Season ' + str(sonarr_season.seasonNumber))  

                    else:
                        if complete_season:
                            plex_season.addLabel('complete').removeLabel('incomplete').removeLabel('inprogress')
                            print('🟢' + plex_series.title + ' - Season ' + str(sonarr_season.seasonNumber))  
                        else:
                            plex_season.addLabel('incomplete').removeLabel('complete').removeLabel('inprogress')
                            print('🔴' + plex_series.title + ' - Season ' + str(sonarr_season.seasonNumber))  
                            complete_series = False
                else:
                    complete_series = False

        if complete_season is not None:
            if complete_series == True:
                plex_series.addLabel('complete').removeLabel('incomplete').removeLabel('inprogress')
                print('🟢' + plex_series.title)  
            else:
                plex_series.addLabel('incomplete').removeLabel('complete').removeLabel('inprogress')
                print('🔴' + plex_series.title)  

print('Done')

