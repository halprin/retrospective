from .views import RetroView, RetroUserView
from .generic_views import VersionServiceView
from ..serviceV2 import ServiceV2


class Version2ServiceView(VersionServiceView):
    @staticmethod
    def service():
        return ServiceV2


class RetroViewV2(Version2ServiceView, RetroView):
    pass


class RetroUserViewV2(Version2ServiceView, RetroUserView):
    pass
