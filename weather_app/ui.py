from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config import (
    add_saved_city,
    get_credential_id,
    get_api_host,
    get_project_id,
    get_saved_cities,
    load_config,
    read_private_key,
    remove_saved_city,
    save_config,
)
from weather_app.api import QWeatherClient
from weather_app.flowlayout import FlowLayout
from weather_app.models import City, ForecastDay, WeatherData, get_icon

THEMES = {
    "dark": {
        "window_bg": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0a18, stop:1 #10102a)",
        "text": "#f0f0f0",
        "text_sec": "#ccc",
        "text_muted": "#aaa",
        "text_dim": "#777",
        "card_bg": "rgba(255,255,255,0.04)",
        "card_border": "#2a2a3e",
        "btn_bg": "#1a3a6a",
        "btn_hover": "#1e4a8a",
        "btn_pressed": "#0f3460",
        "input_bg": "rgba(255,255,255,0.08)",
        "input_border": "#2a2a3e",
        "dropdown_bg": "#14142a",
        "msg_bg": "#14142a",
        "status_bg": "rgba(0,0,0,0.4)",
        "status_text": "#aaa",
        "saved_bg": "rgba(255,255,255,0.06)",
        "saved_border": "#2a2a3e",
        "saved_text": "#ccc",
        "saved_del": "#555",
        "saved_del_hover": "#e04040",
        "dialog_bg": "#14142a",
        "list_bg": "rgba(255,255,255,0.04)",
        "list_border": "#2a2a3e",
        "list_hover": "rgba(255,255,255,0.06)",
        "list_sel": "#1a3a6a",
        "fc_text": "#999",
        "aqi_label": "#ccc",
    },
    "light": {
        "window_bg": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f0f4f8, stop:1 #e2e8f0)",
        "text": "#1a1a2e",
        "text_sec": "#334",
        "text_muted": "#555",
        "text_dim": "#888",
        "card_bg": "rgba(255,255,255,0.7)",
        "card_border": "#d0d6e0",
        "btn_bg": "#3b82f6",
        "btn_hover": "#2563eb",
        "btn_pressed": "#1d4ed8",
        "input_bg": "rgba(255,255,255,0.9)",
        "input_border": "#c8ced8",
        "dropdown_bg": "#fff",
        "msg_bg": "#fff",
        "status_bg": "rgba(0,0,0,0.04)",
        "status_text": "#666",
        "saved_bg": "rgba(255,255,255,0.6)",
        "saved_border": "#c8ced8",
        "saved_text": "#1a1a2e",
        "saved_del": "#999",
        "saved_del_hover": "#d04040",
        "dialog_bg": "#fff",
        "list_bg": "#fff",
        "list_border": "#c8ced8",
        "list_hover": "#e8ecf4",
        "list_sel": "#dbeafe",
        "fc_text": "#777",
        "aqi_label": "#555",
    },
}


def _global_ss(t):
    return f"""
    QMainWindow {{ background: {t["window_bg"]}; }}
    QLabel {{ color: {t["text"]}; }}
    QPushButton {{
        background: {t["btn_bg"]}; color: #fff; border: none;
        border-radius: 6px; padding: 8px 18px; font-size: 14px;
    }}
    QPushButton:hover {{ background: {t["btn_hover"]}; }}
    QPushButton:pressed {{ background: {t["btn_pressed"]}; }}
    QLineEdit, QComboBox {{
        background: {t["input_bg"]}; color: {t["text"]}; border: 1px solid {t["input_border"]};
        border-radius: 6px; padding: 8px 12px; font-size: 14px;
    }}
    QComboBox::drop-down {{ border: none; width: 0px; }}
    QComboBox QAbstractItemView {{
        background: {t["dropdown_bg"]}; color: {t["text"]};
        selection-background-color: {t["btn_bg"]}; border: 1px solid {t["input_border"]}; outline: none;
    }}
    QMessageBox {{ background: {t["msg_bg"]}; color: {t["text"]}; }}
    QMessageBox QLabel {{ color: {t["text"]}; }}
    QMessageBox QPushButton {{ background: {t["btn_bg"]}; color: #fff; min-width: 80px; }}
    QStatusBar {{ background: {t["status_bg"]}; color: {t["status_text"]}; }}
    QListWidget {{
        background: {t["list_bg"]}; border: 1px solid {t["list_border"]};
        border-radius: 6px; color: {t["text"]}; font-size: 14px;
    }}
    QListWidget::item {{ padding: 8px 12px; }}
    QListWidget::item:hover {{ background: {t["list_hover"]}; }}
    QListWidget::item:selected {{ background: {t["list_sel"]}; color: {t["text"]}; }}
    """


class ForecastCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self._theme_ss = ""

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(12, 8, 12, 8)

        self.date_label = QLabel("--")
        self.date_label.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel("--")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 28px;")

        self.temp_label = QLabel("--")
        self.temp_label.setAlignment(Qt.AlignCenter)
        self.temp_label.setStyleSheet("font-size: 15px; font-weight: bold;")

        self.text_label = QLabel("")
        self.text_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.date_label)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.text_label)

    def apply_theme(self, t):
        self._theme_ss = t
        self.setStyleSheet(
            f"ForecastCard {{ background: {t['card_bg']}; border: 1px solid {t['card_border']}; border-radius: 8px; padding: 8px; }}"
        )
        self.date_label.setStyleSheet(f"font-size: 13px; color: {t['fc_text']};")
        self.text_label.setStyleSheet(f"font-size: 12px; color: {t['text_sec']};")

    def set_data(self, forecast, day_offset=None, label_override=None):
        date_str = getattr(forecast, "date", "") or ""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if label_override:
                label = label_override
            elif day_offset == 1:
                label = "今天"
            elif day_offset == 2:
                label = "明天"
            elif day_offset == 3:
                label = "后天"
            else:
                label = dt.strftime("%m/%d")
            date_part = f"{dt.month}月{dt.day}日"
        except (ValueError, AttributeError):
            label = label_override or date_str
            date_part = ""

        if day_offset and 1 <= day_offset <= 3:
            self.date_label.setStyleSheet(f"font-size: 16px; color: {self._theme_ss['fc_text']};")
        else:
            self.date_label.setStyleSheet(f"font-size: 13px; color: {self._theme_ss['fc_text']};")
        self.date_label.setText(f"{label} {date_part}")
        icon_code = forecast.icon_day
        self.icon_label.setText(get_icon(icon_code))
        self.temp_label.setText(f"{forecast.temp_max}° / {forecast.temp_min}°")
        self.text_label.setText(forecast.text_day)


