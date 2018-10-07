from pynamodb.attributes import UnicodeAttribute, ListAttribute, MapAttribute, UnicodeSetAttribute
from backend.api.models import Retrospective, RetroStepBase, IssueAttribute
import os


ENVIRONMENT = os.getenv('ENVIRONMENT', 'test')


class RetroStepV2(RetroStepBase):
    ADDING_ISSUES = 'Adding Issues'
    GROUPING = 'Grouping'
    VOTING = 'Voting'
    RESULTS = 'Results'


class GroupAttribute(MapAttribute):
    id = UnicodeAttribute()
    title = UnicodeAttribute()
    section = UnicodeAttribute()
    votes = UnicodeSetAttribute()


class IssueAttributeV2(IssueAttribute):
    group = UnicodeAttribute()


class RetrospectiveV2(Retrospective):
    class Meta:
        table_name = 'retrospective-{}'.format(ENVIRONMENT)
        if ENVIRONMENT == 'test':
            host = "http://localhost:8008"
    issues = ListAttribute(of=IssueAttributeV2)
    groups = ListAttribute(of=GroupAttribute)
    version = UnicodeAttribute()
