from enum import StrEnum
from typing import Optional, Union
from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class LocalizedStrings(APIModel):
    en_US: Optional[str] = None
    es_MX: Optional[str] = None
    pt_BR: Optional[str] = None
    en_GB: Optional[str] = None
    es_ES: Optional[str] = None
    fr_FR: Optional[str] = None
    ru_RU: Optional[str] = None
    de_DE: Optional[str] = None
    pt_PT: Optional[str] = None
    it_IT: Optional[str] = None
    ko_KR: Optional[str] = None
    zh_TW: Optional[str] = None
    zh_CN: Optional[str] = None


type APIString = Union[LocalizedStrings, str]


class GenderedString(APIModel):
    male: APIString
    female: APIString


class Href(APIModel):
    href: str


class Ref(APIModel):
    key: Href
    id: int
    name: Optional[APIString] = None


class Color(APIModel):
    r: int
    g: int
    b: int
    a: int


class ValueWithDisplayString(APIModel):
    value: Union[int, float]
    display_string: APIString


class EnumType(APIModel):
    type: str
    name: APIString


class Achievement(APIModel):
    id: int
    category: Ref
    name: APIString
    description: APIString
    points: int
    is_account_wide: bool
    media: Ref
    display_order: int


class Title(APIModel):
    id: int
    name: APIString
    gender_name: GenderedString


class ItemWeaponDamage(APIModel):
    min_value: int
    max_value: int
    display_string: APIString
    damage_class: EnumType


class ItemWeaponStats(APIModel):
    damage: ItemWeaponDamage
    attack_speed: ValueWithDisplayString
    dps: ValueWithDisplayString


class ItemStatDisplay(APIModel):
    display_string: APIString
    color: Color


class ItemStat(APIModel):
    type: EnumType
    value: int
    display: ItemStatDisplay
    is_negated: Optional[bool] = None


class ItemSpell(APIModel):
    spell: Ref
    description: APIString


class ItemRequirements(APIModel):
    level: ValueWithDisplayString


class ItemPreview(APIModel):
    item: Ref
    quality: EnumType
    name: APIString
    media: Ref
    item_class: Ref
    item_subclass: Ref
    inventory_type: EnumType
    binding: EnumType
    unique_equipped: Optional[APIString] = None
    weapon: Optional[ItemWeaponStats] = None
    stats: Optional[list[ItemStat]] = None
    spells: Optional[list[ItemSpell]] = None
    requirements: Optional[ItemRequirements] = None
    level: Optional[ValueWithDisplayString] = None
    durability: Optional[ValueWithDisplayString] = None
    context: Optional[int] = None
    bonus_list: Optional[list[int]] = None


class Item(APIModel):
    id: int
    name: APIString
    quality: EnumType
    level: int
    required_level: int
    media: Ref
    item_class: Ref
    item_subclass: Ref
    inventory_type: EnumType
    purchase_price: int
    sell_price: int
    max_count: int
    is_equippable: bool
    is_stackable: bool
    preview_item: ItemPreview
    purchase_quantity: int
    appearances: Optional[list[Ref]] = None


class MountRequirements(APIModel):
    faction: EnumType


class Mount(APIModel):
    id: int
    name: APIString
    creature_displays: list[Ref]
    description: APIString
    source: EnumType
    faction: EnumType
    Requirements: MountRequirements


class QuestRequirements(APIModel):
    min_character_level: int
    max_character_level: int
    faction: EnumType


class QuestReputationReward(APIModel):
    reward: Ref
    value: int


class QuestMoneyUnits(APIModel):
    gold: int
    silver: int
    copper: int


class QuestMoneyReward(APIModel):
    value: int
    units: QuestMoneyUnits


class QuestRewards(APIModel):
    experience: int
    money: QuestMoneyReward
    reputations: Optional[list[QuestReputationReward]] = None


class Quest(APIModel):
    id: int
    title: APIString
    area: Ref
    description: APIString
    rewards: QuestRewards


class QuestCategory(APIModel):
    id: int
    category: APIString
    quests: list[Ref]


class QuestArea(APIModel):
    id: int
    area: APIString
    quests: list[Ref]


class QuestType(APIModel):
    id: int
    type: APIString
    quests: list[Ref]


class Realm(APIModel):
    id: int
    region: Ref
    connected_realm: Href
    name: APIString
    category: APIString
    locale: str
    timezone: str
    type: EnumType
    is_tournament: bool
    slug: str
