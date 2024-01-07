import yaml
import array
from arrapi import SonarrAPI
from plexapi.server import PlexServer, NotFound
import re
from datetime import datetime, date, timedelta



bar_height = 0
complete_background = '#37A03A' #'#006718' #'#e5a00d' # #
incomplete_background =  '#0000009D' #'#851010' #'#e5a00d' #
airing_background = '#2273C6' #'#005086' # '#e5a00d' #
progress_text_color = '#ffffff' #'#ffffff' # #000000'
border_width = 20
border_padding = 0
border_radius = 40
text_align = 'right'
new_icon_top_padding = 150
show_monitored_icon = False
show_episode_count = False

status_colors = {
    'complete' : '#37A03A',
    'incomplete' : '#CA7C29',
    'airing' : '#2273C6'
}

data = {
    'templates' : {
        'poster_border_rounded' : {
            'overlay' : {
                'name' : 'backdrop',
                'back_color' : '#2A2A2A00',
                'back_width' : 1000 - (border_padding * 2),
                'back_height' : 1500 - (border_padding * 2),
                'back_line_color' : '<<border_color>>',
                'back_line_width' : border_width,
                'horizontal_align' : 'left',
                'horizontal_offset' : border_padding,
                'vertical_align' : 'top',
                'vertical_offset' : border_padding,
                'back_radius' : border_radius,
                'weight' : 500,
                'group' : 'rounded_border'
            },
            'tvdb_show' : '<<tvdb_show>>',
            'imdb_id' : '<<imdb_id>>'
        },
        'poster_border' : {
            'overlay' : {
                'name' : 'backdrop',
                'back_color' : '#2A2A2A00',
                'back_width' : 1000,
                'back_height' : 1500,
                'back_line_color' : '<<border_color>>',
                'back_line_width' : border_width,
                'horizontal_align' : 'left',
                'horizontal_offset' : 0,
                'vertical_align' : 'top',
                'vertical_offset' : 0,
                'back_radius' : 0,
                'weight' : 500,
                'group' : 'border'
            },
            'tvdb_show' : '<<tvdb_show>>',
            'imdb_id' : '<<imdb_id>>'
        },
        'progress_background' : {
            'overlay' : {
                'name' : 'backdrop',
                'back_color' : '#4E4E4EB3',
                'back_width' : 1000 - (border_padding * 2),
                'back_height' : bar_height,
                'horizontal_align' : 'left',
                'horizontal_offset' : border_padding,
                'vertical_align' : 'bottom',
                'vertical_offset' : border_padding,
                'back_radius' : border_radius,
                'weight' : 510,
                'group' : 'bg'
            },
            'plex_all' : True
        }, 
        'progress_bar' : {
            'default' : {
                'back_color' : complete_background
            },
            'overlay' : {
                'name' : 'backdrop',
                'back_color' : '<<back_color>>',
                'back_width' : '<<width>>',
                'back_height' : bar_height,
                'horizontal_align' : 'left',
                'horizontal_offset' : border_padding,
                'vertical_align' : 'bottom',
                'vertical_offset' : border_padding,
                'weight' : 210,
                'back_radius' : border_radius,
                'group' : 'border2'
            },
            'tvdb_show' : '<<tvdb_show>>',
            'imdb_id' : '<<imdb_id>>'
        },
        'progress_text' : {
            'default' : {
                'text' : '-'
            },
            'overlay' : {
                'name' : 'text(<<text>>)',
                'font_size' : 70,
                'back_align' : text_align,
                'font_color' : progress_text_color,
                'back_width' : 1000 - (border_padding * 2),
                'back_height' : max(bar_height, 120),
                'horizontal_align' : 'left',
                'vertical_align' : 'bottom',
                'horizontal_offset' : border_padding + 40,
                'vertical_offset' : border_padding,
                'stroke_width' : 5,
                'stroke_color' : '#00000045',
                'weight' : 320
                },
            'tvdb_show' : '<<tvdb_show>>',
            'imdb_id' : '<<imdb_id>>'
        },
      'new_status_shadow' : {
        'overlay': {
            'name': '<<image>>',
            'horizontal_align': 'left',
            'vertical_align': 'top',
            'horizontal_offset': 15,
            'vertical_offset': 15 + new_icon_top_padding,
            'weight': 330
            },
            'tvdb_show': '<<tvdb_show>>',
            'imdb_id': '<<imdb_id>>' 
    },
    'new_status' : {
        'overlay': {
            'name': '<<image>>',
            'horizontal_align': 'left',
            'vertical_align': 'top',
            'horizontal_offset': 10,
            'vertical_offset': 10 + new_icon_top_padding,
            'weight': 330
            },
            'tvdb_show': '<<tvdb_show>>',
            'imdb_id': '<<imdb_id>>' 
    },
    'monitored_status' : {
        'overlay': {
            'name': '<<image>>',
            'horizontal_align': 'left',
            'vertical_align': 'bottom',
            'horizontal_offset': 25,
            'vertical_offset': 0,
            'weight': 330
            },
            'tvdb_show': '<<tvdb_show>>',
            'imdb_id': '<<imdb_id>>' 
    }
    },
    'overlays' : {
        'progress_bg' : {
            'template' : [
                {'name' : 'progress_background'}
            ]
        }
    }
}

