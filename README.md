# CS-Team-Bot
Discord bot for Counter-strike. 

# Interface
```
!register [number of maps]{2} - start registration for next match(this week or next week default to wednesdays)
- The bot gives a message that people react to to register
- Manual stop of registration


!cancel - cancel ongoing registration for next match
  - Remove registration completely, including registration post

!end - end ongoing registration, completing the process
  - Store next match state
  
!next - show information for next match registrated
  - The bot post a message to the broadcast channel

- After registration, registered users can PM bot to set map preferences with
!maps
- The bots prompts the user with a expected format for map order

!maps <[map,map1,map2...mapN]>
- The bot assigns scoring to the player's list of maps. If the list is incomplete, the bot will assign 0 values as default

!teams
- The bot rolls teams for matches
- Teams are assigned a pool of maps they will play based on preferences
- Balanced by rank and map pool
- Ban order is decided

!banorder
- The bot calculates a best shared banorder for all teams in the veto
- Give a list of maps and how high each team score for each map

!ban <map>
- Ban map from veto, with new best shared banorder

!unban <map>
- Unban map from veto, with new best shared banorder

!pick <map>
- Pick map in veto, with new best shared banorder

!unpick <map>
- Unpick map in veto, with new best shared banorder

```
