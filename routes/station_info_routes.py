from flask import Blueprint, render_template, request

station_bp = Blueprint('station_bp', __name__)

metro_lines = {
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
            "Nagasandra", "Peenya", "Yeshwanthpur", "Rajajinagar",
            "Mantri Square Sampige Road", "Majestic", "Chickpete", "KR Market",
            "National College", "South End Circle", "Jayanagar", "Banashankari",
            "Yelachenahalli", "Silk Institute"
        ],
        "color": "green"
    },
    "Yellow Line": {
        "stations": [
            "RV Road", "Ragigudda", "Jayadeva Hospital", "BTM Layout",
            "HSR Layout", "Central Silk Board", "Bommasandra"
        ],
        "color": "gold"
    },
    "Interchanges": {
        "Majestic": ["Purple Line", "Green Line"],
        "Jayadeva Hospital": ["Yellow Line"]
    }
}

# Flatten station list
all_stations = sorted(set(
    station for line, data in metro_lines.items() if line != "Interchanges"
    for station in data["stations"]
))

@station_bp.route('/station-info', methods=['GET', 'POST'])
def station_info():
    if request.method == 'POST':
        query = request.form['station_query']
        found_lines = []
        nearby_stations = []
        interchange_lines = metro_lines["Interchanges"].get(query, [])

        for line, data in metro_lines.items():
            if line != "Interchanges" and query in data["stations"]:
                found_lines.append({"name": line, "color": data["color"]})
                idx = data["stations"].index(query)
                nearby_stations = data["stations"][max(0, idx-2):idx] + data["stations"][idx+1:idx+3]

        return render_template(
            'station_info.html',
            station=query,
            lines=found_lines,
            nearby=nearby_stations,
            interchange=interchange_lines,
            all_stations=all_stations
        )

    return render_template('station_info.html', all_stations=all_stations)
    