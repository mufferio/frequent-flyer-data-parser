import csv
import datetime
from typing import Dict, List, Tuple

from airport import Airport
from customer import Customer
from flight import Trip, FlightSegment
from visualizer import Visualizer

#############################################
# DO NOT DECLARE ANY OTHER GLOBAL VARIABLES!
#############################################

# AIRPORT_LOCATIONS: global mapping of an airport's IATA with their respective
#                    longitude and latitude positions.
# NOTE: This is used for our testing purposes, so it has to be populated in
# create_airports(), but you are welcome to use it as you see fit.
AIRPORT_LOCATIONS = {}

# DEFAULT_BASE_COST: Default rate per km for the base cost of a flight segment.
DEFAULT_BASE_COST = 0.1225


def import_data(file_airports: str, file_customers: str, file_segments: str,
                file_trips: str) -> Tuple[List[List[str]], List[List[str]],
                                          List[List[str]], List[List[str]]]:
    """
    Opens all the data files <data/filename.csv> which stores the CSV data,
    and returns a tuple of lists of lists of strings. This contains the
    read in data, line-by-line, (airports, customers, flights, trips).

    Precondition: the dataset file must be in CSV format.
    """

    airport_log, customer_log, flight_log, trip_log = [], [], [], []

    airport_data = csv.reader(open(file_airports))
    customer_data = csv.reader(open(file_customers))
    flight_data = csv.reader(open(file_segments))
    trip_data = csv.reader(open(file_trips))

    for row in airport_data:
        airport_log.append(row)

    for row in flight_data:
        flight_log.append(row)

    for row in customer_data:
        customer_log.append(row)

    for row in trip_data:
        trip_log.append(row)

    return airport_log, flight_log, customer_log, trip_log


def create_customers(log: List[List[str]]) -> Dict[int, Customer]:
    """ Returns a dictionary of Customer IDs and their Customer instances, 
    based on the customers from the input dataset from the <log>.

    Precondition:
        - The <log> list contains the input data in the correct format.
    """
    final = {}
    for customer in log:
        cust_id = int(customer[0])
        name = customer[1]
        age = int(customer[2])
        nationality = customer[3]
        new_cust = Customer(cust_id, name, age, nationality)
        final[cust_id] = new_cust
    return final


def create_flight_segments(log: List[List[str]]) \
        -> Dict[datetime.date, List[FlightSegment]]:
    """ Returns a dictionary storing all FlightSegments, indexed by their
    departure date, based on the input dataset stored in the <log>.

    Precondition:
    - The <log> list contains the input data in the correct format.
    """
    final = {}
    for segment in log:
        flight_id = segment[0]
        dep_loc = segment[1]
        arr_loc = segment[2]
        dep_day_str = segment[3]
        dep_hour_str = segment[4]
        arr_hour_str = segment[5]
        flight_length = float(segment[6])
        dep_date = datetime.datetime(year=int(dep_day_str[0:4]),
                                     month=int(dep_day_str[5:7]),
                                     day=int(dep_day_str[8:10]),
                                     hour=int(dep_hour_str[0:2]),
                                     minute=int(dep_hour_str[3:5]))
        arr_date = datetime.datetime(year=int(dep_day_str[0:4]),
                                     month=int(dep_day_str[5:7]),
                                     day=int(dep_day_str[8:10]),
                                     hour=int(arr_hour_str[0:2]),
                                     minute=int(arr_hour_str[3:5]))
        if arr_date <= dep_date:
            arr_date += datetime.timedelta(days=1)

        segment_obj = FlightSegment(
            flight_id, dep_date, arr_date,
            DEFAULT_BASE_COST, flight_length, dep_loc, arr_loc,
            (AIRPORT_LOCATIONS[dep_loc], AIRPORT_LOCATIONS[arr_loc])
        )
        dep_day = dep_date.date()
        if dep_day not in final:
            final[dep_day] = []
        final[dep_day].append(segment_obj)
    return final


def create_airports(log: List[List[str]]) -> List[Airport]:
    """ Return a list of Airports with all applicable data, based
    on the input dataset stored in the <log>.

    Precondition:
    - The <log> list contains the input data in the correct format.
    """
    final_airports = []
    for airport in log:
        name = airport[1]
        aid = airport[0]
        loc = (float(airport[2]), float(airport[3]))
        new = Airport(name, aid, loc)
        final_airports.append(new)
        AIRPORT_LOCATIONS[aid] = loc
    return final_airports


def _strip_outer_quotes(text: str) -> str:
    """Helper for Load Trips.
    Remove a single pair of matching quotes surrounding <text>, if any."""
    return text[1:-1] if (len(text) >= 2
                          and text[0] == text[-1]
                          and text[0] in "\"'") else text


