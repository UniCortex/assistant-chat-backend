from dishka import Provider, Scope, provide

from app.setup.config.settings import AppSettings


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def app_settings(self) -> AppSettings:
        return AppSettings()
