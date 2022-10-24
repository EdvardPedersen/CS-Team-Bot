# CS-Team-Bot
Discord bot for Counter-strike. 

# Setup
- Auth
  - Head over to: https://discord.com/developers/applications
  - Create a new application
  - Under 'Bot' add new bot
  - Take the token and paste it into a file('auth') in the same folder as bot.py

# Interface
```
!commands
- print list of available commands

!register [number of maps]{2}
  - start registration for next matchday
  - 2 matches default override with argument
  - wednesday default matchday, set with !playday
  - 20:00 default playtime, set with !playtime
  - The bot gives a message that people react to to register
  - Manual stop of registration


!cancel - cancel ongoing registration for next match
  - Remove registration completely, including registration post

!end - end ongoing registration, completing the process
  - Store next match state
  
!next - show information for next match registrated
  - The bot post a message to the broadcast channel

!maps [map,map1,map2...mapN]
- if no arg:
  - The bots prompts the user with a expected format for map order
- else:
  - The bot assigns scoring to the player's list of maps. If the list is incomplete, the bot will assign 0 values as default

!teams
  - if match:
    - return information for current rolled teams
  - else:
    - No match found

!banorder
- The bot calculates a best shared banorder for all teams in the veto
- Give a list of maps and how high each team score for each map

!ban <map>
- Ban map from veto, updates shared banorder

!unban <map>
- Unban map from veto, updates shared banorder

!pick <map>
- Pick map in veto, updates shared banorder

!unpick <map>
- Unpick map in veto, updates shared banorder

!dad
  - Post random dad-joke

!dank
  - Post dank-meme from youtube

!igl_add <name/ID>
  - Add given user to list of IGLs
  - Argument either discord name or discord ID

!igl_remove <name/ID>
  - Remove given user from list of IGLs
  - Argument either discord name or discord ID

!list_active_duty
  - List current active_duty
  - Manually maintaned in the repo
    - Found in constants.py

!list_players
  - List information about all players registered to the bot
    - rank and map-preference

!list_ranks
  - list all ranks with name and ID
    - ID used when setting ranks for players

!playday [day of week]
  - If no arg:
    - return current set playday
  - else:
    - set given day of week as playday

!playtime [xx:xx]
  - if no arg:
    - return current set playtime
  - else:
    - set given time as playtime

!player_info [name/ID]
  - if no arg:
    - return information for requesting player
  - else:
    - return information for given player[name/ID] if found
  - error:
    - Not found
    - Please register

!rank [1-18]
  - set your in-game rank




```
