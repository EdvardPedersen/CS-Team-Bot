class Configuration():
    def __init__(self,owner=None, admin=[], server=None, role=None):
        self.owner = None
        self.super_users_id = None
        self.server = None
        self.team_role = None
        self.parseParams(owner,admin,server,role)
        self.guild = ""
        self.role = ""

    def parseParams(self,owner,admin,server,role):
        self.owner = owner
        self.super_users_id = admin
        self.super_users_id.append(self.owner)
        self.server = server
        self.team_role = role
