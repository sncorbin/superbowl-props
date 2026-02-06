"""
NFL Teams Data
Contains all 32 NFL teams with their colors and logo URLs
"""

NFL_TEAMS = {
    # AFC East
    "BUF": {
        "code": "BUF",
        "city": "Buffalo",
        "name": "Bills",
        "full_name": "Buffalo Bills",
        "conference": "AFC",
        "division": "East",
        "primary_color": "#00338D",
        "secondary_color": "#C60C30",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/buf.png"
    },
    "MIA": {
        "code": "MIA",
        "city": "Miami",
        "name": "Dolphins",
        "full_name": "Miami Dolphins",
        "conference": "AFC",
        "division": "East",
        "primary_color": "#008E97",
        "secondary_color": "#FC4C02",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/mia.png"
    },
    "NE": {
        "code": "NE",
        "city": "New England",
        "name": "Patriots",
        "full_name": "New England Patriots",
        "conference": "AFC",
        "division": "East",
        "primary_color": "#002244",
        "secondary_color": "#C60C30",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/ne.png"
    },
    "NYJ": {
        "code": "NYJ",
        "city": "New York",
        "name": "Jets",
        "full_name": "New York Jets",
        "conference": "AFC",
        "division": "East",
        "primary_color": "#125740",
        "secondary_color": "#FFFFFF",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png"
    },
    # AFC North
    "BAL": {
        "code": "BAL",
        "city": "Baltimore",
        "name": "Ravens",
        "full_name": "Baltimore Ravens",
        "conference": "AFC",
        "division": "North",
        "primary_color": "#241773",
        "secondary_color": "#9E7C0C",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/bal.png"
    },
    "CIN": {
        "code": "CIN",
        "city": "Cincinnati",
        "name": "Bengals",
        "full_name": "Cincinnati Bengals",
        "conference": "AFC",
        "division": "North",
        "primary_color": "#FB4F14",
        "secondary_color": "#000000",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/cin.png"
    },
    "CLE": {
        "code": "CLE",
        "city": "Cleveland",
        "name": "Browns",
        "full_name": "Cleveland Browns",
        "conference": "AFC",
        "division": "North",
        "primary_color": "#311D00",
        "secondary_color": "#FF3C00",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/cle.png"
    },
    "PIT": {
        "code": "PIT",
        "city": "Pittsburgh",
        "name": "Steelers",
        "full_name": "Pittsburgh Steelers",
        "conference": "AFC",
        "division": "North",
        "primary_color": "#FFB612",
        "secondary_color": "#101820",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/pit.png"
    },
    # AFC South
    "HOU": {
        "code": "HOU",
        "city": "Houston",
        "name": "Texans",
        "full_name": "Houston Texans",
        "conference": "AFC",
        "division": "South",
        "primary_color": "#03202F",
        "secondary_color": "#A71930",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/hou.png"
    },
    "IND": {
        "code": "IND",
        "city": "Indianapolis",
        "name": "Colts",
        "full_name": "Indianapolis Colts",
        "conference": "AFC",
        "division": "South",
        "primary_color": "#002C5F",
        "secondary_color": "#A2AAAD",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/ind.png"
    },
    "JAX": {
        "code": "JAX",
        "city": "Jacksonville",
        "name": "Jaguars",
        "full_name": "Jacksonville Jaguars",
        "conference": "AFC",
        "division": "South",
        "primary_color": "#006778",
        "secondary_color": "#D7A22A",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/jax.png"
    },
    "TEN": {
        "code": "TEN",
        "city": "Tennessee",
        "name": "Titans",
        "full_name": "Tennessee Titans",
        "conference": "AFC",
        "division": "South",
        "primary_color": "#0C2340",
        "secondary_color": "#4B92DB",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/ten.png"
    },
    # AFC West
    "DEN": {
        "code": "DEN",
        "city": "Denver",
        "name": "Broncos",
        "full_name": "Denver Broncos",
        "conference": "AFC",
        "division": "West",
        "primary_color": "#FB4F14",
        "secondary_color": "#002244",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/den.png"
    },
    "KC": {
        "code": "KC",
        "city": "Kansas City",
        "name": "Chiefs",
        "full_name": "Kansas City Chiefs",
        "conference": "AFC",
        "division": "West",
        "primary_color": "#E31837",
        "secondary_color": "#FFB81C",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png"
    },
    "LV": {
        "code": "LV",
        "city": "Las Vegas",
        "name": "Raiders",
        "full_name": "Las Vegas Raiders",
        "conference": "AFC",
        "division": "West",
        "primary_color": "#000000",
        "secondary_color": "#A5ACAF",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/lv.png"
    },
    "LAC": {
        "code": "LAC",
        "city": "Los Angeles",
        "name": "Chargers",
        "full_name": "Los Angeles Chargers",
        "conference": "AFC",
        "division": "West",
        "primary_color": "#0080C6",
        "secondary_color": "#FFC20E",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/lac.png"
    },
    # NFC East
    "DAL": {
        "code": "DAL",
        "city": "Dallas",
        "name": "Cowboys",
        "full_name": "Dallas Cowboys",
        "conference": "NFC",
        "division": "East",
        "primary_color": "#003594",
        "secondary_color": "#869397",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png"
    },
    "NYG": {
        "code": "NYG",
        "city": "New York",
        "name": "Giants",
        "full_name": "New York Giants",
        "conference": "NFC",
        "division": "East",
        "primary_color": "#0B2265",
        "secondary_color": "#A71930",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png"
    },
    "PHI": {
        "code": "PHI",
        "city": "Philadelphia",
        "name": "Eagles",
        "full_name": "Philadelphia Eagles",
        "conference": "NFC",
        "division": "East",
        "primary_color": "#004C54",
        "secondary_color": "#A5ACAF",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/phi.png"
    },
    "WAS": {
        "code": "WAS",
        "city": "Washington",
        "name": "Commanders",
        "full_name": "Washington Commanders",
        "conference": "NFC",
        "division": "East",
        "primary_color": "#5A1414",
        "secondary_color": "#FFB612",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/wsh.png"
    },
    # NFC North
    "CHI": {
        "code": "CHI",
        "city": "Chicago",
        "name": "Bears",
        "full_name": "Chicago Bears",
        "conference": "NFC",
        "division": "North",
        "primary_color": "#0B162A",
        "secondary_color": "#C83803",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/chi.png"
    },
    "DET": {
        "code": "DET",
        "city": "Detroit",
        "name": "Lions",
        "full_name": "Detroit Lions",
        "conference": "NFC",
        "division": "North",
        "primary_color": "#0076B6",
        "secondary_color": "#B0B7BC",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/det.png"
    },
    "GB": {
        "code": "GB",
        "city": "Green Bay",
        "name": "Packers",
        "full_name": "Green Bay Packers",
        "conference": "NFC",
        "division": "North",
        "primary_color": "#203731",
        "secondary_color": "#FFB612",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/gb.png"
    },
    "MIN": {
        "code": "MIN",
        "city": "Minnesota",
        "name": "Vikings",
        "full_name": "Minnesota Vikings",
        "conference": "NFC",
        "division": "North",
        "primary_color": "#4F2683",
        "secondary_color": "#FFC62F",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/min.png"
    },
    # NFC South
    "ATL": {
        "code": "ATL",
        "city": "Atlanta",
        "name": "Falcons",
        "full_name": "Atlanta Falcons",
        "conference": "NFC",
        "division": "South",
        "primary_color": "#A71930",
        "secondary_color": "#000000",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png"
    },
    "CAR": {
        "code": "CAR",
        "city": "Carolina",
        "name": "Panthers",
        "full_name": "Carolina Panthers",
        "conference": "NFC",
        "division": "South",
        "primary_color": "#0085CA",
        "secondary_color": "#101820",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/car.png"
    },
    "NO": {
        "code": "NO",
        "city": "New Orleans",
        "name": "Saints",
        "full_name": "New Orleans Saints",
        "conference": "NFC",
        "division": "South",
        "primary_color": "#D3BC8D",
        "secondary_color": "#101820",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/no.png"
    },
    "TB": {
        "code": "TB",
        "city": "Tampa Bay",
        "name": "Buccaneers",
        "full_name": "Tampa Bay Buccaneers",
        "conference": "NFC",
        "division": "South",
        "primary_color": "#D50A0A",
        "secondary_color": "#FF7900",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/tb.png"
    },
    # NFC West
    "ARI": {
        "code": "ARI",
        "city": "Arizona",
        "name": "Cardinals",
        "full_name": "Arizona Cardinals",
        "conference": "NFC",
        "division": "West",
        "primary_color": "#97233F",
        "secondary_color": "#000000",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/ari.png"
    },
    "LAR": {
        "code": "LAR",
        "city": "Los Angeles",
        "name": "Rams",
        "full_name": "Los Angeles Rams",
        "conference": "NFC",
        "division": "West",
        "primary_color": "#003594",
        "secondary_color": "#FFA300",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/lar.png"
    },
    "SF": {
        "code": "SF",
        "city": "San Francisco",
        "name": "49ers",
        "full_name": "San Francisco 49ers",
        "conference": "NFC",
        "division": "West",
        "primary_color": "#AA0000",
        "secondary_color": "#B3995D",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/sf.png"
    },
    "SEA": {
        "code": "SEA",
        "city": "Seattle",
        "name": "Seahawks",
        "full_name": "Seattle Seahawks",
        "conference": "NFC",
        "division": "West",
        "primary_color": "#002244",
        "secondary_color": "#69BE28",
        "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/sea.png"
    }
}