class CityPickerDialog(QDialog):
    def __init__(self, cities: list[City], theme: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择城市")
        self.setMinimumWidth(380)
        self.selected_city: City | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        label = QLabel(f"找到 {len(cities)} 个匹配结果，请选择：")
        label.setStyleSheet(f"font-size: 14px; color: {theme['text']};")
        layout.addWidget(label)

        self.list_widget = QListWidget()
        for c in cities:
            parts = [c.name]
            if c.adm2 and c.adm2 != c.name:
                parts.append(c.adm2)
            if c.adm1:
                parts.append(c.adm1)
            item = QListWidgetItem(" - ".join(parts))
            item.setData(Qt.UserRole, cities.index(c))
            self.list_widget.addItem(item)

        self.list_widget.itemDoubleClicked.connect(self._accept)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self._accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self._cities = cities
        self.setStyleSheet(f"QDialog {{ background: {theme['dialog_bg']}; }}")

    def _accept(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.selected_city = self._cities[row]
            self.accept()
        else:
            QMessageBox.information(self, "提示", "请先选择一个城市")


class AboutDialog(QDialog):
    def __init__(self, theme: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 Checkitout Weather")
        self.setFixedSize(420, 260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        title = QLabel("☀ Checkitout Weather")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {theme['text']};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        ver = QLabel("v1.0.0")
        ver.setStyleSheet(f"font-size: 13px; color: {theme['text_muted']};")
        ver.setAlignment(Qt.AlignCenter)
        layout.addWidget(ver)

        layout.addSpacing(8)

        desc = QLabel("一款基于和风天气 API 的桌面天气应用。\n手动刷新（就是没有自动刷新功能，也不会做这个功能，减少 API 消耗），即查即知。")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 13px; color: {theme['text_sec']};")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        layout.addSpacing(8)

        link_label = QLabel(
            '<a href="https://github.com/hellodk34/checkitout_weather" '
            'style="color: #3b82f6; text-decoration: none;">'
            "github.com/hellodk34/checkitout_weather</a>"
        )
        link_label.setTextFormat(Qt.RichText)
        link_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        link_label.setOpenExternalLinks(True)
        link_label.setStyleSheet("font-size: 13px;")
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setCursor(Qt.PointingHandCursor)
        layout.addWidget(link_label)

        layout.addStretch()

        copy_label = QLabel("© 2026 hellodk34. MIT License.")
        copy_label.setStyleSheet(f"font-size: 11px; color: {theme['text_muted']};")
        copy_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copy_label)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setStyleSheet(f"QDialog {{ background: {theme['dialog_bg']}; }}")


class WeatherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Checkitout Weather")
        self.setMinimumSize(860, 660)
        self.resize(920, 780)

        self.client: QWeatherClient = None
        self.weather_data: WeatherData = None
        self._cached_cities: list[City] = []
        self._theme_name = load_config().get("app", {}).get("theme", "light")
        self._theme = THEMES.get(self._theme_name, THEMES["dark"])

        central = QWidget()
        self.setCentralWidget(central)
        self._build_ui(central)
        self._apply_theme(self._theme_name, persist=False)
        self._init_client()
        self._load_saved_cities()
        if self.client and get_saved_cities():
            self._load_saved_city(get_saved_cities()[0]["id"])

    def _apply_theme(self, name="light", persist=True):
        t = THEMES.get(name, THEMES["light"])
        self._theme = t
        self._theme_name = name

        self.setStyleSheet(_global_ss(t))
        self.current_frame.setStyleSheet(
            f"QFrame {{ background: {t['card_bg']}; border-radius: 12px; }}"
        )
        self.city_label.setStyleSheet(f"font-size: 14px; color: {t['text_sec']};")
        for lbl in self.detail_labels.values():
            lbl.setStyleSheet(f"font-size: 13px; color: {t['text_sec']};")
        self.sun_label.setStyleSheet(f"font-size: 13px; color: {t['text_sec']};")
        self.air_label.setStyleSheet(f"font-size: 13px; color: {t['aqi_label']}; padding: 4px 0;")
        self.update_label.setStyleSheet(f"font-size: 13px; color: {t['text_muted']};")
        self.about_btn.setStyleSheet(
            f"QPushButton {{ color: {t['text_muted']}; font-size: 13px; text-decoration: none; border: none; }}"
            f"QPushButton:hover {{ color: {t['text']}; }}"
        )

        self.theme_btn.setText("☀️ 亮色" if name == "light" else "🌙 暗色")

        for card in self.forecast_cards:
            card.apply_theme(t)

        for container, name_btn, del_btn in self._saved_items:
            self._style_saved_item(container, name_btn, del_btn, t)

        if persist:
            cfg = load_config()
            cfg.setdefault("app", {})["theme"] = name
            save_config(cfg)

    def _style_saved_item(self, container, name_btn, del_btn, t):
        container.setStyleSheet(
            f"QWidget {{ background: {t['saved_bg']}; border: 1px solid {t['saved_border']}; border-radius: 12px; }}"
        )
        name_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {t['saved_text']}; border: none; padding: 2px 4px; font-size: 13px; }}"
            f"QPushButton:hover {{ color: {t['text']}; }}"
        )
        del_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {t['saved_del']}; border: none; font-size: 14px; font-weight: bold; padding: 0; }}"
            f"QPushButton:hover {{ color: {t['saved_del_hover']}; }}"
        )

    def _init_client(self):
        host = get_api_host()
        project_id = get_project_id()
        credential_id = get_credential_id()
        privkey = read_private_key()

        if host and project_id and credential_id and privkey:
            self.client = QWeatherClient()
            self.statusBar().showMessage(f"✅ JWT 认证已就绪 ({host})", 3000)
        else:
            self.client = None
            missing = []
            if not host:
                missing.append("host")
            if not project_id:
                missing.append("project_id")
            if not credential_id:
                missing.append("credential_id")
            if not privkey:
                missing.append("private_key")
            self.statusBar().showMessage(
                f"⚠️ 缺少配置: {', '.join(missing)}。"
                " 请编辑 ~/.config/checkitout_weather/config.toml",
                10000,
            )

    def _build_ui(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 12, 16, 12)

        header_layout = QHBoxLayout()
        header = QLabel("☀ Checkitout Weather")
        header.setStyleSheet("font-size: 22px; font-weight: bold;")
        header_layout.addWidget(header)
        header_layout.addStretch()

        self.theme_btn = QPushButton()
        self.theme_btn.setToolTip("切换主题")
        self.theme_btn.clicked.connect(self._toggle_theme)
        header_layout.addWidget(self.theme_btn)
        layout.addLayout(header_layout)

        search_layout = QHBoxLayout()
        self.search_combo = QComboBox()
        self.search_combo.setEditable(True)
        self.search_combo.setCompleter(None)
        self.search_combo.setPlaceholderText("输入城市名称搜索...")
        self.search_combo.setMinimumHeight(38)
        self.search_combo.lineEdit().returnPressed.connect(self._search_city)
        search_layout.addWidget(self.search_combo, 1)

        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self._search_city)
        self.search_btn.setMinimumHeight(38)
        search_layout.addWidget(self.search_btn)

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setToolTip("手动刷新当前城市天气")
        self.refresh_btn.clicked.connect(self._manual_refresh)
        self.refresh_btn.setMinimumHeight(38)
        self.refresh_btn.setMinimumWidth(42)
        search_layout.addWidget(self.refresh_btn)

        layout.addLayout(search_layout)

        saved_bar = QHBoxLayout()
        saved_bar.setSpacing(6)
        saved_label = QLabel("📍 已收藏:")
        saved_label.setStyleSheet("font-size: 13px;")
        saved_bar.addWidget(saved_label)

        self.saved_container = QWidget()
        self.saved_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.saved_layout = FlowLayout(self.saved_container, margin=0, spacing=6)
        self._saved_items: list[tuple] = []
        saved_bar.addWidget(self.saved_container, 1)
        layout.addLayout(saved_bar)

        self.current_frame = QFrame()
        current_layout = QVBoxLayout(self.current_frame)
        current_layout.setSpacing(6)
        current_layout.setContentsMargins(20, 16, 20, 16)

        self.city_label = QLabel("请搜索城市")
        current_layout.addWidget(self.city_label)

        weather_row = QHBoxLayout()
        self.temp_icon_label = QLabel("--")
        self.temp_icon_label.setStyleSheet("font-size: 52px;")
        weather_row.addWidget(self.temp_icon_label)

        temp_info = QVBoxLayout()
        self.temp_main_label = QLabel("--")
        self.temp_main_label.setStyleSheet("font-size: 42px; font-weight: bold;")
        temp_info.addWidget(self.temp_main_label)

        self.desc_label = QLabel("")
        self.desc_label.setStyleSheet("font-size: 14px;")
        temp_info.addWidget(self.desc_label)
        weather_row.addLayout(temp_info, 1)
        current_layout.addLayout(weather_row)

        details_grid = QVBoxLayout()
        details_grid.setSpacing(4)

        row1 = QHBoxLayout()
        row1.setSpacing(16)
        self.detail_labels = {}
        detail_items = [
            ("humidity", "💧 湿度", "--"),
            ("precip", "🌧 降水", "--"),
            ("pressure", "🌀 气压", "--"),
            ("wind", "🌬 风", "--"),
            ("vis", "👁 能见度", "--"),
            ("uv", "☀ UV", "--"),
        ]
        for key, label, default in detail_items:
            lbl = QLabel(f"{label}  {default}")
            self.detail_labels[key] = lbl
            row1.addWidget(lbl)
        details_grid.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(16)
        self.sun_label = QLabel("🌅 日出  --  🌇 日落  --")
        row2.addWidget(self.sun_label)
        row2.addStretch()
        details_grid.addLayout(row2)
        current_layout.addLayout(details_grid)

        layout.addWidget(self.current_frame)

        forecast_layout = QVBoxLayout()
        forecast_layout.setSpacing(8)
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        self.forecast_cards = []
        for i in range(8):
            card = ForecastCard()
            self.forecast_cards.append(card)
            (row1 if i < 4 else row2).addWidget(card)
        forecast_layout.addLayout(row1)
        forecast_layout.addLayout(row2)
        layout.addLayout(forecast_layout)

        self.air_label = QLabel("")
        layout.addWidget(self.air_label)

        footer = QHBoxLayout()
        self.update_label = QLabel("")
        footer.addWidget(self.update_label)
        footer.addStretch()

        self.about_btn = QPushButton("关于")
        self.about_btn.setFlat(True)
        self.about_btn.setCursor(Qt.PointingHandCursor)
        self.about_btn.clicked.connect(self._show_about)
        footer.addWidget(self.about_btn)
        layout.addLayout(footer)

        layout.addStretch()

    def _show_about(self):
        dialog = AboutDialog(self._theme, self)
        dialog.exec()

    def _toggle_theme(self):
        new = "light" if self._theme_name == "dark" else "dark"
        self._apply_theme(new)

    def _load_saved_cities(self):
        for container, _, _ in self._saved_items:
            container.deleteLater()
        self._saved_items.clear()
        for c in get_saved_cities():
            self._add_saved_city_button(c)

    def _add_saved_city_button(self, c: dict):
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        row = QHBoxLayout(container)
        row.setContentsMargins(8, 3, 8, 3)
        row.setSpacing(4)

        label = c["name"]
        if c.get("adm2") and c["adm2"] != c["name"]:
            label = f"{c['adm2']}-{c['name']}"
        elif c.get("adm1") and c["adm1"] != c["name"]:
            label = f"{c['adm1']}-{c['name']}"

        city_id = c["id"]
        name_btn = QPushButton(label)
        name_btn.clicked.connect(lambda checked, cid=city_id: self._load_saved_city(cid))
        row.addWidget(name_btn)

        del_btn = QPushButton("x")
        del_btn.setFixedSize(18, 18)
        del_btn.clicked.connect(lambda checked, cid=city_id: self._delete_saved_city(cid))
        row.addWidget(del_btn)

        self._style_saved_item(container, name_btn, del_btn, self._theme)
        self.saved_layout.addWidget(container)
        self._saved_items.append((container, name_btn, del_btn))

    def _load_saved_city(self, city_id: str):
        for c in get_saved_cities():
            if c["id"] == city_id:
                city = City(id=c["id"], name=c["name"], lat=c["lat"], lon=c["lon"],
                            adm1=c.get("adm1", ""), adm2=c.get("adm2", ""))
                self._fetch_and_display(city)
                return

    def _delete_saved_city(self, city_id: str):
        remove_saved_city(city_id)
        self._load_saved_cities()

    def _search_city(self):
        query = self.search_combo.currentText().strip()
        if not query:
            QMessageBox.warning(self, "提示", "请输入城市名称后搜索")
            return
        if not self.client:
            QMessageBox.warning(
                self, "配置未完成",
                "请先配置和风天气 JWT 认证信息。\n"
                "编辑 ~/.config/checkitout_weather/config.toml，填入:\n"
                "[api]\n"
                'host = "你的专属Host"\n'
                'project_id = "你的Project ID"\n'
                'credential_id = "你的Credential ID"\n'
                'private_key_path = "/path/to/private.pem"\n'
                "# 或用 inline 私钥内容替代文件路径\n"
                '# private_key = "-----BEGIN PRIVATE KEY-----\\n..."\n\n'
                "或通过环境变量设置:\n"
                "export QWEATHER_API_HOST=...\n"
                "export QWEATHER_PROJECT_ID=...\n"
                "export QWEATHER_CREDENTIAL_ID=...\n"
                "export QWEATHER_PRIVATE_KEY=\"$(cat key.pem)\""
            )
            return

        try:
            cities = self.client.lookup_city(query)
        except Exception as e:
            QMessageBox.critical(self, "网络错误", f"搜索城市失败:\n{e}")
            return

        if not cities:
            QMessageBox.information(self, "无结果", "未找到匹配的城市")
            return

        self._cached_cities = cities

        if len(cities) == 1:
            self._select_city(cities[0])
            return

        dialog = CityPickerDialog(cities, self._theme, self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_city:
            self._select_city(dialog.selected_city)

    def _select_city(self, city: City):
        self._save_city(city)
        self._load_saved_cities()
        self._fetch_and_display(city)

    def _save_city(self, city: City):
        add_saved_city({
            "id": city.id,
            "name": city.name,
            "adm1": city.adm1,
            "adm2": city.adm2,
            "lat": city.lat,
            "lon": city.lon,
        })

    def _fetch_and_display(self, city):
        try:
            wd = self.client.fetch_weather(city)
        except Exception as e:
            QMessageBox.critical(self, "网络错误", f"获取天气数据失败:\n{e}")
            return
        self.weather_data = wd
        self._display_weather(wd)

    def _display_weather(self, wd: WeatherData):
        city = wd.city
        loc_parts = [city.name]
        if city.adm2 and city.adm2 != city.name:
            loc_parts.append(city.adm2)
        if city.adm1:
            loc_parts.append(city.adm1)
        self.city_label.setText(" - ".join(loc_parts))

        if wd.current:
            c = wd.current
            self.temp_icon_label.setText(get_icon(c.icon))
            self.temp_main_label.setText(f"{c.temp}°C")
            self.desc_label.setText(
                f"{c.text}  ·  体感 {c.feels_like}°C  ·  ☁ {c.cloud}%"
            )

            self.detail_labels["humidity"].setText(f"💧 湿度  {c.humidity}%")
            self.detail_labels["precip"].setText(f"🌧 降水  {c.precip}mm")
            self.detail_labels["pressure"].setText(f"🌀 气压  {c.pressure}hPa")
            self.detail_labels["wind"].setText(f"🌬 风  {c.wind_dir}{c.wind_scale}级")
            vis_val = c.vis if isinstance(c.vis, str) else str(c.vis)
            self.detail_labels["vis"].setText(f"👁 能见度  {vis_val}km")
        else:
            self.temp_icon_label.setText("--")
            self.temp_main_label.setText("--")
            self.desc_label.setText("")
            for lbl in self.detail_labels.values():
                lbl.setText("--")

        if wd.forecast:
            uv_index = wd.forecast[0].uv_index
            uv_label = self._uv_desc(uv_index)
            self.detail_labels["uv"].setText(f"☀ 紫外线 UV  {uv_label}")
        else:
            self.detail_labels["uv"].setText("☀ UV  --")

        if wd.yesterday:
            self.forecast_cards[0].set_data(wd.yesterday, label_override="昨天")
        else:
            self.forecast_cards[0].set_data(ForecastDay.__new__(ForecastDay), label_override="昨天")
        for i, fc in enumerate(wd.forecast[:7]):
            self.forecast_cards[i + 1].set_data(fc, day_offset=i + 1)
        for i in range(len(wd.forecast), 7):
            self.forecast_cards[i + 1].set_data(ForecastDay.__new__(ForecastDay), day_offset=i + 1)

        if wd.air:
            a = wd.air
            aqi_color = self._aqi_color(a.aqi)
            primary_str = f" 首要污染物: {a.primary}" if a.primary else ""
            self.air_label.setText(
                f"🌬 空气质量: <span style='color:{aqi_color}; font-weight:bold;'>{a.category}</span>"
                f"  (AQI {a.aqi})  PM2.5: {a.pm2p5} μg/m³  PM10: {a.pm10} μg/m³"
                f"{primary_str}"
            )
            self.air_label.setTextFormat(Qt.RichText)
        else:
            self.air_label.setText("")

        if wd.sun:
            sr = self._extract_time(wd.sun.sunrise)
            ss = self._extract_time(wd.sun.sunset)
            self.sun_label.setText(f"🌅 日出  {sr}  🌇 日落  {ss}")
        else:
            self.sun_label.setText("🌅 日出  --  🌇 日落  --")

        if wd.current:
            raw = wd.current.update_time
            formatted = self._format_time(raw)
            self.update_label.setText(f"🕐 更新时间: {formatted}")
        else:
            self.update_label.setText("")

    @staticmethod
    def _extract_time(raw: str) -> str:
        if not raw:
            return "--"
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M%z"):
            try:
                dt = datetime.strptime(raw.replace("+08:00", "+0800"), fmt)
                return dt.strftime("%H:%M")
            except ValueError:
                continue
        return raw[-5:] if len(raw) >= 5 else raw

    @staticmethod
    def _format_time(raw: str) -> str:
        for fmt in ("%Y-%m-%dT%H:%M%z", "%Y-%m-%dT%H:%M:%S%z",
                     "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
            try:
                dt = datetime.strptime(raw.replace("+08:00", "+0800").replace(
                    "+08", "+0800"), fmt)
                return dt.strftime("%Y-%m-%d %H:%M (%z)").replace("+0800", "+08:00")
            except ValueError:
                continue
        return raw

    def _aqi_color(self, aqi: int) -> str:
        if aqi <= 50:
            return "#00e400"
        elif aqi <= 100:
            return "#ffff00"
        elif aqi <= 150:
            return "#ff7e00"
        elif aqi <= 200:
            return "#ff0000"
        elif aqi <= 300:
            return "#99004c"
        else:
            return "#7e0023"

    @staticmethod
    def _uv_desc(uv: int) -> str:
        if uv <= 2:
            return f"{uv} (弱)"
        elif uv <= 5:
            return f"{uv} (中等)"
        elif uv <= 7:
            return f"{uv} (强)"
        elif uv <= 10:
            return f"{uv} (很强)"
        else:
            return f"{uv} (极强)"

    def _manual_refresh(self):
        if not self.weather_data:
            return
        old_update_time = self.weather_data.current.update_time if self.weather_data.current else None
        city = self.weather_data.city
        try:
            wd = self.client.fetch_weather(city)
        except Exception as e:
            QMessageBox.critical(self, "网络错误", f"获取天气数据失败:\n{e}")
            return
        new_update_time = wd.current.update_time if wd.current else None
        if old_update_time and new_update_time and old_update_time == new_update_time:
            QMessageBox.information(self, "暂无更新", "暂无更新数据，请稍后再试。")
            return
        self.weather_data = wd
        self._display_weather(wd)

    def closeEvent(self, event):
        if self.client:
            self.client.close()
        super().closeEvent(event)
