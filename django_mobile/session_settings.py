from conf import SettingsProxy, settings as django_mobile_settings

class SessionDefaultSettings:
    FLAVOURS_SESSION_KEY = 'flavour'

settings = SettingsProxy(django_mobile_settings, SessionDefaultSettings)