from enum import StrEnum

from bnet import __version__

APP_NAME = "bnet-ghst"

USER_AGENT = f"{APP_NAME}/{__version__} (ghost@ghst.tools)"


class BattleNetRegion(StrEnum):
    US = "us"
    EU = "eu"
    KR = "kr"
    TW = "tw"
    CN = "cn"


class BattleNetLocale(StrEnum):
    en_US = "en_US"
    es_MX = "es_MX"
    pt_BR = "pt_BR"
    en_GB = "en_GB"
    es_ES = "es_ES"
    fr_FR = "fr_FR"
    ru_RU = "ru_RU"
    de_DE = "de_DE"
    pt_PT = "pt_PT"
    it_IT = "it_IT"
    ko_KR = "ko_KR"
    zh_TW = "zh_TW"
    zh_CN = "zh_CN"


AVAILABLE_LOCALES_PER_REGION = {
    BattleNetRegion.US: {
        BattleNetLocale.en_US,
        BattleNetLocale.es_MX,
        BattleNetLocale.pt_BR,
    },
    BattleNetRegion.EU: {
        BattleNetLocale.en_GB,
        BattleNetLocale.es_ES,
        BattleNetLocale.fr_FR,
        BattleNetLocale.ru_RU,
        BattleNetLocale.de_DE,
        BattleNetLocale.pt_PT,
        BattleNetLocale.it_IT,
    },
    BattleNetRegion.KR: {BattleNetLocale.ko_KR},
    BattleNetRegion.TW: {BattleNetLocale.zh_TW},
    BattleNetRegion.CN: {BattleNetLocale.zh_CN},
}


class BattleNetNamespaceType(StrEnum):
    Static = "static"
    Dynamic = "dynamic"
    Profile = "profile"


class ClassicWarcraftNamespace(StrEnum):
    Classic = "classic"
    ClassicEra = "classic1x"
    ClassicAnniversary = "classicann"
