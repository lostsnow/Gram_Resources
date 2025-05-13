import typing
from functools import partial
from os import path
from typing import List, Dict

import bs4

from impl.config import config
from impl.core._abstract_spider import BaseSpider, RequestClient
from impl.core.file_manager import FileManager
from impl.models.base import BaseWikiModel
from impl.models.enums import Game, DataType
from impl.models.genshin.daily_material import MaterialsData, AreaDailyMaterialsData, DOMAIN_AREA_MAP, DOMAIN_TYPE_MAP

FILE_PATH = "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/{PATH}"
DATA_FILES = """
ExcelBinOutput/AvatarExcelConfigData.json
ExcelBinOutput/AvatarPromoteExcelConfigData.json
ExcelBinOutput/AvatarSkillDepotExcelConfigData.json
ExcelBinOutput/AvatarSkillExcelConfigData.json
ExcelBinOutput/MaterialExcelConfigData.json
ExcelBinOutput/ProudSkillExcelConfigData.json
TextMap/TextMapCHS.json
TextMap/TextMapCHT.json
TextMap/TextMapDE.json
TextMap/TextMapEN.json
TextMap/TextMapES.json
TextMap/TextMapFR.json
TextMap/TextMapIT.json
TextMap/TextMapJP.json
TextMap/TextMapKR.json
TextMap/TextMapPT.json
TextMap/TextMapRU.json
TextMap/TextMapTH_0.json
TextMap/TextMapTH_1.json
TextMap/TextMapTR.json
TextMap/TextMapVI.json
""".strip()
KEYS_MAP = {
    "id": "ELKKIAIGOBK",
    "nameTextMapHash": "DNINKKHEILA",
    "descTextMapHash": "PGEPICIANFN",
    # AvatarSkillExcelConfigData
    "skillIcon": "BGIHPNEDFOL",
    "forceCanDoSkill": "CFAICKLGPDP",
    "costElemType": "PNIDLNBBJIC",
    "proudSkillGroupId": "DGIJCGLPDPI",
    # AvatarTalentExcelConfigData
    "talentId": "JFALAEEKFMI",
    "icon": "CNPCNIGHGJJ",
    # ReliquaryExcelConfigData
    "itemType": "CEBMMGCMIJM",
    "equipType": "HNCDIADOINL",
    "rankLevel": "IMNCLIODOBL",
    "mainPropDepotId": "AIPPMEGLAKJ",
    "appendPropDepotId": "GIFPAPLPMGO",
    # EquipAffixExcelConfigData
    "affixId": "NEMBIFHOIKM",
    "openConfig": "JIPJEMFCKAI",
    # ReliquaryMainPropExcelConfigData
    # ReliquaryAffixExcelConfigData
    "propType": "JJNPGPFNJHP",
    "propValue": "AGDCHCBAGFO",
    # WeaponExcelConfigData
    "awakenIcon": "KMOCENBGOEM",
    # MaterialExcelConfigData
    "materialType": "HBBILKOGMIP",
    "picPath": "PPCKMKGIIMP",
    # ManualTextMapConfigData
    "textMapId": "EHLGDOCBKBO",
    "textMapContentTextMapHash": "ECIGIIKPLGD",
    # ProfilePictureExcelConfigData
    "iconPath": "FPPENJGNALC",
    # AvatarSkillDepotExcelConfigData
    "skills": "CBJGLADMBHG",
    "energySkill": "GIEFGHHKGDD",
    "talents": "IAGMADCJGIA",
    # AvatarExcelConfigData
    "iconName": "OCNPJGGMLLO",
    "sideIconName": "IPNPPIGGOPB",
    "qualityType": "ADLDGBEKECJ",
    "skillDepotId": "HCBILEOPKHD",
    "candSkillDepotIds": "FOCOLMLMEFN",
    "featureTagGroupID": "EOCNJBDLDMK",
    "avatarPromoteId": "ECMKJJIDKAE",
    # AvatarPromoteExcelConfigData
    "costItems": "FPIJIIENLBP",
    "promoteLevel": "AKPHFJACMIB",
    # ProudSkillExcelConfigData
    "level": "BHFAPOEDIDB",
}


def fix_map(data: str) -> str:
    for k, v in KEYS_MAP.items():
        data = data.replace(f'"{v}":', f'"{k}":')
    return data


