# presenter.py

import csv
import os
import webbrowser
from tkinter import messagebox
import folium as folium
from model import *

class Presenter:
    def __init__(self, view):
        self.view = view
        self.bus_stops = self.load_bus_stops()  # Load bus stops from CSV file
        self.favorites = Favorites()

    def load_bus_stops(self):
        bus_stops = []
        with open('./data/stops.csv', 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                bus_stops.append({
                    "stop_code": row["stop_code"],
                    "stop_name": row["stop_name"],
                    "stop_lat": float(row["stop_lat"]),
                    "stop_lon": float(row["stop_lon"]),
                })
        return bus_stops

    @staticmethod
    def is_valid_coordinate(coordinate):
        try:
            float(coordinate)
            return True
        except ValueError:
            return False

    def fetch_and_display_route_summary(self):
        stop_no = self.view.get_stop_no()
        if not stop_no:
            messagebox.showerror('Error', 'Stop No. cannot be empty.')
            return
        self.view.clear_table()
        routes = fetch_oc_route_summary_for_stop_feed(stop_no)
        self.view.display_routes(routes)

    def fetch_and_display_next_trips(self):
        stop_no = self.view.get_stop_no()
        route_no = self.view.get_route_no()
        if not stop_no or not route_no:
            messagebox.showerror('Error', 'Stop No. and Route No. cannot be empty.')
            return
        self.view.clear_table()
        trips = fetch_next_trips(stop_no, route_no)
        self.view.display_trips(trips)

    def fetch_and_display_next_trips_all_routes(self):
        stop_no = self.view.get_stop_no()
        if not stop_no:
            messagebox.showerror('Error', 'Stop No. cannot be empty.')
            return
        self.view.clear_table()
        trips = fetch_next_trips_all_routes(stop_no)
        self.view.display_trips(trips)

    def show_on_map(self):
        trips = fetch_next_trips_all_routes(self.view.get_stop_no())

        # Filter out trips without coordinates and convert coordinates to float
        trips_with_coordinates = [
            trip for trip in trips
            if trip._longitude and trip._latitude and self.is_valid_coordinate(
                trip._longitude) and self.is_valid_coordinate(trip._latitude)
        ]

        if not trips_with_coordinates:
            messagebox.showinfo('Info', 'No trips with valid coordinates found.')
            return

        bus_stops = self.load_bus_stops()
        stop_no = self.view.get_stop_no()  # get stop number from entry field

        # Find the bus stop from the loaded list of bus stops
        bus_stop = next((bus_stop for bus_stop in bus_stops if bus_stop["stop_code"] == stop_no), None)
        if bus_stop is not None:
            bus_map = folium.Map(location=[float(bus_stop["stop_lat"]), float(bus_stop["stop_lon"])], zoom_start=13)

            folium.Marker(
                location=[float(bus_stop["stop_lat"]), float(bus_stop["stop_lon"])],
                popup=f"Stop: {bus_stop['stop_code']} - {bus_stop['stop_name']}",
                icon=folium.Icon(icon="flag", prefix="fa", color="green"),
            ).add_to(bus_map)

            # Add markers for trips with coordinates
            for trip in trips_with_coordinates:
                folium.Marker(
                    location=[float(trip._latitude), float(trip._longitude)],
                    popup=f"Bus: {trip._route_no}<br><br>Destination: {trip._route_heading}<br><br>Arrival Time: {trip._adjusted_schedule_time} mins",
                    icon=folium.Icon(icon="bus", prefix="fa"),
                ).add_to(bus_map)

            # Save map to HTML
            bus_map.save('bus_map.html')

            # Open the map in the default web browser
            webbrowser.open('file://' + os.path.realpath('bus_map.html'))
        else:
            messagebox.showinfo('Info', 'Bus stop not found.')

    def save_to_favorites(self, stop_no, route_no):
        self.favorites.save_to_favorites(stop_no, route_no)
        messagebox.showinfo('Info', 'Saved to favorites!')

    def remove_from_favorites(self, stop_no, route_no):
        self.favorites.remove_from_favorites(stop_no, route_no)
        messagebox.showinfo('Info', 'Removed from favorites!')

    def display_favorites(self):
        favorites = self.favorites.get_favorites()
        self.view.display_favorites(favorites)

    def remove_favorite(self, stop, route):
        self.favorites.remove_from_favorites(stop, route)
        self.display_favorites()  # Refresh the display