# Super Bowl venues - recent and upcoming
SUPER_BOWL_VENUES = {
    "LIX": {
        "number": "LIX",
        "year": 2025,
        "date": "2025-02-09",
        "venue": "Caesars Superdome",
        "city": "New Orleans",
        "state": "LA"
    },
    "LX": {
        "number": "LX",
        "year": 2026,
        "date": "2026-02-08",
        "venue": "Levi's Stadium",
        "city": "Santa Clara",
        "state": "CA"
    },
    "LXI": {
        "number": "LXI",
        "year": 2027,
        "date": "2027-02-14",
        "venue": "SoFi Stadium",
        "city": "Inglewood",
        "state": "CA"
    },
    "LXII": {
        "number": "LXII",
        "year": 2028,
        "date": "2028-02-13",
        "venue": "Mercedes-Benz Stadium",
        "city": "Atlanta",
        "state": "GA"
    }
}

def get_team(code):
    """Get team data by code"""
    return NFL_TEAMS.get(code.upper())

def get_all_teams():
    """Get all teams sorted by full name"""
    return sorted(NFL_TEAMS.values(), key=lambda x: x['full_name'])

def get_teams_by_conference(conference):
    """Get teams in a conference (AFC or NFC)"""
    return [t for t in NFL_TEAMS.values() if t['conference'] == conference]

def get_super_bowl_info(number):
    """Get Super Bowl venue info by number"""
    return SUPER_BOWL_VENUES.get(number.upper())
