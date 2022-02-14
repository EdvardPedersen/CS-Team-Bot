# CS-Team-Bot
Discord bot for Counter-strike. 

# Interface
```
!register - start registration for next match(this week or next week default to wednesdays)
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
- The bot responds with a list of all maps, with a reaction to each map containing number 1-7
- User reacts with the appropriate rank for the map
- The bot ends with a question of which rank the user is

!teams
- The bot rolls teams for matches
- Teams are assigned a pool of maps they will play based on preferences
- Balanced by rank and map pool
- Ban order is decided
```
