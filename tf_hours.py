import requests
import threading
from tf_utils import sorter


#'API_KEY'
BACKPACK_API = "64cbfeaba5a1140fa30534d5"
API_KEY = '31475B06B733BC05DE0DB5BCFD3FECE0'

steam_id_file = sorter("tf2.txt")


def minutes_to_hours(minutes):
    hours = minutes / 60
    formatted_output = "{:.3f}".format(hours)
    return formatted_output

def fetch_data(steam_id_string, playerXtime):
    # Construct the API endpoint URL to get player summaries
    profile_url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_KEY}&steamids={steam_id_string}&format=json'

    # Make an HTTP GET request to the API to get profile information
    profile_response = requests.get(profile_url)

    if profile_response.status_code == 200:
        profile_data = profile_response.json()

        if 'response' in profile_data and 'players' in profile_data['response']:
            players_list = profile_data['response']['players']
            if players_list:
                player = players_list[0]  # Assuming only one player is returned
                display_name = player.get('personaname', 'Unknown')  # Get the display name
            else:
                print('No player data found for the provided Steam Community ID.')
                return
        else:
            print('Error retrieving profile data.')
            return
    else:
        print('Profile API request failed.')
        return

    # Set include_played_free_games parameter
    include_played_free_games = 1  # Set to 1 to include played free games

    # Construct the API endpoint URL with the new parameter
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={steam_id_string}&format=json&include_played_free_games={include_played_free_games}'

    # Make an HTTP GET request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        if 'response' in data and 'games' in data['response']:
            games = data['response']['games']

            total_playtime = 0

            for game in games:
                if game['appid'] == 440:
                    total_playtime += game.get('playtime_forever', 0)  # minutes
                    total_playtime_hours = minutes_to_hours(total_playtime)
                    if float(total_playtime_hours) < 800:
                        link = f"https://backpack.tf/profiles/{steam_id_string}"
                        playerXtime[steam_id_string] = {'hours': total_playtime_hours, 'link': link, 'player_name':display_name}
        else:
            print('Error retrieving playtime data.')
    else:
        print('API request failed.')


def scanner(STEAM_IDS):
    playerXtime = {}
    threads = []

    for steamid in STEAM_IDS:
        steam_id_string = str(steamid)
        thread = threading.Thread(target=fetch_data, args=(steam_id_string, playerXtime))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    players = dict(sorted(playerXtime.items(), key=lambda item: float(item[1]['hours'].split()[0])))
    return players



a = scanner(steam_id_file)
print(a)