class GenshinRoleMaterialSpider(BaseSpider):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.OTHER
    data_source: str = "data"

    def __init__(self):
        super().__init__()
        save_path = partial(
            FileManager.get_raw_icon_path, game=self.game, data_type=self.data_type, data_source=self.data_source
        )
        self.avatar_data_path = save_path("AvatarExcelConfigData.json")
        self.avatar_promote_data_path = save_path("AvatarPromoteExcelConfigData.json")
        self.avatar_skill_depot_data_path = save_path("AvatarSkillDepotExcelConfigData.json")
        self.avatar_skill_data_path = save_path("AvatarSkillExcelConfigData.json")
        self.proud_skill_data_path = save_path("ProudSkillExcelConfigData.json")
        self.material_data_path = save_path("MaterialExcelConfigData.json")
        self.material_data: Dict[str, str] = {}
        self.zh_lang_path = save_path("TextMap/TextMapCHS.json")
        self.zh_lang = {}
        self.avatar_promote_data: Dict[str, str] = {}
        self.skill_depot_map: Dict[str, int] = {}
        """
        开发备忘：

        avatar_promote_data_path 是角色升级数据，里面包含了角色升级所需的素材消耗信息
        avatar_promote_data 是角色名称 -> avatarPromoteId 的 map

        avatar_skill_depot_data_path 是一个角色 id -> 天赋 id 的 map，不包含天赋信息
        skill_depot_map 是角色 id -> 主天赋 id 的 map
        avatar_skill_data_path 是天赋基础信息，不包含天赋消耗信息，需要进一步通过 proudSkillGroupId 请求
        proud_skill_data_path 是天赋详细信息，包含了素材消耗信息

        material_data_path 是 item 信息
        material_data 是 id -> name 的 map
        zh_lang_path 是中文文本信息
        """
        self.data = {"status": 0, "data": {}}

    async def _download_file(self, url: str) -> str:
        response = await RequestClient.request("GET", url)
        c = fix_map(response.text.replace("\r\n", "\n")).encode("utf-8")
        return await FileManager.save_raw_icon(url, self.game, self.data_type, self.data_source, c)

    async def download_data_file(self):
        tasks = [self._download_file(FILE_PATH.format(PATH=p.strip())) for p in DATA_FILES.split("\n")]
        await self.gather_tasks(tasks)

    async def get_name_list(self):
        ignore_name_list = ["旅行者"]
        name_list = []
        avatar_data = await FileManager.load_json(self.avatar_data_path)
        for avatar in avatar_data:
            if avatar["featureTagGroupID"] == 10000001:
                # 未上线角色
                continue
            avatar_name = self.zh_lang[str(avatar["nameTextMapHash"])]
            if avatar_name not in ignore_name_list and avatar_name not in name_list:
                name_list.append(avatar_name)
                self.avatar_promote_data[avatar_name] = avatar["avatarPromoteId"]
                self.skill_depot_map[avatar_name] = avatar["skillDepotId"]
                self.data["data"][avatar_name] = {}
        return name_list

    async def load_material_data(self):
        _material_data = await FileManager.load_json(self.material_data_path)
        for material in _material_data:
            try:
                self.material_data[material["id"]] = self.zh_lang[str(material["nameTextMapHash"])]
            except KeyError:
                pass

    async def get_up_data(self):
        _avatar_promote_data = await FileManager.load_json(self.avatar_promote_data_path)
        data_map: Dict[str, Dict] = {}
        data_material_map: Dict[str, List[str]] = {}
        for avatar in _avatar_promote_data:
            pid = avatar["avatarPromoteId"]
            cos = avatar.get("costItems", [])
            if len(cos) != 4:
                continue
            for i in cos[2:]:
                if not i:
                    continue
                t_list = data_material_map.get(pid, [])
                if i["id"] not in t_list:
                    t_list.append(i["id"])
                    data_material_map[pid] = t_list

            if avatar.get("promoteLevel") != 6:
                continue
            data_map[avatar["avatarPromoteId"]] = avatar
            data_material_map.get(pid, []).sort()
        for avatar in self.avatar_promote_data.keys():
            pid = self.avatar_promote_data[avatar]
            t = data_map[pid]
            self.data["data"][avatar]["ascension_materials"] = self.material_data[t["costItems"][0]["id"]]
            self.data["data"][avatar]["level_up_materials"] = self.material_data[t["costItems"][1]["id"]]
            self.data["data"][avatar]["materials"] = [self.material_data[i] for i in data_material_map[pid] if i]

    async def load_avatar_skill_depot_data(self) -> Dict[int, int]:
        _avatar_skill_depot_data = await FileManager.load_json(self.avatar_skill_depot_data_path)
        energy_skill_map: Dict[int, int] = {}
        for _avatar in _avatar_skill_depot_data:
            if "energySkill" not in _avatar:
                continue
            energy_skill_map[_avatar["id"]] = _avatar["energySkill"]
        return energy_skill_map

    async def load_avatar_skill_data(self) -> Dict[int, int]:
        _avatar_skill_data = await FileManager.load_json(self.avatar_skill_data_path)
        avatar_skill_map: Dict[int, int] = {}
        for _avatar in _avatar_skill_data:
            if "proudSkillGroupId" not in _avatar:
                continue
            avatar_skill_map[_avatar["id"]] = _avatar["proudSkillGroupId"]
        return avatar_skill_map

    async def load_proud_skill_data(self) -> Dict[int, List[str]]:
        _proud_skill_data = await FileManager.load_json(self.proud_skill_data_path)
        proud_skill_map: Dict[int, List[str]] = {}
        for _avatar in _proud_skill_data:
            if _avatar["level"] != 10:
                continue
            key = _avatar["proudSkillGroupId"]
            cos = _avatar["costItems"]
            value = [self.material_data[cos[0]["id"]][1:3], self.material_data[cos[2]["id"]]]
            proud_skill_map[key] = value
        return proud_skill_map

    async def get_skill_data(self):
        energy_skill_map = await self.load_avatar_skill_depot_data()
        avatar_skill_map = await self.load_avatar_skill_data()
        proud_skill_map = await self.load_proud_skill_data()
        for avatar in self.skill_depot_map.keys():
            depot_id = self.skill_depot_map[avatar]
            skill_id = energy_skill_map[depot_id]
            skill_group_id = avatar_skill_map[skill_id]
            self.data["data"][avatar]["talent"] = proud_skill_map[skill_group_id]

    async def get_material_data(self):
        await self.get_name_list()
        await self.load_material_data()
        await self.get_up_data()
        await self.get_skill_data()
        await FileManager.save_data_file(self.game, self.data_type, self.data, "roles_material")

    async def initialize(self):
        if not config.GENSHIN:
            return
        print("Download raw file")
        await self.download_data_file()
        print("Download raw file success")
        self.zh_lang = await FileManager.load_json(self.zh_lang_path)
        await self.get_material_data()

    async def start_crawl(self) -> List[BaseWikiModel]:
        pass


