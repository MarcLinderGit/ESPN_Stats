import urllib.request
import re

class NFLTeamLinks:
    def __init__(self):
        self.espn_teams_url = 'https://www.espn.com/nfl/teams'
        self.team_urls = {}

    def build_team_urls(self):
        with urllib.request.urlopen(self.espn_teams_url) as f:
            teams_source = f.read().decode('utf-8')

        teams_data = re.findall(r"www\.espn\.com/nfl/team/_/name/(\w+)/(.+?)\",", teams_source)

        for team_id, team_name in teams_data:
            roster_url = f'https://www.espn.com/nfl/team/roster/_/name/{team_id}/{team_name}'
            self.team_urls[team_name] = roster_url

    def get_team_urls(self):
        return self.team_urls

# Create an instance of the NFLTeamData class
nfl_data = NFLTeamLinks()

# Build the team URLs
nfl_data.build_team_urls()

# Get the team URLs
rosters = nfl_data.get_team_urls()

# Print the team URLs
print(rosters)