def _parse_itinerary_literal(raw: str) -> list[tuple[str, str]]:
    """Helper for Load Trips
    Return a cleaned [(airport, seat-class), …] list or [] on error."""
    cleaned = _strip_outer_quotes(raw)
    return _row_3_str_parse(cleaned)


def _build_seg_pairs(itinerary: list[tuple[str, str]],
                     segments_today: list[FlightSegment]
                     ) -> list[tuple[FlightSegment, str]] | None:
    """
    Helper for load trips
    Match consecutive legs in <itinerary> to FlightSegments.
    Return a list [(segment, seat-class), …] or None if any leg is invalid.
    """
    pairs = []
    for (dep, seat), (arr, _) in zip(itinerary, itinerary[1:]):
        if seat == '':
            return None
        seg = next((s for s in segments_today
                    if s.get_dep() == dep and s.get_arr() == arr), None)
        if seg is None:
            return None
        pairs.append((seg, seat))
    return pairs


def _row_3_str_parse(row: str) -> List[Tuple[str, str]]:
    """
    Helper for load trips
    Parse a string like "[('SCL','Business'),('FCO','Business'),...]" into
    a list of (dep_loc, seat_type) tuples.
    """
    s = row.strip()
    if s.startswith('[') and s.endswith(']'):
        s = s[1:-1]
    result = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] == '(':
            j = s.find(')', i)
            if j == -1:
                break
            content = s[i + 1:j]
            raw = (content.replace("'", "").
                   replace('"', ""))
            parts = raw.split(',', 1)
            dep_loc = parts[0].strip()
            if len(parts) > 1:
                seat_type = parts[1].strip()
            else:
                seat_type = ''
            result.append((dep_loc, seat_type))
            i = j + 1
        else:
            i += 1
    return result


def load_trips(log: List[List[str]], customer_dict: Dict[int, Customer],
               flight_segments: Dict[datetime.date, List[FlightSegment]]) \
        -> List[Trip]:
    """ Creates the Trip objects and makes the bookings.

    Preconditions:
    - The <log> list contains the input data in the correct format.
    - the customers are already correctly stored in the <customer_dict>,
    indexed by their customer ID.
    - the flight segments are already correctly stored in the 
    <flight_segments>, indexed by their departure date
    """
    trips_loaded = []
    for row in log:
        if len(row) < 4:
            continue
        rid, cid_str, date_str = row[:3]
        customer = customer_dict.get(int(cid_str))
        if customer is None:
            continue
        trip_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        itinerary = _parse_itinerary_literal(",".join(row[3:]))
        if len(itinerary) < 2:
            continue
        seg_pairs = _build_seg_pairs(itinerary,
                                     flight_segments.get(trip_date, []))
        if seg_pairs is None:
            continue
        trips_loaded.append(customer.book_trip(rid, seg_pairs, trip_date))
    return trips_loaded


if __name__ == '__main__':
    print("\n---------------------------------------------")
    print("Reading in all data! Processing...")
    print("---------------------------------------------\n")

    # input_data = import_data('data/airports.csv', 'data/customers.csv',
    #     'data/segments.csv', 'data/trips.csv')
    input_data = import_data('data/airports.csv', 'data/customers.csv',
                             'data/segments_small.csv', 'data/trips_small.csv')

    airports = create_airports(input_data[0])
    print("Airports Created! Still Processing...")
    flights = create_flight_segments(input_data[1])
    print("Flight Segments Created! Still Processing...")
    customers = create_customers(input_data[2])
    print("Customers Created! Still Processing...")
    print("Loading trips can take a while...")
    trips = load_trips(input_data[3], customers, flights)
    print("Trips Created! Opening Visualizer...\n")

    flights_len = 0
    for ky in flights:
        flights_len += len(flights[ky])

    print("---------------------------------------------")
    print("Some Statistics:")
    print("---------------------------------------------")
    print("Total airports in the dataset:", len(airports))
    print("Total flight segments in the dataset:", flights_len)
    print("Total customers in the dataset:", len(customers))
    print("Total trips in the dataset:", len(trips))
    print("---------------------------------------------\n")

    all_flights = [seg for tp in trips for seg in tp.get_flight_segments()]
    all_customers = [customers[cid] for cid in customers]

    V = Visualizer()
    V.draw(all_flights)

    while not V.has_quit():

        flights = V.handle_window_events(all_customers, all_flights)

        all_flights = []

        for flt in flights:
            all_flights.append(flt)

        V.draw(all_flights)

    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'csv', 'datetime', 'doctest',
            'visualizer', 'customer', 'flight', 'airport'
        ],
        'max-nested-blocks': 6,
        'allowed-io': [
            'create_customers', 'create_airports', 'import_data',
            'create_flight_segments', 'load_trips'
        ],
        'generated-members': 'pygame.*'
    })
