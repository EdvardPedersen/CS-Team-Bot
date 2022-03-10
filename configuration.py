import json


class Configuration():
    def __init__(self,config_file="config"):
        self.config_file = config_file
        self.owner = None
        self.server = None
        self.team_role = None
        self.broadcast_channel = None
        self.guild = ""
        self.role = ""
        self.team_role = None
        self.setup()


    def _setupCfgTerminal(self):
        try:
            owner = int(input("OwnerID: "))
            team_role = None
            while not team_role:
                team_role = int(input("Team role ID: "))
            broadcast_channel = input("Name of broadcast channel: ")
            server_id = int(input("Server ID: "))
            cfg = {
                "ownerID":owner,
                "team role ID":team_role,
                "broadcast channel":broadcast_channel,
                "server ID":server_id
            }
            with open(self.config_file,"w") as f:
                json.dump(cfg,f)
        except Exception as e:
            print(e)
            print(type(e))
            exit()
    
    def setup(self):
        config = {}
        loaded = False
        while(not loaded):
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                    self.owner = config["ownerID"]
                    self.team_role = config["team role ID"]
                    self.broadcast_channel = config["broadcast channel"]
                    self.server = config["server ID"]
                    loaded = True
            except FileNotFoundError as ferr:
                print(ferr)
                if input("Would you like to setup the config from the terminal? y/n ") == 'y':
                    self._setupCfgTerminal()
                else:
                    exit(f"Please setup your config: {self.config_file}")
            except json.decoder.JSONDecodeError as derr:
                print(derr)
                if input("Would you like to setup the config from the terminal? y/n ") == 'y':
                    self._setupCfgTerminal()
                else:
                    exit(f"Please setup your config: {self.config_file}")
            except KeyError as kerr:
                print(kerr)
                if input("Would you like to setup the config from the terminal? y/n ") == 'y':
                    self._setupCfgTerminal()
                else:
                    exit(f"Please setup your config: {self.config_file}")
            except Exception as e:
                print(e)
                print(type(e))
                exit()
