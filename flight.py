from __future__ import annotations

import datetime
from typing import Dict, List, Optional, Tuple

# Global Airplane Seat Type capacity
AIRPLANE_CAPACITY = {"Economy": 150, "Business": 22}


class FlightSegment:
    """ A FlightSegment offered by the airline system.

    === Public Attributes ===
    seat_capacity:
        the class of seat and total number of seats available on a specific
        segment.
    seat_availability:
        the class of seat and number of seats still available on a specific
        segment.

    === Representation Invariants ===
        -  the keys in seat_availability.keys() must all be >= 0
           (i.e. they cannot be negative)
    """

    # === Private Attributes ===
    # _flight_id:
    #     a unique identifier for this flight.
    # _time:
    #     a tuple containing the departure and arrival time of a segment.
    # _manifest:
    #      a list of tuples containing all customers' ID and type of flight
    #      class that they've taken (e.g. economy).
    # _base_fare_cost:
    #     the base cost of the fare (e.g., $0.1225/km).
    # _flight_duration:
    #     the total time it takes for the flight segment to complete.
    # _flight_length:
    #     the number of kilometers between the departure and arrival locations.
    # _dep_loc:
    #     the unique 3-digit (IATA) airport identifier of where the flight
    #     segment is departing (i.e. leaving from).
    # _arr_loc:
    #     the unique 3-digit (IATA) airport identifier of where the flight
    #     segment is landing (i.e. arriving to).
    # _long_lat:
    #     a tuple of tuples, containing the longitude and latitude of the
    #     departure and arrival destinations.
    #
    # === Representation Invariants ===
    #     -  _flight_length >= 0
    #     -  _dep_loc and _arr_loc must be exactly three characters [A-Z]
    #        and are assumed to be valid and distinct IATA airport codes.

    seat_capacity: Dict[str, int]  # str: class, int: seats_available
    seat_availability: Dict[str, int]  # str: class, int: seats_available
    _flight_id: str
    _time: Tuple[datetime.datetime, datetime.datetime]
    _base_fare_cost: float
    _flight_duration: datetime.time
    _flight_length: float
    _dep_loc: str
    _arr_loc: str
    _long_lat: Tuple[Tuple[float, float], Tuple[float, float]]
    _manifest: List[Tuple[int, str]]  # (customer_id, seat_type)

    def __init__(
            self,
            fid: str,
            dep: datetime.datetime,
            arr: datetime.datetime,
            base_cost: float,
            length: float,
            dep_loc: str,
            arr_loc: str,
            long_lat: Tuple[Tuple[float, float], Tuple[float, float]]
    ) -> None:
        """
        Initialize a FlightSegment object based on the parameters specified.
        """
        self._flight_id = fid
        self._time = (dep, arr)
        self._base_fare_cost = base_cost
        self._flight_length = length
        self._dep_loc = dep_loc
        self._arr_loc = arr_loc
        self._long_lat = long_lat
        self._manifest = []
        self.seat_capacity = {}
        self.seat_availability = {}

        delta = arr - dep
        hours = int(delta.total_seconds()) // 3600
        minutes = (int(delta.total_seconds()) % 3600) // 60
        seconds = int(delta.total_seconds()) % 60
        duration_as_time = datetime.time(hour=hours,
                                         minute=minutes,
                                         second=seconds,
                                         microsecond=delta.microseconds)
        self._flight_duration = duration_as_time

    def __repr__(self) -> str:
        return ("[" + str(self._flight_id) + "]:" + str(self._dep_loc) + "->"
                + str(self._arr_loc))

    def get_length(self) -> float:
        """ Returns the length, in KMs, of this flight segment. """
        return self._flight_length

    def get_times(self) -> Tuple[datetime.datetime, datetime.datetime]:
        """ Returns the (departure, arrival) time of this flight segment. """
        return self._time

    def get_arr(self) -> str:
        """ Returns the arrival airport (i.e. the IATA). """
        return self._arr_loc

    def get_dep(self) -> str:
        """ Returns the departure airport (i.e. the IATA). """
        return self._dep_loc

    def get_fid(self) -> str:
        """ Returns the flight identifier. """
        return self._flight_id

    def get_long_lat(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """ Returns the longitude and latitude of a FlightSegment,
            specifically like this: ((LON1, LAT1), (LON2, LAT2)).
        """
        return self._long_lat

    def get_duration(self) -> datetime.time:
        """ Returns the duration of the flight. """
        return self._flight_duration

    def get_base_fare_cost(self) -> float:
        """ Returns the base fare cost for this flight segment. """
        return self._base_fare_cost

    def check_manifest(self, cid: int) -> bool:
        """ Returns True if a certain customer <cid> has booked a seat
            on this specific flight, otherwise False.
        """
        for customers in self._manifest:
            if cid == customers[0]:
                return True
        return False

    def check_seat_class(self, cid: int) -> Optional[str]:
        """ Checks the manifest to see what class of cabin a certain customer
            (based on their <cid>) has booked. None is returned in the event
            there is no seat booked for that <cid>.
        """
        if not self.check_manifest(cid):
            return None
        else:
            for i in range(len(self._manifest)):
                if self._manifest[i][0] == cid:
                    return self._manifest[i][1]
                else:
                    continue
        return None

    def _count_booked_classes(self) -> dict[str, int]:
        """
        helper for book seat that counts the total
        available economy and business class seats
        """
        total_economy = 0
        total_business = 0
        for cust in self._manifest:
            if cust[1] == "Economy":
                total_economy += 1
            else:
                total_business += 1
        return {"Economy": total_economy, "Business": total_business}

    def book_seat(self, cid: int, seat_type: str) -> None:
        """ Book a seat of the given <seat_type> for the customer <cid>.
            If that customer is already booked, do nothing. If the seat
            type is different, and it is available, make the change.
        """
        counts = self._count_booked_classes()
        cap = AIRPLANE_CAPACITY

        if not self.check_manifest(cid):
            if counts[seat_type] < cap[seat_type]:
                self._manifest.append((cid, seat_type))
            return

        current = self.check_seat_class(cid)
        if current == seat_type:
            return
        if counts[seat_type] >= cap[seat_type]:
            return

        for idx, (cust_id, _) in enumerate(self._manifest):
            if cust_id == cid:
                self._manifest[idx] = (cid, seat_type)
                break

    def cancel_seat(self, cid: int) -> None:
        """	If a seat has already been booked by <cid>, cancel the booking
            and restore the seat's availability. Otherwise, do nothing and
            return None.
        """
        for i, (cust_id, _) in enumerate(self._manifest):
            if cust_id == cid:
                self._manifest.pop(i)
                break


# ------------------------------------------------------------------------------
class Trip:
    """ A Trip is composed of FlightSegment(s) which makes up a customer's
        itinerary.

    === Public Attributes ===
    reservation_id:
         a unique identifier for this trip.
    customer_id:
         the unique identifier of the customer who booked this trip.
    trip_departure:
         the date in which this trip was booked.
    """
    # === Private Attributes ===
    # _flights:
    #      a list of all flight segments for this particular trip
    reservation_id: str
    customer_id: int
    trip_departure: datetime.date
    _flights: List[FlightSegment]

    def __init__(self, rid: str, cid: int, trip_date: datetime.date,
                 flight_segments: List[FlightSegment]) -> None:
        """ Initializes a trip object given the specified parameters. """
        self.reservation_id = rid
        self.customer_id = cid
        self.trip_departure = trip_date
        self._flights = flight_segments

    def get_flight_segments(self) -> List[FlightSegment]:
        """ Returns a list of all Flight Segments part of this booking. """
        return self._flights

    def get_reservation_id(self) -> str:
        """ Returns this Trip's Reservation ID. """
        return self.reservation_id

    def get_in_flight_time(self) -> int:
        """ Returns the amount of time (in minutes) the trip is spent in
            flight (i.e. the time in the air only).
        """
        tot_time = 0
        for segment in self.get_flight_segments():
            dep, arr = segment.get_times()
            delta = arr - dep
            tot_time += int(delta.total_seconds() // 60)
        return tot_time

    def get_total_trip_time(self) -> int:
        """ Returns the amount of time (in minutes) the trip is takes,
            including all transit time (i.e. including waiting for the next
            flight on a layover).
        """
        if not self._flights:
            return 0

        segs = sorted(self._flights, key=lambda s: s.get_times()[0])  # chrono
        total = 0
        prev_arr = None

        for seg in segs:
            dep, arr = seg.get_times()
            flight_min = int((arr - dep).total_seconds() // 60)
            total += flight_min

            if prev_arr is not None:
                layover_min = int((dep - prev_arr).total_seconds() // 60)
                if layover_min > 0:  # ignore overlaps (shouldn’t happen)
                    total += layover_min
            prev_arr = arr

        return total


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'doctest',
            'datetime', '__future__'
        ],
        'max-attributes': 11,
        'max-args': 9
    })
