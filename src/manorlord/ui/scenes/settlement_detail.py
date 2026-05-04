from __future__ import annotations

import pygame

from manorlord.config import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_TEXT_DIM,
    HUD_HEIGHT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SIDEBAR_WIDTH,
)
from manorlord.ui.scene import Scene
from manorlord.ui.widgets import Button, Label, Panel


SIDEBAR_X = SCREEN_WIDTH - SIDEBAR_WIDTH

_KIND_NAMES = {
    "capital": "主城",
    "town": "城镇",
    "village": "村庄",
}


class SettlementDetailScene(Scene):
    def __init__(self, manager: "SceneManager", settlement_id: int) -> None:
        super().__init__(manager)
        self.settlement_id = settlement_id

    def on_enter(self) -> None:
        self.hud_panel = Panel(pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT))
        self.sidebar_panel = Panel(
            pygame.Rect(SIDEBAR_X, HUD_HEIGHT, SIDEBAR_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT),
        )

        self.back_button = Button(
            pygame.Rect(SCREEN_WIDTH - 160, 30, 130, 50),
            "返回",
            self.theme.body,
            self._back,
        )

        self._refresh_content()

    def _back(self) -> None:
        from manorlord.ui.scenes.map_view import MapViewScene

        self.manager.change_scene(MapViewScene(self.manager))

    def _refresh_content(self) -> None:
        if self.state is None:
            self.content_lines: list[Label] = []
            return

        settlement = self.state.settlements.get(self.settlement_id)
        if settlement is None:
            self.content_lines = [Label("未知聚落", self.theme.heading, color=COLOR_ACCENT, topleft=(40, 30))]
            return

        realm = self.state.realms.get(settlement.realm_id)
        province = self.state.provinces.get(settlement.province_id)
        lord = self.state.characters.get(realm.owner_id) if realm else None

        x = 60
        y = HUD_HEIGHT + 40
        lines: list[Label] = []

        lines.append(Label(settlement.name, self.theme.heading, color=COLOR_ACCENT, topleft=(x, y)))
        y += 60

        kind_label = _KIND_NAMES.get(settlement.kind, settlement.kind)
        lines.append(Label(f"类型：{kind_label}", self.theme.subheading, topleft=(x, y)))
        y += 50

        if realm is not None:
            lines.append(Label(f"领地：{realm.name}", self.theme.body, topleft=(x, y)))
            y += 40
        if province is not None:
            lines.append(Label(f"省份：{province.name} — {province.terrain}", self.theme.body, topleft=(x, y)))
            y += 40

        lines.append(Label(f"人口：{settlement.population}", self.theme.body, topleft=(x, y)))
        y += 40

        if lord is not None:
            lines.append(Label(f"统治者：{lord.title.display_name}{lord.full_name}", self.theme.body, color=COLOR_TEXT_DIM, topleft=(x, y)))
            y += 36

        y += 20
        desc = self._flavor_text(settlement, province)
        for sentence in desc.split("。"):
            sentence = sentence.strip()
            if not sentence:
                continue
            if not sentence.endswith("。"):
                sentence += "。"
            for wrapped in self._wrap(sentence, 55):
                lines.append(Label(wrapped, self.theme.body, color=COLOR_TEXT_DIM, topleft=(x, y)))
                y += 32

        self.content_lines = lines

    @staticmethod
    def _flavor_text(settlement, province) -> str:
        terrain = province.terrain if province else "未知"
        kind = settlement.kind
        flavor_map: dict[str, dict[str, str]] = {
            "capital": {
                "平原": "主城大道上车水马龙，商贾与信使往来不绝。",
                "山地": "石墙从山腰拔起，庇护着这片领地的权力中枢。",
                "森林": " timber 厅堂与雕刻大门标志着林地王国的心脏。",
                "丘陵": "层层梯田花园环绕山顶，四面八方皆可视。",
                "海岸": "海港钟声穿过盐渍街道，船只停靠在主城码头。",
                "沼泽": "架高的栈道连接着这座潮湿却易守难攻的主城。",
                "湖泊": "水门与运河桥梁纵横交错，水城风采尽显。",
                "城邦": "石塔与玻璃穹顶耸立在拥挤的集市广场之上。",
            },
            "town": {
                "平原": "一座不起眼的贸易站，收割季节前粮车汇聚于此。",
                "山地": "矿工的提灯在石头仓库之间的狭窄巷弄里闪烁。",
                "森林": "伐木营将最好的 timber 运经这座宁静的林间小镇。",
                "丘陵": "羊群集市与染缸为这座山坡小镇染上斑斓色彩。",
                "海岸": "家家户户门前晾着渔网，在海风中飘舞。",
                "沼泽": "芦苇屋顶与沼泽铁匠铺赋予这座小镇坚韧的性格。",
                "湖泊": "造船匠与织网人维系着平静的湖上贸易。",
                "城邦": "工匠与商人密集的街区，作坊烟雾缭绕。",
            },
            "village": {
                "平原": "低矮的茅屋簇拥在几亩田地之间。",
                "山地": "层层羊圈攀附在陡坡之上，石屋点缀其间。",
                "森林": "炭窑与猎户小屋隐匿于树林深处。",
                "丘陵": "羊群小径在比任何活人记忆都古老的石墙之间蜿蜒。",
                "海岸": "几艘小船拖上岸，饱经风霜的手修补着渔网。",
                "沼泽": "高脚茅屋矗立在古旧木桩之上，凌驾于泥泞之上。",
                "湖泊": "芦苇篮与干鱼悬挂在每座屋檐下。",
                "城邦": "狭窄的巷道与共享庭院隐藏在宽阔大道背后。",
            },
        }
        return flavor_map.get(kind, flavor_map["village"]).get(terrain, "一座宁静的聚落，鲜为旅人所知。")

    @staticmethod
    def _wrap(text: str, width: int) -> list[str]:
        words = text.split()
        result: list[str] = []
        current: list[str] = []
        length = 0
        for word in words:
            extra = len(word) + (1 if current else 0)
            if length + extra > width:
                result.append(" ".join(current))
                current = [word]
                length = len(word)
            else:
                current.append(word)
                length += extra
        if current:
            result.append(" ".join(current))
        return result

    def handle_event(self, event: pygame.event.Event) -> None:
        self.back_button.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)
        self.hud_panel.draw(surface)
        self.sidebar_panel.draw(surface)
        for line in self.content_lines:
            line.draw(surface)
        self.back_button.draw(surface)
