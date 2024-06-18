import re
import os 
import sys

BASE_DIR = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))

## converting this '[U:1:33834758]' to this 'STEAM_0:0:16917379'
def usteamid_to_steamid(usteamid):
  for ch in ['[', ']']:
    if ch in usteamid:
      usteamid = usteamid.replace(ch, '')
  
  usteamid_split = usteamid.split(':')
  steamid = []
  steamid.append('STEAM_0:')
  
  z = int(usteamid_split[2])
  
  if z % 2 == 0:
      steamid.append('0:')
  else:
      steamid.append('1:')

  steamacct = z // 2
  
  steamid.append(str(steamacct))
  
  return ''.join(steamid)

#################################################
### convert a 64bit CommunityID into a SteamID #### [U:1:1248212164] > 76561197960265728
#################################################


steamid64ident = 76561197960265728
def usteamid_to_commid(usteamid):

  for ch in ['[', ']']:
    if ch in usteamid:
      usteamid = usteamid.replace(ch, '')
  
  usteamid_split = usteamid.split(':')
  commid = int(usteamid_split[2]) + steamid64ident
  
  return commid




def sorter(player_info): ## sorting from status all the unique id's 
      pattern = r'\[U:.*?\]'

      matches = re.findall(pattern, player_info)
      bit_64_id = []
      for match in matches:
          # print(match) if want to see 64bitid 
          bit_64_id.append(usteamid_to_commid(match))
      return bit_64_id



def minutes_to_hours(minutes):
    hours = minutes / 60
    formatted_output = "{:.3f}".format(hours)
    return formatted_output