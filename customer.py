from __future__ import annotations

from datetime import datetime
from typing import List, Tuple, Dict, Optional

from flight import Trip, FlightSegment

"""
    FF_Status: Dict[str, Tuple(int, int)] where the Tuple(status miles to 
               reach discount for fares from the next trip (NOT flight segment)
               after the status is achieved).
               The units are (Kilometers, Percent).
"""
FREQUENT_FLYER_STATUS = {"Prestige": (15000, -10), "Elite-Light": (30000, -15),
                         "Elite-Regular": (50000, -20),
                         "Super-Elite": (100000, -25)}

"""
    FREQUENT_FLYER_MULTIPLIER: the key is the type of cabin class (seat type), 
                               the value is the miles multiplier (status miles 
                               are calculated by multiplying the flight length 
                               by this miles multiplier).
"""
FREQUENT_FLYER_MULTIPLIER = {"Economy": 1, "Business": 5}

"""
    CLASS_MULTIPLIER: used to determine the real-cost of the segment based on 
                      the class of flight: Dict(str, float) taken by the 
                      customer, where the Dict(class, multiplier).
"""
CLASS_MULTIPLIER = {"Economy": 1.0, "Business": 2.5}


class Customer:
    """ A Customer of Python Air.

    === Public Attributes ===
    name:
        the customer's name (may include one or all:
        first, middle, and last).
    age:
        the customer's age.
    nationality:
        the customer's nationality (there are no dual citizens).
    all_flight_costs:
        the sum of all flight costs this customer has taken over
        the course of their existence.

    Representation Invariants:
        - trips are stored per customer forever.
        - miles/status are accumulated and never lost.
    """

    # === Private Attributes ===
    # _customer_id:
    #     this is a unique 6-digit customer identifier.
    # _ff_status:
    #     this is the customer's frequent flyer status.
    # _miles:
    #     this is the running tally of the customer's
    #     total qualifying miles for their status.
    # _trips:
    #     this stores the dictionary of Trips and their
    #     corresponding costs.

    name: str
    age: int
    nationality: str
    all_flight_costs: float
    _customer_id: int
    _trips: Dict[Trip, float]
    _ff_status: str
    _miles: int

    def __init__(self, cus_id: int, name: str, age: int, nat: str) -> None:
        """ A Customer of Python Air. """
        self.name = name
        self.age = age
        self.nationality = nat
        self.all_flight_costs = 0.0
        self._customer_id = cus_id
        self._trips = {}
        self._ff_status = ""
        self._miles = 0

    def get_id(self) -> int:
        """ Returns this customer's identification (ID). """
        return self._customer_id

    def get_trips(self) -> List[Trip]:
        """ Returns a list of Trips booked for this customer. """
        final_list = []
        for trip in self._trips:
            final_list.append(trip)
        return final_list

    def get_total_flight_costs(self) -> float:
        """ Returns this customer's total flight costs. """
        final_list = self.get_trips()
        tot = 0.0
        for trip in final_list:
            tot += self._trips[trip]
        return tot

    def get_cost_of_trip(self, trip_lookup: Trip) -> Optional[float]:
        """ Returns the cost of that Trip, otherwise None. """
        return self._trips.get(trip_lookup)

    def get_ff_status(self) -> str:
        """ Returns this customer's frequent flyer status. """
        return self._ff_status

    def get_miles(self) -> int:
        """ Returns this customer's qualifying miles. """
        return self._miles

    def _increase_miles(self, segment: FlightSegment, seat_type: str) -> None:
        """
        helper method which increases a customers miles based on
        flight length of kilometres <length> inputted
        """
        self._miles += (FREQUENT_FLYER_MULTIPLIER[seat_type]
                        * segment.get_length())

    def _update_ff_status(self) -> None:
        """
        helper method which checks and updates a customers frequent flier
        status based on the miles in their customer profile.
        """
        m = self._miles
        if m >= FREQUENT_FLYER_STATUS["Super-Elite"][0]:
            self._ff_status = "Super-Elite"
        elif m >= FREQUENT_FLYER_STATUS["Elite-Regular"][0]:
            self._ff_status = "Elite-Regular"
        elif m >= FREQUENT_FLYER_STATUS["Elite-Light"][0]:
            self._ff_status = "Elite-Light"
        elif m >= FREQUENT_FLYER_STATUS["Prestige"][0]:
            self._ff_status = "Prestige"
        else:
            self._ff_status = ""

    def _update_flight_cost(self, segment: FlightSegment,
                            seat_type: str) -> None:
        """
        helper method to update flight costs of a customer
        """
        self.all_flight_costs += (segment.get_base_fare_cost()
                                  * CLASS_MULTIPLIER[seat_type])

    def book_trip(self, reservation_id: str,
                  segments: List[Tuple[FlightSegment, str]],
                  trip_date: datetime.date) -> Trip:
        """ Books the customer's trip and returns a Trip.

            <segments> are a List of Tuples, containing a (FlightSegment,
            seat_type) pair.

            Precondition: the customer is guaranteed to have a seat on each of
                          the <segments>.
        """
        discount_pct = FREQUENT_FLYER_STATUS.get(self._ff_status, (0, 0))[1]
        discount_factor = 1 + discount_pct / 100.0
        raw_cost = 0.0
        just_segments: List[FlightSegment] = []
        for seg, seat in segments:
            seg.book_seat(self.get_id(), seat)
            just_segments.append(seg)
            raw_cost += seg.get_base_fare_cost() * CLASS_MULTIPLIER[seat]
        trip_cost = raw_cost * discount_factor
        for seg, seat in segments:
            self._miles += FREQUENT_FLYER_MULTIPLIER[seat] * seg.get_length()
        self.all_flight_costs += trip_cost
        trip_obj = Trip(reservation_id, self.get_id(), trip_date, just_segments)
        self._trips[trip_obj] = trip_cost
        self._update_ff_status()
        return trip_obj

    def cancel_trip(self, canceled_trip: Trip,
                    segments: List[Tuple[FlightSegment, str]]) -> None:
        """ Cancels this customer's Trip.

            <segments> are a List of Tuples, containing the (FlightSegment,
            seat_type) pair.

            Precondition: the <canceled_trip> must be a valid Trip that this
                          customer has booked.
        """
        for segment, _ in segments:
            segment.cancel_seat(self.get_id())
        original_cost = self._trips[canceled_trip]
        self.all_flight_costs -= original_cost
        self.all_flight_costs -= 100.0


if __name__ == '__main__':

    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta',
            'typing',
            'doctest',
            'flight',
            '__future__',
            'datetime'
        ],
        'max-attributes': 8,
    })
