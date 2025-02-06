import math
from math import cos, sin, atan2, radians, degrees, asin
from numpy import sin, cos, arcsin, radians, sqrt
import folium
import warnings
import pyproj

# Ignorer les avertissements FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

lambert93 = pyproj.CRS("EPSG:2154")  # Lambert 93
wgs84 = pyproj.CRS("EPSG:4326")  # WGS84 (GPS)

# Créer un transformateur entre les systèmes de projection
transformer = pyproj.Transformer.from_crs(lambert93, wgs84, always_xy=True)


def lambert93_to_wgs84(x, y):
    lon, lat = transformer.transform(x, y)
    return lon, lat

def calculate_bearing(lat1, lng1, lat2, lng2):
    """
    A function to calculate azimuth
    """
 
    start_lat = math.radians(lat1)
    start_long = math.radians(lng1)
    end_lat = math.radians(lat2)
    end_long = math.radians(lng2)
    d_long = end_long - start_long
    d_phi = math.log(math.tan(end_lat / 2.0 + math.pi / 4.0) / math.tan(start_lat / 2.0 + math.pi / 4.0))
    if abs(d_long) > math.pi:
        if d_long > 0.0:
            d_long = -(2.0 * math.pi - d_long)
        else:
            d_long = (2.0 * math.pi + d_long)
    bearing = (math.degrees(math.atan2(d_long, d_phi)) + 360.0) % 360.0
 
    return bearing


def get_destination_lat_long(lat, lng, azimuth, distance):
    """
    A function to calculate coordinates
    """
 
    # azimuth, lat, lng: array of 1 element ==> we use .iloc[-1] to get this element
 
    radius = 6373 #Radius of the Earth in km
    brng = radians(azimuth) #Bearing is degrees converted to radians.
    dist = (distance)/1000 #Distance m converted to km
 
    lat1 = radians(lat) #Current dd lat point converted to radians
    lon1 = radians(lng) #Current dd long point converted to radians
 
    lat2 = asin(sin(lat1) * cos(dist/radius) + cos(lat1)* sin(dist/radius)* cos(brng))
 
    lon2 = lon1 + atan2(sin(brng) * sin(dist/radius)* cos(lat1), cos(dist/radius)- sin(lat1)* sin(lat2))
 
    #convert back to degrees
    lat2 = degrees(lat2)
    lon2 = degrees(lon2)
 
    return[lat2, lon2]

 
def approx_flying_distance_in_m(ref_latitude, ref_longitude, points_latitude, points_longitude):
    """
    https://en.wikipedia.org/wiki/Great-circle_distance
 
    :param ref_latitude:
    :param ref_longitude:
    :param points_latitude:
    :param points_longitude:
 
    :return:
 
    """
    # earth radius
    radius = 6373.0
 
    ref_lat = radians(ref_latitude)
    points_lat = radians(points_latitude)
    dlat = points_lat - ref_lat
 
    ref_lon = radians(ref_longitude)
    points_lon = radians(points_longitude)
    dlon = points_lon - ref_lon
 
    def haversine(theta):
        return sin(theta / 2) ** 2
 
    central_angle = 2 * arcsin(sqrt(haversine(dlat) + cos(ref_lat) * cos(points_lat) * haversine(dlon)))
 
    return radius * central_angle * 1000

def afficher_carte(df_maps,df_defaut_final):
    m = folium.Map(location=[df_maps["latitude"].mean(), df_maps["longitude"].mean()], zoom_start=13)
    markers = folium.FeatureGroup(name="Markers")
    for _, row in df_maps.iterrows():
    # Ajouter un point à la localisation
        markers.add_child(
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=3,  # Taille du point
            color="black",  # Couleur du contour
            fill=True,
            fill_color="black",  # Couleur du point
            fill_opacity=0.7
        ),
        folium.Marker(
                location=[row["latitude"], row["longitude"]],
                icon=folium.DivIcon(
                    icon_size=(150, 36),
                    icon_anchor=(7, 7),
                    html=f'<div style="font-size: 14px; color: blue; font-weight: bold;">{str(row["Regard amont"])}</div>'
                )
            )
    )

    for _, row in df_defaut_final.iterrows():
        marker_icon = get_marker_icon(row["Defaut"],row["Gravite"])
        
        # Ajouter un marqueur avec l'icône personnalisée
        markers.add_child(
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                icon=marker_icon,
                popup=row["Defaut"] 
            )
        )
    # Ajouter la FeatureGroup à la carte
    m.add_child(markers)

    # Ajouter une polyligne reliant les points
    coordinates = list(zip(df_maps['latitude'], df_maps['longitude']))
    folium.PolyLine(
        locations=coordinates,
        color='blue',
        weight=3,
        opacity=0.7
    ).add_to(m)
    
    return m

def get_color(gravity):
    if gravity == 3:
        return "red"
    elif gravity == 2:
        return "orange"
    elif gravity == 1:
        return "green"
    else:
        return "blue"


def get_marker_icon(defaut,gravite):
    couleur = get_color(gravite)
    if defaut.lower() == "racine":
        return folium.Icon(icon="seedling", prefix="fa", color=couleur)  # Icône d'arbre (feuille)
    elif defaut.lower() == "intrusion":
        return folium.Icon(icon="tint", prefix="fa", color=couleur)  # Icône d'alerte
    elif defaut.lower() == "fissure":
        return folium.Icon(icon="bolt-lightning", prefix="fa", color=couleur)  # Icône de fissure (ou une autre icône)
    elif defaut.lower() == "infiltration":
        return folium.Icon(icon="water",icon_color="blue", prefix="fa", color=couleur)  # Icône de fissure (ou une autre icône)
    elif defaut.lower() == "depot":
        return folium.Icon(icon="angles-down", prefix="fa", color=couleur)  # Icône de fissure (ou une autre icône)
    elif defaut.lower() == "concretion":
        return folium.Icon(icon="location-pin-lock", prefix="fa", color=couleur)  # Icône de fissure (ou une autre icône)
    else:
        return folium.Icon(icon="circle-info", prefix="fa", color=couleur)  # Icône de fissure (ou une autre icône)