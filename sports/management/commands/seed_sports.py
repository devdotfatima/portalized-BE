from django.core.management.base import BaseCommand
from sports.models import Sport, Position

class Command(BaseCommand):
    help = "Seeds the database with NCAA sports and their positions."

    def handle(self, *args, **kwargs):
        data = {
            "female": {
                "Basketball": ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"],
                "Volleyball": ["Outside Hitter", "Opposite Hitter", "Middle Blocker", "Setter", "Libero", "Defensive Specialist"],
                "Soccer": ["Goalkeeper", "Defender", "Midfielder", "Forward"],
                "Softball": ["Pitcher", "Catcher", "First Base", "Second Base", "Shortstop", "Third Base", "Outfield"],
                "Field Hockey": ["Goalkeeper", "Defender", "Midfielder", "Forward"],
                "Lacrosse": ["Goalkeeper", "Defender", "Midfielder", "Attacker"],
                "Gymnastics": ["Vault Specialist", "Uneven Bars Specialist", "Balance Beam Specialist", "Floor Exercise Specialist", "All-Around"],
                "Swimming and Diving": ["Freestyle", "Backstroke", "Breaststroke", "Butterfly", "Individual Medley", "Diver"],
                "Track and Field (Indoor and Outdoor)": ["Sprinter", "Middle Distance Runner", "Long Distance Runner", "Hurdler", "Jumper", "Thrower", "Multi-Event Athlete"],
                "Cross Country": [],
                "Tennis": ["Singles Player", "Doubles Player"],
                "Golf": [],
                "Ice Hockey": ["Goalie", "Defense", "Forward"],
                "Rowing": ["Rower", "Coxswain"],
                "Water Polo": ["Goalkeeper", "Center", "Driver", "Utility Player", "Winger"],
                "Rifle": ["Smallbore", "Air Rifle"],
            },
            "male": {
                "Basketball": ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"],
                "Football": ["Quarterback", "Running Back", "Wide Receiver", "Tight End", "Offensive Linemen",
                             "Defensive Linemen", "Linebacker", "Cornerback", "Safety",
                             "Kicker", "Punter", "Return Specialist", "Long Snapper"],
                "Baseball": ["Pitcher", "Catcher", "First Base", "Second Base", "Shortstop", "Third Base", "Outfield", "Designated Hitter"],
                "Soccer": ["Goalkeeper", "Defender", "Midfielder", "Forward"],
                "Ice Hockey": ["Goalie", "Defenseman", "Center", "Left Wing", "Right Wing"],
                "Lacrosse": ["Goalkeeper", "Defenseman", "Long Stick Midfielder", "Midfielder", "Attackman", "Faceoff Specialist"],
                "Wrestling": [],
                "Track and Field (Indoor and Outdoor)": ["Sprinter", "Middle Distance Runner", "Long Distance Runner", "Hurdler", "Jumper", "Thrower", "Multi-Event Athlete"],
                "Cross Country": [],
                "Swimming and Diving": ["Freestyle", "Backstroke", "Breaststroke", "Butterfly", "Individual Medley",
                                        "1m Springboard", "3m Springboard", "Platform"],
                "Golf": [],
                "Tennis": ["Singles Player", "Doubles Player"],
                "Volleyball": ["Outside Hitter", "Opposite Hitter", "Middle Blocker", "Setter", "Libero", "Defensive Specialist"],
                "Water Polo": ["Goalkeeper", "Center", "Driver", "Winger", "Point", "Utility Player"],
                "Fencing": ["Foil", "Épée", "Sabre"],
                "Rifle": ["Smallbore", "Air Rifle"],
                "Bowling": [],
                "Gymnastics": ["Floor Exercise", "Pommel Horse", "Still Rings", "Vault", "Parallel Bars", "Horizontal Bar", "All-Around"],
            }
        }

        created_sports = 0
        created_positions = 0

        for gender, sports in data.items():
            for sport_name, positions in sports.items():
                sport, sport_created = Sport.objects.get_or_create(name=sport_name, gender=gender)
                if sport_created:
                    self.stdout.write(self.style.SUCCESS(f"✓ Created Sport: {sport_name} ({gender})"))
                    created_sports += 1
                for position_name in positions:
                    position, pos_created = Position.objects.get_or_create(sport=sport, name=position_name)
                    if pos_created:
                        self.stdout.write(f"  └─ Added Position: {position_name}")
                        created_positions += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ Done! Created {created_sports} sports and {created_positions} positions."))