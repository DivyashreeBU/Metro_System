from app import app
from models import db, MetroLine, Station

metro_data = {
    "Purple Line": {
        "stations": [
            "Challaghatta", "Kengeri", "Mysuru Road", "Vijayanagar", "Hosahalli",
            "Magadi Road", "Majestic", "Cubbon Park", "MG Road", "Trinity",
            "Indiranagar", "Baiyappanahalli", "KR Puram", "Whitefield"
        ],
        "color": "purple"
    },
    "Green Line": {
        "stations": [
            "Nagasandra", "Peenya", "Yeshwanthpur", "Rajajinagar", "Mantri Square Sampige Road",
            "Majestic", "Chickpete", "KR Market", "National College", "South End Circle",
            "Jayanagar", "Banashankari", "Yelachenahalli", "Silk Institute"
        ],
        "color": "green"
    },
    "Yellow Line": {
        "stations": [
            "RV Road", "Ragigudda", "Jayadeva Hospital", "BTM Layout",
            "HSR Layout", "Central Silk Board", "Bommasandra"
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

        line = MetroLine(name=line_name, color=line_info["color"])
        db.session.add(line)
        db.session.flush()  # Get line.id before committing

        for station_name in line_info["stations"]:
            is_interchange = station_name in metro_data["Interchanges"]
            station = Station(name=station_name, line_id=line.id, is_interchange=is_interchange)
            db.session.add(station)

    db.session.commit()
    print("✅ Metro lines and stations seeded successfully.")