class GenshinDailyMaterialSpider(BaseSpider):
    game: "Game" = Game.GENSHIN
    data_type: "DataType" = DataType.OTHER
    data_source: str = "data"

    def __init__(self):
        self.material_ids_map: Dict[str, str] = {}

    async def get_honey_impact_material_name(self, material_id: str) -> str:
        url = f"https://gensh.honeyhunterworld.com/tooltip.php?id={material_id}&lang=chs"
        response = await RequestClient.request("POST", url)
        soup = bs4.BeautifulSoup(response.content, "lxml")
        name = soup.find("h2").text.strip()
        self.material_ids_map[material_id] = name
        return name

    @staticmethod
    async def _parse_honey_impact_source() -> MaterialsData:
        """
        ## honeyimpact 的源码格式:
        ```html
        <div class="calendar_day_wrap">
          <!-- span 里记录秘境和对应突破素材 -->
          <span class="item_secondary_title">
            <a href="">秘境名<img src="" /></a>
            <div data-days="0"> <!-- data-days 记录星期几 -->
              <a href=""><img src="" /></a> <!-- 「某某」的教导，ID 在 href 中 -->
              <a href=""><img src="" /></a> <!-- 「某某」的指引，ID 在 href 中 -->
              <a href=""><img src="" /></a> <!-- 「某某」的哲学，ID 在 href 中 -->
            </div>
            <div data-days="1"><!-- 同上，但是星期二 --></div>
            <div data-days="2"><!-- 同上，但是星期三 --></div>
            <div data-days="3"><!-- 同上，但是星期四 --></div>
            <div data-days="4"><!-- 同上，但是星期五 --></div>
            <div data-days="5"><!-- 同上，但是星期六 --></div>
            <div data-days="6"><!-- 同上，但是星期日 --></div>
          <span>
          <!-- 这里开始是该秘境下所有可以刷的角色或武器的详细信息 -->
          <!-- 注意这个 a 和上面的 span 在 DOM 中是同级的 -->
          <a href="">
            <!-- data-days 储存可以刷素材的星期几，如 146 指的是 周二/周五/周日 -->
            <div data-assign="char_编号" data-days="146" class="calendar_pic_wrap">
              <img src="" /> <!-- Item ID 在此 -->
              <span> 角色名 </span> <!-- 角色名周围的空格是切实存在的 -->
            </div>
            <!-- 以此类推，该国家所有角色都会被列出 -->
          </a>
          <!-- 炼武秘境格式和精通秘境一样，也是先 span 后 a，会把所有素材都列出来 -->
        </div>
        ```
        """
        response = await RequestClient.request("GET", "https://gensh.honeyhunterworld.com/?lang=CHS")
        calendar = bs4.BeautifulSoup(response.text, "lxml").select_one(".calendar_day_wrap")
        if calendar is None:
            return MaterialsData()  # 多半是格式错误或者网页数据有误
        everyday_materials: List[Dict[str, "AreaDailyMaterialsData"]] = [{} for _ in range(7)]
        current_country: str = ""
        for element in calendar.find_all(recursive=False):
            element: bs4.Tag
            if element.name == "span":  # 找到代表秘境的 span
                domain_name = next(iter(element)).text  # 第一个孩子节点的 text
                current_country = DOMAIN_AREA_MAP[domain_name]  # 后续处理 a 列表也会用到这个 current_country
                materials_type = f"{DOMAIN_TYPE_MAP[domain_name]}_materials"
                for div in element.find_all("div", recursive=False):  # 7 个 div 对应的是一周中的每一天
                    div: bs4.Tag
                    weekday = int(div.attrs["data-days"])  # data-days 是一周中的第几天（周一 0，周日 6）
                    if current_country not in everyday_materials[weekday]:
                        everyday_materials[weekday][current_country] = AreaDailyMaterialsData()
                    materials: List[str] = getattr(everyday_materials[weekday][current_country], materials_type)
                    for a in div.find_all("a", recursive=False):  # 当天能刷的所有素材在 a 列表中
                        a: bs4.Tag
                        href = a.attrs["href"]  # 素材 ID 在 href 中
                        honey_url = path.dirname(href).removeprefix("/")
                        materials.append(honey_url)
            if element.name == "a":
                # country_name 是从上面的 span 继承下来的，下面的 item 对应的是角色或者武器
                # element 的第一个 child，也就是 div.calendar_pic_wrap
                calendar_pic_wrap = typing.cast(bs4.Tag, next(iter(element)))  # element 的第一个孩子
                item_name_span = calendar_pic_wrap.select_one("span")
                if item_name_span is None or item_name_span.text.strip() == "旅行者":
                    continue  # 因为旅行者的天赋计算比较复杂，不做旅行者的天赋计算
                # data-assign 的数字就是 Item ID
                data_assign = calendar_pic_wrap.attrs["data-assign"]
                item_is_weapon = data_assign.startswith("weapon_")
                item_id = "".join(filter(str.isdigit, data_assign))
                for weekday in map(int, calendar_pic_wrap.attrs["data-days"]):  # data-days 中存的是星期几可以刷素材
                    ascendable_items = everyday_materials[weekday][current_country]
                    ascendable_items = ascendable_items.weapon if item_is_weapon else ascendable_items.avatar
                    ascendable_items.append(item_id)
        return MaterialsData.model_validate(everyday_materials)

    async def fix_honey_material_id(self, data: MaterialsData):
        material_ids = []
        for weekday in data.root:
            for country, area_data in weekday.items():
                for i in range(2):
                    if i == 0:
                        materials = area_data.avatar_materials
                    else:
                        materials = area_data.weapon_materials
                    material_ids.extend(materials)
        material_ids_only = list(set(material_ids))
        tasks = [self.get_honey_impact_material_name(i) for i in material_ids_only]
        await self.gather_tasks(tasks)
        for weekday in data.root:
            for country, area_data in weekday.items():
                for i in range(2):
                    if i == 0:
                        materials = area_data.avatar_materials
                    else:
                        materials = area_data.weapon_materials
                    new_data = [self.material_ids_map.get(i, i) for i in materials]
                    materials.clear()
                    materials.extend(new_data)

    async def initialize(self):
        if not config.GENSHIN:
            return
        print("parse_honey_impact_source")
        data = await self._parse_honey_impact_source()
        await self.fix_honey_material_id(data)
        await FileManager.save_data_file(self.game, self.data_type, data.model_dump(), "daily_material")

    async def start_crawl(self) -> List[BaseWikiModel]:
        pass
