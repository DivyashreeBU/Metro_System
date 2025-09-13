from app import app
from models import db, MetroLine, Station

# 🚇 Metro line and station data with zones
metro_data = {
    "Purple Line": {
        "stations": [
            ("Challaghatta", "5"), ("Kengeri", "5"), ("Mysuru Road", "4"), ("Vijayanagar", "4"),
            ("Hosahalli", "3"), ("Magadi Road", "3"), ("Majestic", "3"), ("Cubbon Park", "2"),
            ("MG Road", "2"), ("Trinity", "2"), ("Indiranagar", "2"), ("Baiyappanahalli", "1"),
            ("KR Puram", "1"), ("Whitefield", "1")
        ],
        "color": "purple"
    },
    "Green Line": {
        "stations": [
            ("Nagasandra", "1"), ("Peenya", "1"), ("Yeshwanthpur", "2"), ("Rajajinagar", "2"),
            ("Mantri Square Sampige Road", "2"), ("Majestic", "3"), ("Chickpete", "3"),
            ("KR Market", "3"), ("National College", "3"), ("South End Circle", "4"),
            ("Jayanagar", "4"), ("Banashankari", "4"), ("Yelachenahalli", "5"), ("Silk Institute", "5")
        ],
        "color": "green"
    },
    "Yellow Line": {
        "stations": [
            ("RV Road", "4"), ("Ragigudda", "4"), ("Jayadeva Hospital", "4"), ("BTM Layout", "4"),
            ("HSR Layout", "5"), ("Central Silk Board", "5"), ("Bommasandra", "5")
        ],
        "color": "yellow"
    },
    "Interchanges": {
        "Majestic": ["Purple Line", "Green Line"],
        "Jayadeva Hospital": ["Yellow Line"]
    }
}

with app.app_context():
    for line_name, line_info in metro_data.items():
        if line_name == "Interchanges":
            continue

        # 🎨 Create MetroLine
        line = MetroLine(name=line_name, color=line_info["color"])
        db.session.add(line)
        db.session.flush()  # Get line.id before committing

        # 🚉 Create Stations
        for station_name, zone in line_info["stations"]:
            is_interchange = station_name in metro_data["Interchanges"]
            station = Station(
                name=station_name,
                zone=zone,
                line_id=line.id,
                is_interchange=is_interchange
            )
            db.session.add(station)

    db.session.commit()
    print("✅ Metro lines and stations seeded successfully.")