from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, ListAttribute, MapAttribute, BooleanAttribute, UnicodeSetAttribute
from enum import Enum


class RetroStep(Enum):
    ADDING_ISSUES = 'Adding Issues'
    VOTING = 'Voting'
    RESULTS = 'Results'

    def next(self):
        cls = self.__class__
        members = list(cls)
        next_index = members.index(self) + 1
        if next_index >= len(members):
            raise ValueError('No next step after {}'.format(members[next_index - 1]))
        return members[next_index]

    def previous(self):
        cls = self.__class__
        members = list(cls)
        previous_index = members.index(self) - 1
        if previous_index < 0:
            raise ValueError('No previous step before {}'.format(members[previous_index + 1]))
        return members[previous_index]


class IssueAttribute(MapAttribute):
    id = UnicodeAttribute()
    title = UnicodeAttribute()
    section = UnicodeAttribute()
    creator_token = UnicodeAttribute()
    votes = UnicodeSetAttribute()


class ParticipantAttribute(MapAttribute):
    name = UnicodeAttribute()
    ready = BooleanAttribute()
    admin = BooleanAttribute()
    token = UnicodeAttribute()


class Retrospective(Model):
    class Meta:
        table_name = "retrospective"
        host = "http://localhost:8008"
    id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    current_step = UnicodeAttribute()
    issues = ListAttribute(of=IssueAttribute)
    participants = ListAttribute(of=ParticipantAttribute)