# Plex
plex_url = 'http://192.168.8.100:32400' #dict(data)['plex']['url'] #config['plex']['url']
plex_token = 'HyRBkXfvuvpVzE3299Xc' #dict(data)['plex']['token'] #config['plex']['token']
plex = PlexServer(plex_url, plex_token,timeout=120)

# Sonarr
sonarr_url = 'http://192.168.8.100:8989/' #dict(data)['sonarr']['url'] #config['sonarr']['url']
sonarr_api_key = 'd4f9ec92776f449d812c2a34c9f24091' #dict(data)['sonarr']['token'] #config['sonarr']['apikey']
sonarr = SonarrAPI(sonarr_url, sonarr_api_key)

def getTvdbId(series):
    tvdb = next((guid for guid in series.guids if guid.id.startswith("tvdb")), None)
    match = re.search(r'\d+', tvdb.id)
    
    return int(match.group()) if match else 0


# Returns True, if the given date is older than N Days
def is_within_N_days(dateAdded, N):
    # Create a date object for the current date
    today = date.today()
    # Create a date object from string format of date
    dateObj = dateAdded.date()
    # Create a date object for the date N days ago
    startDate = today - timedelta(days=N)
    # check if the given date is older than N days
    if dateObj > startDate:
        return True
    else:
        return False


plex_series_list = plex.library.section('Test-Shows').all()
# overlays = array.array( data['overlays'])
for plex_series in plex_series_list:
# Get the TvDB ID for the show
    try:
        tvdb_id = getTvdbId(plex_series)
    except:
        continue
    
    try:
        sonarr_series = sonarr.get_series(tvdb_id=tvdb_id)
    except:
        print(plex_series.title + ' not found on Sonarr')
    
    status = 'complete'
    
    if sonarr_series.percentOfEpisodes < 100:
        if sonarr_series.monitored:
            status = 'incomplete'
    else:
        if not sonarr_series.ended:
            status = 'airing'
    
    data['overlays'][f'{sonarr_series.titleSlug}_{sonarr_series.year}_border'] = {
        'template' : [ {
            'name' : 'poster_border',
            'border_color' : status_colors[status]
            }
        ],
        'tvdb_show' : tvdb_id,
        'imdb_id' : sonarr_series.imdbId
    }    
    data['overlays'][f'{sonarr_series.titleSlug}_{sonarr_series.year}__rounded_border'] = {
        'template' : [ {
            'name' : 'poster_border_rounded',
            'border_color' : status_colors[status]
            }
        ],
        'tvdb_show' : tvdb_id,
        'imdb_id' : sonarr_series.imdbId
    }
    
    data['overlays'][f'{sonarr_series.titleSlug}_{sonarr_series.year}'] = {
        'template' : [ {
            'name' : 'progress_bar',
            'width' : int((sonarr_series.percentOfEpisodes / 100) * 1000) - (border_padding * 2)
            }
        ],
        'tvdb_show' : tvdb_id,
        'imdb_id' : sonarr_series.imdbId
    }
    
    if sonarr_series.percentOfEpisodes < 100:
        if sonarr_series.monitored:
            data['overlays'][f'{sonarr_series.titleSlug}_{sonarr_series.year}']['template'][0]['back_color'] = incomplete_background
    else:
        if not sonarr_series.ended:
            data['overlays'][f'{sonarr_series.titleSlug}_{sonarr_series.year}']['template'][0]['back_color'] = airing_background
    
    
    if show_episode_count:
        data['overlays'][f'{sonarr_series.titleSlug}_{sonarr_series.year}_text'] = {
            'template' : [ {
                'name' : 'progress_text',
                'text' : f'{str(sonarr_series.episodeFileCount)} / {str(sonarr_series.episodeCount)}'
                }
            ],
            'tvdb_show' : tvdb_id,
            'imdb_id' : sonarr_series.imdbId
        }
    
    if show_monitored_icon:
        data['overlays'][f'{sonarr_series.titleSlug}_{sonarr_series.year}_monitored_status'] = {
            'template' : [ {
                'name' : 'monitored_status',
                'image' : f'{"not-" if not sonarr_series.monitored else ""}monitored'
                }
            ],
            'tvdb_show' : tvdb_id,
            'imdb_id' : sonarr_series.imdbId
        }
    
    if is_within_N_days(sonarr_series.added, 7):
        data['overlays'][f'{sonarr_series.titleSlug}_{sonarr_series.year}_new_status_shadow'] = {
            'template' : [ {
                'name' : 'new_status_shadow',
                'image' : 'new_icon_shadow'
                }
            ],
            'tvdb_show' : tvdb_id,
            'imdb_id' : sonarr_series.imdbId
        }
        data['overlays'][f'{sonarr_series.titleSlug}_{sonarr_series.year}_new_status'] = {
            'template' : [ {
                'name' : 'new_status',
                'image' : 'new_icon'
                }
            ],
            'tvdb_show' : tvdb_id,
            'imdb_id' : sonarr_series.imdbId
        }
        

#data['overlays'].append(data1)

yaml_output = yaml.dump(data, sort_keys=False) 

def write_yaml_to_file(py_obj,filename):
    with open(f'config/sonarr-info/overlays/{filename}.yml', 'w',) as f :
        yaml.dump(py_obj,f,sort_keys=False) 
    print('Written to file successfully')
    
write_yaml_to_file(data, 'output')

