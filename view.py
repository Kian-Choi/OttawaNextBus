# view.py

import tkinter as tk
from tkinter import messagebox, ttk, Toplevel, StringVar, Listbox, END
from threading import Thread
import csv


class View:
    def __init__(self, window, presenter):
        self.window = window
        self.presenter = presenter
        self.search_window_open = False
        self.stop_search_window = None

        self.window.title('Ottawa Next Bus')
        self.entry_stop = tk.Entry(window)
        self.entry_route = tk.Entry(window)
        self.search_button = tk.Button(window, text='Search Stop', command=self.open_stop_search)

        # Define Treeview for table
        self.tree = ttk.Treeview(window, columns=('Route Number', 'Destination', 'Is Real Time', 'Arrival Time'),
                                 show='headings')
        self.tree.column('Route Number', width=100)
        self.tree.column('Destination', width=200)
        self.tree.column('Is Real Time', width=100)
        self.tree.column('Arrival Time', width=100)
        self.tree.heading('Route Number', text='Route Number')
        self.tree.heading('Destination', text='Destination')
        self.tree.heading('Is Real Time', text='Is Real Time')
        self.tree.heading('Arrival Time', text='Arrival Time')

        # Place widgets
        tk.Label(window, text='Enter Stop No.').grid(row=0)
        self.entry_stop.grid(row=0, column=1)
        self.search_button.grid(row=0, column=2)
        tk.Label(window, text='Enter Route No.').grid(row=1)
        self.entry_route.grid(row=1, column=1)
        self.tree.grid(row=3, column=0, columnspan=3, sticky="nsew")

        # Buttons
        tk.Button(window, text='Get Route Summary',
                  command=lambda: Thread(target=self.presenter.fetch_and_display_route_summary).start()).grid(row=2, column=0)
        tk.Button(window, text='Get Next Trips',
                  command=lambda: Thread(target=self.presenter.fetch_and_display_next_trips).start()).grid(row=2, column=1)
        tk.Button(window, text='Get Next Trips for All Routes',
                  command=lambda: Thread(target=self.presenter.fetch_and_display_next_trips_all_routes).start()).grid(
            row=2, column=2)
        tk.Button(window, text='Show on the Map',
                  command=lambda: Thread(target=self.presenter.show_on_map).start()).grid(row=4, column=0)
        tk.Button(window, text='Save to Favorites', command=self.save_to_favorites).grid(row=4, column=1)
        tk.Button(window, text='Show Favorites', command=self.show_favorites).grid(row=4, column=2)

        # Configure the rows and columns to resize with the window
        window.grid_rowconfigure(3, weight=1)
        window.grid_columnconfigure(0, weight=1)
        window.grid_columnconfigure(1, weight=1)
        window.grid_columnconfigure(2, weight=1)

    def open_stop_search(self):
        if not self.search_window_open:
            self.search_window_open = True
            self.stop_search_window = Toplevel(self.window)
            self.stop_search_window.title('Search Stop')
            self.stop_search_window.geometry('400x300')

            stop_search_entry = tk.Entry(self.stop_search_window)
            stop_search_entry.pack(fill="x", expand=True)

            stop_listbox = Listbox(self.stop_search_window)
            stop_listbox.pack(fill="both", expand=True)

            stop_search_entry.bind('<KeyRelease>', lambda e: self.search_stop(stop_search_entry.get(), stop_listbox))
            stop_listbox.bind('<<ListboxSelect>>',
                              lambda e: self.update_stop_entry(stop_listbox.get(stop_listbox.curselection())))

    def search_stop(self, search_term, stop_listbox):
        stops = self.load_stops(search_term)
        stop_listbox.delete(0, END)
        for stop in stops:
            stop_listbox.insert(END, stop)

    def load_stops(self, search_term):
        stops = []
        with open('./data/stops.csv', 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if search_term.lower() in row['stop_name'].lower() or search_term in row['stop_code']:
                    stops.append(f"{row['stop_code']} - {row['stop_name']}")
        return stops

    def update_stop_entry(self, stop):
        self.entry_stop.delete(0, END)
        self.entry_stop.insert(0, stop.split(" - ")[0])
        self.search_window_open = False
        self.stop_search_window.destroy()

    def get_stop_no(self):
        return self.entry_stop.get()

    def get_route_no(self):
        return self.entry_route.get()

    def display_trips(self, trips):
        for trip in trips:
            self.tree.insert('', 'end', values=(
                trip._route_no, trip._route_heading, trip.is_real_time, trip._adjusted_schedule_time))

    def display_routes(self, routes):
        for route in routes:
            self.tree.insert('', 'end', values=(route._route_no, route._route_heading, 'N/A', 'N/A'))

    def clear_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

    def save_to_favorites(self):
        stop_no = self.get_stop_no()
        route_no = self.get_route_no()
        self.presenter.save_to_favorites(stop_no, route_no)

    def remove_from_favorites(self):
        stop_no = self.get_stop_no()
        route_no = self.get_route_no()
        self.presenter.remove_from_favorites(stop_no, route_no)

    def show_favorites(self):
        self.favorites_window = Toplevel(self.window)
        self.favorites_window.title('Favorites')

        # Define Treeview for table
        self.fav_tree = ttk.Treeview(self.favorites_window, columns=('Stop', 'Route'), show='headings')
        self.fav_tree.column('Stop', width=100)
        self.fav_tree.column('Route', width=100)
        self.fav_tree.heading('Stop', text='Stop No.')
        self.fav_tree.heading('Route', text='Route No.')
        self.fav_tree.pack(fill="both", expand=True)

        remove_button = tk.Button(self.favorites_window, text='Remove', command=lambda: self.remove_selected_favorite())
        remove_button.pack()

        favorites = self.presenter.favorites.get_favorites()
        for fav in favorites:
            self.fav_tree.insert('', 'end', values=(fav['stop'], fav['route']))

        # Bind double-click event
        self.fav_tree.bind('<Double-1>', self.fill_fields_with_selected_favorite)

    def fill_fields_with_selected_favorite(self, event):
        selected_item = self.fav_tree.selection()[0]  # Get the item clicked
        stop, route = self.fav_tree.item(selected_item, 'values')

        self.entry_stop.delete(0, END)
        self.entry_stop.insert(0, stop)
        self.entry_route.delete(0, END)
        self.entry_route.insert(0, route)

        # Close the favorites window
        self.favorites_window.destroy()

    def remove_selected_favorite(self):
        selected_item = self.fav_tree.selection()[0]  # Get the item clicked
        stop, route = self.fav_tree.item(selected_item, 'values')

        self.presenter.remove_from_favorites(stop, route)
        self.fav_tree.delete(selected_item)  # Remove the item from the Treeview
