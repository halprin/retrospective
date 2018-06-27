from pynamodb.attributes import UnicodeAttribute, ListAttribute, MapAttribute
from backend.api.models import Retrospective, RetroStepBase, IssueAttribute


class RetroStepV2(RetroStepBase):
    ADDING_ISSUES = 'Adding Issues'
    GROUPING = 'Grouping'
    VOTING = 'Voting'
    RESULTS = 'Results'


class GroupAttribute(MapAttribute):
    id = UnicodeAttribute()
    title = UnicodeAttribute()
    section = UnicodeAttribute()


class IssueAttributeV2(IssueAttribute):
    group = UnicodeAttribute()


class RetrospectiveV2(Retrospective):
    issues = ListAttribute(of=IssueAttributeV2)
    groups = ListAttribute(of=GroupAttribute)
    version = UnicodeAttribute()
