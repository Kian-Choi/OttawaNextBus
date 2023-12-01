# bus_recorder.py
from datetime import datetime
import time
import csv
import os.path
from model import fetch_next_trips_all_routes

FIELDNAMES = [
    'FetchTime',
    'StopNo',
    'RouteNo',
    'TripDestination',
    'TripStartTime',
    'AdjustedScheduleTime',
    'Longitude',
    'Latitude'
]


def write_header(file):
    writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
    writer.writeheader()


def write_trip_data(stop_no, file, trip_list):
    writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
    for t in trip_list:
        writer.writerow({
            'FetchTime': datetime.now(),
            'StopNo': stop_no,
            'RouteNo': t._route_no,
            'TripDestination': t._route_heading,
            'TripStartTime': t._trip_start_time,
            'AdjustedScheduleTime': t._adjusted_schedule_time,
            'Longitude': t._longitude,
            'Latitude': t._latitude
        })


def fetch_and_write_trip(stop_no):
    trips = fetch_next_trips_all_routes(stop_no)
    print(f'{len(trips)} trips fetched for {stop_no}')
    file_path = './result.csv'

    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as file:
            write_header(file)

    with open(file_path, 'a', newline='') as file:
        write_trip_data(stop_no, file, trips)


def main():
    interval = 30

    while True:
        # from home to work
        if 5 <= datetime.now().hour < 8:
            fetch_and_write_trip(3044)  # Strandherd
            fetch_and_write_trip(3014)  # Lincoln field
            fetch_and_write_trip(1824)  # Moodie / Crystal Bay Centre
            fetch_and_write_trip(3017)  # Baseline
            print(f'fetched successfully, wait {interval} seconds')

        # from work to home
        elif 14 <= datetime.now().hour < 17:
            fetch_and_write_trip(8492)  # Tim hortons 58 66
            fetch_and_write_trip(8494)  # Tim hortons 57
            fetch_and_write_trip(3015)  # Queensway

            print(f'fetched successfully, wait {interval} seconds')
            print()
        else:
            print(f'not in dedicated timezone, wait {interval} seconds to fetch again')
            print(datetime.now())
            print()
        time.sleep(interval)


if __name__ == "__main__":
    # print(os.getcwd())
    main()
