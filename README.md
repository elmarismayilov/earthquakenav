# EarthquakeNav 🌍📍

**EarthquakeNav** is an app that detects nearby earthquakes and helps users navigate to the safest evacuation spots using real-time data and intelligent scoring.


## 📌 Motivation

I built this app with two clear goals in mind:

1. To create something **meaningful and practical** that could assist people in emergencies.
2. To **leverage computer science and mathematics**—especially geospatial algorithms—to help save lives.

While modern smartphones often notify users when earthquakes occur, they don’t help answer a critical question:  
**"Where should I go right now to stay safe?"**

**EarthquakeNav** answers that question by combining earthquake detection, place search, and smart safety evaluation.


## ⚙️ Features, Technologies, and Architecture

### 🔧 Technologies Used
- **Python**
- **Django** (for web interface)
- **USGS Earthquake API** (to detect seismic activity)
- **OpenStreetMap Overpass API** (to find evacuation places)
- **IPInfo API** (for user geolocation)

### 🧠 How It Works

1. **Determine User Location**  
   Uses IP geolocation (via ipinfo.io) to get the user's approximate location.

2. **Fetch Earthquake Data**  
   Queries the [USGS Earthquake API](https://earthquake.usgs.gov/) to find recent earthquakes within a 100 km radius. Selects the strongest one (by magnitude).

3. **Find Evacuation Candidates**  
   Uses [OpenStreetMap’s Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) to search for nearby:
   - 🏞 Parks  
   - 🏫 Schools  
   - 🏥 Hospitals  
   - 🏟 Stadiums  
   - 🚒 Fire Stations  

4. **Calculate Safety Score**  
   For each candidate location, a **safety score** is calculated using a formula inspired by the **Gaussian distribution**:

   Safety Score = 1 - exp(-(distance_to_epicenter^2) / (2 * sigma^2))

   Where:  
   - sigma = magnitude x 5
   - Higher score = safer location  
   - Closer to 1 → safer | Closer to 0 → riskier

5. **Zone Classification**  
   Locations are grouped into 3 zones:
   - 🟢 **Green Zone** — safest  
   - 🟡 **Yellow Zone** — moderate risk  
   - 🔴 **Red Zone** — close to epicenter  

6. **Smart Sorting**  
   Within each zone, locations are sorted by proximity to the user — prioritizing safe **and** nearby options.

7. **Navigation**  
   When a user selects a location, the app opens **Google Maps** with directions from the user’s current location to that evacuation spot.


## 🚀 Future Work / Improvements

This is the first version, and there are many ways to grow:

- 🧠 Improve the safety algorithm with real-time seismic modeling or AI
- 🗺 Avoid risk-prone areas even within safe zones (e.g. poor infrastructure zones)
- 📍 Allow manual user location entry (for better precision or fallback)
- ⚙️ Let users filter results by type or distance
- 🔔 Add real-time alerts and push notifications
- 🌐 Support more regions, multiple languages, and offline caching

All updates and improvements will be shared on the [https://github.com/elmarismayilov/earthquakenav].


## 🤝 Contact

I'm open to collaborations, feedback, and contributions!

- GitHub: [https://github.com/elmarismayilov/earthquakenav](#)
- LinkedIn: [www.linkedin.com/in/elmar-ismayilov](https://www.linkedin.com/in/elmar-ismayilov)
