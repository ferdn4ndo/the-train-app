from app.simulation.exception.error import ConflictConditionError, UnprocessableEntityError


class Section:
    SECTION_START_STRAIGHT = "start_straight"
    SECTION_START_DEVIATED = "start_deviated"
    SECTION_END_STRAIGHT = "end_straight"
    SECTION_END_DEVIATED = "end_deviated"

    def __init__(
        self,
        name,
        start_kilometer=0.0,  # [km]
        length=100,  # [m]
        connections=None,
        flow="both",  # 'both', 'normal-only', 'reverse-only'
        lines=None,
        restrictions=None,
        description=""
    ):
        if restrictions is None:
            restrictions = []
        if lines is None:
            lines = []
        if connections is None:
            connections = []
        self.name = name
        self.length = length
        self.flow = flow
        self.lines = lines
        self.description = description

        self.start_kilometer = start_kilometer
        self.end_kilometer = start_kilometer + length

        self.max_velocity = 60  # km/h

        self.connections = []
        self.read_connections(connections)

        self.restrictions = []
        self.read_restrictions(restrictions)

        self.interdicted = False

    def __eq__(self, other):
        return self.name == other.name if isinstance(other, Section) else False

    def __repr__(self):
        return "<Section_{}_[at {}]>".format(self.name, hex(id(self)))

    def get_sections_ahead(self, backwards=False):
        when_at = (
            [self.SECTION_START_STRAIGHT, self.SECTION_START_DEVIATED]
            if backwards else
            [self.SECTION_END_STRAIGHT, self.SECTION_END_DEVIATED]
        )

        return [
            connection.destiny_section_name for connection in self.connections
            if connection.connection_origin in when_at
        ]

    def read_connections(self, connections_list):
        for connection in connections_list:
            connection_object = SectionConnection(
                connection["connects_to"],
                connection["when_at"]
            )
            self.connections.append(connection_object)

    def read_restrictions(self, restriction_list):
        for restriction in restriction_list:
            restriction_object = SectionRestriction(
                self,
                start_km=restriction["start_km"],
                end_km=restriction["end_km"],
                max_velocity=restriction["max_speed"]
            )
            self.restrictions.append(restriction_object)

    def maximum_velocity_at_relative_position(self, relative_position):
        active_restrictions = [
            restriction for restriction in self.restrictions
            if restriction.is_active_at_position(relative_position)
        ]

        if len(active_restrictions) > 0:
            return min([restriction.max_velocity for restriction in active_restrictions])

        return self.max_velocity

    def clear(self):
        self.connections = []
        self.flow = "both"
        self.lines = []
        self.start_kilometer = 0.0

    def interdict(self):
        if self.interdicted:
            raise ConflictConditionError(
                'Section {} is already interdicted!',
                self.name
            )

        self.interdicted = True

    def is_turnout(self):
        return True if len(self.accessible_connections()) > 2 else False

    def get_origin_map(self):
        return [
            {connection_name: self.get_relative_origin(connection_name)}
            for connection_name in
            self.accessible_connections()
        ]

    def get_relative_origin(self, origin_section_name):
        for connection in self.connections:
            if connection.destiny_section_name == origin_section_name:
                return connection.connection_origin
        return None

    def clear_interdiction(self):
        if not self.interdicted:
            raise ConflictConditionError(
                'Section {} is already clear!',
                self.name
            )

        self.interdicted = False

    def accessible_connections(self, origin="both"):
        if origin == "both":
            possible_origins = (
                Section.SECTION_START_STRAIGHT, Section.SECTION_START_DEVIATED,
                Section.SECTION_END_STRAIGHT, Section.SECTION_END_DEVIATED
            )
        elif origin == "start":
            possible_origins = (Section.SECTION_START_STRAIGHT, Section.SECTION_START_DEVIATED)
        elif origin == "end":
            possible_origins = (Section.SECTION_END_STRAIGHT, Section.SECTION_END_DEVIATED)
        else:
            possible_origins = [origin]

        return list(
            connection.destiny_section_name for connection in self.connections
            if connection.connection_origin in possible_origins
        )

    def serialize(self):
        return {
            "name": self.name,
            "connections": {
                "start_straight": self.accessible_connections("start_straight"),
                "start_deviated": self.accessible_connections("start_deviated"),
                "end_straight": self.accessible_connections("end_straight"),
                "end_deviated": self.accessible_connections("end_deviated"),
                "start": list(
                    self.accessible_connections("start_straight") +
                    self.accessible_connections("start_deviated")
                ),
                "end": list(
                    self.accessible_connections("end_straight") +
                    self.accessible_connections("end_deviated")
                ),
                "both": self.accessible_connections(),
            },
            "lines": self.lines,
            "flow": self.flow,
            "start_kilometer": self.start_kilometer,
            "restrictions": self.restrictions,
            "is_turnout": self.is_turnout(),
            "length": self.length,
            "origin_map": self.get_origin_map(),
            "interdicted": self.interdicted,
        }


class SectionRestriction:

    def __init__(self, section: Section, start_km, end_km, max_velocity):
        self.start_km = start_km
        self.end_km = end_km

        self.start_position = (start_km - section.start_kilometer) / section.length
        self.end_position = (end_km - section.start_kilometer) / section.length

        self.max_velocity = max_velocity

    def is_active_at_position(self, position):
        return True if self.start_position <= position <= self.end_position else False


class SectionConnection:

    def __init__(
            self,
            destiny_section_name,
            connection_origin=Section.SECTION_START_STRAIGHT,
    ):
        if connection_origin not in [
            Section.SECTION_START_STRAIGHT,
            Section.SECTION_END_STRAIGHT,
            Section.SECTION_START_DEVIATED,
            Section.SECTION_END_DEVIATED
        ]:
            raise UnprocessableEntityError("The origin '{}' is unknown".format(connection_origin))

        self.destiny_section_name = destiny_section_name
        self.connection_origin = connection_origin

    def __eq__(self, other):
        return (
                self.destiny_section_name == other.destiny_section_name and
                self.connection_origin == other.connection_origin
        )

    def __hash__(self):
        hash_str = "{}_to_{}".format(
            self.destiny_section_name, self.connection_origin
        )
        return sum([
            ord(hash_str[idx]) * idx
            for idx in range(len(hash_str))
        ])

    def __cmp__(self, other):
        return object.__cmp__(self, other)
