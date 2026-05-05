from __future__ import annotations

import json
import sys
import tkinter as tk
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from tkinter import messagebox, ttk
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

try:
    from PIL import Image
except ImportError:
    Image = None


APP_TITLE = "PZ Build 42 Book Checker"
DATA_DIR = Path.home() / "Zomboid" / "Book Checker"
SAVE_FILE = DATA_DIR / "pz_books_progress.json"
LEGACY_SAVE_FILE = Path("pz_books_progress.json")
SOURCE_URL = "https://pzwiki.net/wiki/Skill_book"
SRC_IMAGE_DIR = Path("Src") / "img"
APP_ICON_FILE = Path("assets") / "app.ico"
EMOJI_CACHE_DIR = DATA_DIR / "emoji_cache"
EMOJI_CACHE_VERSION = "v2"
EMOJI_ICON_SIZE = 26


THEMES = {
    "light": {
        "app_bg": "#edf1ed",
        "card_bg": "#fbfcf8",
        "card_complete_bg": "#dcefe2",
        "border": "#cbd5cb",
        "border_complete": "#4a8f62",
        "text": "#1e2b24",
        "muted": "#6d756f",
        "muted_complete": "#4a6a56",
        "button_bg": "#f1f3ed",
        "button_fg": "#2f3b33",
        "button_active": "#e2e7dc",
        "found_bg": "#3f7d55",
        "found_active": "#336845",
        "found_fg": "#ffffff",
        "empty": "#5f6b72",
        "panel_bg": "#e4eae3",
        "field_bg": "#fbfcf8",
        "field_border": "#b8c4b8",
        "control_bg": "#f5f7f1",
        "control_hover": "#e8eee6",
    },
    "dark": {
        "app_bg": "#151b18",
        "card_bg": "#1f2221",
        "card_complete_bg": "#2a2d2b",
        "border": "#3b3f3d",
        "border_complete": "#777d79",
        "text": "#edf6ee",
        "muted": "#a5b1aa",
        "muted_complete": "#d2d8d4",
        "button_bg": "#2a2d2b",
        "button_fg": "#eaf2ec",
        "button_active": "#383c39",
        "found_bg": "#3f7d55",
        "found_active": "#336845",
        "found_fg": "#ffffff",
        "empty": "#a5b1aa",
        "panel_bg": "#1c211e",
        "field_bg": "#242927",
        "field_border": "#444b47",
        "control_bg": "#252b28",
        "control_hover": "#303732",
    },
}


def resource_path(relative_path: str | Path) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path.cwd()))
    return base_path / relative_path


TEXT = {
    "ru": {
        "all_skills": "Все темы",
        "app_title": "Книги навыков Project Zomboid Build 42",
        "clear": "Очистить",
        "empty": "Ничего не найдено",
        "found_status": "Собрано {found}/{total} книг, закрыто тем: {complete}/{skills}",
        "language": "Язык: RU",
        "mark": "Отметить",
        "missing": "Только неполные",
        "reset": "Сбросить все",
        "reset_confirm": "Очистить все отметки найденных книг?",
        "reset_title": "Сбросить все",
        "save": "Сохранить",
        "search": "Поиск",
        "source": "Источник: {url}",
        "theme_dark": "Тема: темная",
        "theme_light": "Тема: светлая",
        "topic": "Тема",
        "volume": "Том {volume}",
        "volumes": "{count}/5 томов",
        "volumes_complete": "Все тома собраны",
    },
    "en": {
        "all_skills": "All topics",
        "app_title": "Project Zomboid Build 42 Skill Books",
        "clear": "Clear",
        "empty": "Nothing found",
        "found_status": "Found {found}/{total} books, completed topics: {complete}/{skills}",
        "language": "Language: EN",
        "mark": "Mark",
        "missing": "Only incomplete",
        "reset": "Reset all",
        "reset_confirm": "Clear all found book marks?",
        "reset_title": "Reset all",
        "save": "Save",
        "search": "Search",
        "source": "Source: {url}",
        "theme_dark": "Theme: dark",
        "theme_light": "Theme: light",
        "topic": "Topic",
        "volume": "Vol. {volume}",
        "volumes": "{count}/5 volumes",
        "volumes_complete": "All volumes collected",
    },
}


VOLUME_META = [
    ("I", "1-2", 220),
    ("II", "3-4", 260),
    ("III", "5-6", 300),
    ("IV", "7-8", 340),
    ("V", "9-10", 380),
]


SKILL_BOOKS = {
    "Agriculture": [
        "Better Gardening",
        "Growing Food at Home",
        "Liam Keating's Subsistence Farming",
        "The Science of Crop Genetics and Yields",
        "USDA Guide to Agricultural Output Maximization",
    ],
    "Aiming": [
        "Better Aiming",
        "Drawing and Shooting",
        "Leading Moving Targets",
        "Long Range Sniping Tactics",
        "Secrets From the World's Best Snipers",
    ],
    "Animal Care": [
        "A Tale of St. Francis",
        "Animal Welfare Basics",
        "How Animals Think: A Helpful Guide",
        "The Wants and Needs of Diverse Fauna",
        "Wilds Tamed: An In-Depth Comparative",
    ],
    "Blacksmithing": [
        "Elementary Forge Practice",
        "General Purpose Blacksmithing",
        "Old West Smiths and Their Secrets",
        "Really Hard Steel Co. Workers Handbook",
        "The Complete Encyclopedia of Metallurgy",
    ],
    "Butchering": [
        "Butchering Basics",
        "From Chuck to Shank",
        "Hunter's Guide to Butchering",
        "Master Butcher's Complete Guide",
        "The Ergonomics of Tools in Meat Cutting Operations",
    ],
    "Carpentry": [
        "A Guide to Nailing",
        "Carpentry, Woodcraft Style",
        "Hand Crafted Shelving and Storage",
        "Making Your Own Cabin From Scratch",
        "Site Joinery and Architectural Carpentry",
    ],
    "Carving": [
        "Beginners Carving",
        "Cool Woodshaping Projects!",
        "Grinling Gibbons: His Life and Works",
        "Medieval Wood and Bone Carving Techniques",
        "The Art and Process of Natural Material Carving",
    ],
    "Cooking": [
        "Better Burger Flipping",
        "Essential Home Cooking Guide",
        "Flavorful Cuisine - 1993 Edition",
        "Professional Tips from a Master Chef",
        "Ruban Vert Gourmet - Complete Cooking Techniques",
    ],
    "Electrical": [
        "Basic Electronics",
        "Kentucky AV Guide '93",
        "Practical Wiring Guide",
        "Telecommunications in the 20th Century",
        "Understanding Integrated Controls for Electronic Systems",
    ],
    "First Aid": [
        "A Scouts Injury Guide",
        "Bandaging and Suturing",
        "Emergency Paramedics Manual",
        "Gray's Anatomy of the Human Body",
        "Surgical Techniques of the Operating Room",
    ],
    "Fishing": [
        "Dean's Good Fishing Guide",
        "Fly Fishing, with JR Hartley",
        "Fresh and Saltwater Fishing",
        "Latest Rod and Net Techniques",
        "The Authoritative Kentucky Fishing Guide",
    ],
    "Foraging": [
        "A Feast in the Forest",
        "Dean's Guide to Sticks & Stones",
        "Finding The Treasure in the Trash",
        "Survival Foraging: How Nature Can Save Your Life",
        "US Park Service Complete Nature Census - Kentucky",
    ],
    "Glassmaking": [
        "Glass: A History",
        "From Sand to Glass: A Journey",
        "Laboratory Manual of Glassblowing",
        "Secrets of the Carlow Crystal Makers",
        "Venetian Glass: An Electron Microprobe Analysis",
    ],
    "Knapping": [
        "Flint Knapping 101",
        "Guide to Kentucky Geology",
        "Lithic Technology Manual 1993",
        "Schmidt Rock Hardness Testing Techniques",
        "Technological Morphometrics of Clovis Artifacts",
    ],
    "Long Blade": [
        "Cool Swords!",
        "Fencing: A History",
        "Old Sword-Play by Alfred Hutton",
        "The Zettels of Johannes Liechtenauer",
        "Wear Analysis of Selected Medieval Swords",
    ],
    "Maintenance": [
        "Basic Repairs",
        "Better Tools, Made Easy",
        "Home Guide to Tool Repairs",
        "Maintaining High Grade Tools",
        "Understanding Biomechanics of Tool Use",
    ],
    "Masonry": [
        "A Bricklayer's Life",
        "Flooring: Do It Yourself",
        "Dibnah's Guide to Bricks",
        "Secrets of a Professional Mason",
        "Statistical Analysis of Historic Masonry Constructions",
    ],
    "Mechanics": [
        "Carzone's Repair Guide",
        "How Vehicle Engines Work",
        "Laine's Repair Manual '93",
        "Long Term Vehicle Maintenance",
        "Mastering Automotive Fault Diagnosis Techniques",
    ],
    "Pottery": [
        "Ancient Pottery",
        "Build Your Own Kiln",
        "Glazing Ceramics at Home",
        "Ming Chinese Masterworks: A Guide",
        "Pyrometamorphic Process of Ceramic Materials",
    ],
    "Reloading": [
        "Basic Reloading",
        "Dead Man's Click",
        "Jungle Style Reloading",
        "Strippers, Speedloaders, and Bolt Action",
        "The Ultimate Encyclopedia of Reloading Techniques",
    ],
    "Tailoring": [
        "Basic Clothing Repair",
        "From Rags to Royalty: A Sewing Guide",
        "Haute Couture Tailoring Methods",
        "Modern Patterns from the Catwalks of Paris",
        "Textile Production and Manufacturing Techniques",
    ],
    "Tracking": [
        "Animal Pawprints",
        "Hunting with Hemingway",
        "Long Range Animal Tracking",
        "The Smell of Ivory: An African Adventure",
        "Understanding Animal Behavior Through Spoor Placement",
    ],
    "Trapping": [
        "Basic Pest Control",
        "Better Trapping, with Dean",
        "Park Rangers Wildlife Handbook '93",
        "Research on Rodents and Mammals of Kentucky",
        "The Encyclopedia of Applied Animal Psychology",
    ],
    "Welding": [
        "Basics of Welding",
        "Building with Metal",
        "Machining Metal: The Mass Genfac Guide",
        "Ore to Sheets: A Complete Metalworking Manual",
        "Technological Fundamentals of Metal Fabrication",
    ],
}


SKILL_RU = {
    "Agriculture": "Фермерство",
    "Aiming": "Прицеливание",
    "Animal Care": "Уход за животными",
    "Blacksmithing": "Кузня",
    "Butchering": "Разделка мяса",
    "Carpentry": "Строительство",
    "Carving": "Резьба",
    "Cooking": "Кулинария",
    "Electrical": "Электрика",
    "First Aid": "Первая помощь",
    "Fishing": "Рыбалка",
    "Foraging": "Собирательство",
    "Glassmaking": "Стеклоделие",
    "Knapping": "Обтесывание камня",
    "Long Blade": "Длинные клинки",
    "Maintenance": "Прочность",
    "Masonry": "Каменьщик",
    "Mechanics": "Автомеханика",
    "Pottery": "Гончарное дело",
    "Reloading": "Перезарядка",
    "Tailoring": "Шитье",
    "Tracking": "Выслеживание",
    "Trapping": "Охота ловушками",
    "Welding": "Сварка",
}


SKILL_EN = {
    "Agriculture": "Farming",
    "Aiming": "Aiming",
    "Animal Care": "Animal Care",
    "Blacksmithing": "Forge",
    "Butchering": "Butchering",
    "Carpentry": "Carpentry",
    "Carving": "Carving",
    "Cooking": "Cooking",
    "Electrical": "Electrical",
    "First Aid": "First Aid",
    "Fishing": "Fishing",
    "Foraging": "Foraging",
    "Glassmaking": "Glassmaking",
    "Knapping": "Knapping",
    "Long Blade": "Long Blade",
    "Maintenance": "Durability",
    "Masonry": "Masonry",
    "Mechanics": "Mechanics",
    "Pottery": "Pottery",
    "Reloading": "Reloading",
    "Tailoring": "Tailoring",
    "Tracking": "Tracking",
    "Trapping": "Trapping",
    "Welding": "Welding",
}


SKILL_LABELS = {
    "ru": SKILL_RU,
    "en": SKILL_EN,
}


SKILL_COLORS = {
    "Agriculture": "#6aa84f",
    "Aiming": "#8e3f3f",
    "Animal Care": "#a87b48",
    "Blacksmithing": "#5c5f66",
    "Butchering": "#a94442",
    "Carpentry": "#b17b3a",
    "Carving": "#8a6335",
    "Cooking": "#d79b35",
    "Electrical": "#d6b937",
    "First Aid": "#d75a5a",
    "Fishing": "#3f86a8",
    "Foraging": "#4f9b69",
    "Glassmaking": "#60a9b8",
    "Knapping": "#7f8377",
    "Long Blade": "#6e7891",
    "Maintenance": "#7d6a58",
    "Masonry": "#818783",
    "Mechanics": "#4f6c91",
    "Pottery": "#b66b4b",
    "Reloading": "#8b6f3e",
    "Tailoring": "#8f63a9",
    "Tracking": "#5f7d45",
    "Trapping": "#8c7445",
    "Welding": "#4d7f8f",
}


SKILL_EMOJI = {
    "Agriculture": "🌱",
    "Aiming": "🎯",
    "Animal Care": "🐾",
    "Blacksmithing": "⚒️",
    "Butchering": "🥩",
    "Carpentry": "🪚",
    "Carving": "🪵",
    "Cooking": "🍳",
    "Electrical": "⚡",
    "First Aid": "➕",
    "Fishing": "🎣",
    "Foraging": "🍄",
    "Glassmaking": "💎",
    "Knapping": "🪨",
    "Long Blade": "🗡️",
    "Maintenance": "🛡️",
    "Masonry": "🧱",
    "Mechanics": "🔧",
    "Pottery": "🏺",
    "Reloading": "🔫",
    "Tailoring": "🧵",
    "Tracking": "👣",
    "Trapping": "🪤",
    "Welding": "✨",
}


@dataclass(frozen=True)
class Book:
    key: str
    skill: str
    volume: str
    levels: str
    pages: int
    title: str


def build_books() -> list[Book]:
    books = []
    for skill, titles in SKILL_BOOKS.items():
        for index, title in enumerate(titles):
            volume, levels, pages = VOLUME_META[index]
            books.append(
                Book(
                    key=f"{skill}:{volume}",
                    skill=skill,
                    volume=volume,
                    levels=levels,
                    pages=pages,
                    title=f'{skill} {volume}: "{title}"',
                )
            )
    return books


class BookCheckerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1040x720")
        self.minsize(780, 520)

        self.books = build_books()
        self.progress, saved_theme, saved_language = self.load_state()
        self.theme_name = saved_theme
        self.language = saved_language
        self.search_var = tk.StringVar()
        self.skill_var = tk.StringVar(value=self.t("all_skills"))
        self.selected_skill_key: str | None = None
        self.status_var = tk.StringVar()
        self.show_missing_only = tk.BooleanVar(value=False)
        self.dark_theme_var = tk.BooleanVar(value=self.theme_name == "dark")
        self.card_widgets: dict[str, dict[str, object]] = {}
        self.ui_widgets: list[tk.Widget] = []
        self.skill_images: dict[str, tk.PhotoImage] = {}
        self.emoji_images: dict[str, tk.PhotoImage] = {}
        self.empty_label: tk.Label | None = None
        self.save_after_id: str | None = None

        self.configure_style()
        self.configure_window_icon()
        self.load_skill_images()
        self.load_emoji_images()
        self.create_widgets()
        self.refresh()

    def configure_style(self) -> None:
        palette = self.palette
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("TFrame", background=palette["app_bg"])
        style.configure("TLabel", background=palette["app_bg"], foreground=palette["text"])
        style.configure("Muted.TLabel", background=palette["app_bg"], foreground=palette["muted"])
        style.configure("TCheckbutton", background=palette["app_bg"], foreground=palette["text"])

    def configure_window_icon(self) -> None:
        icon_path = resource_path(APP_ICON_FILE)
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except tk.TclError:
                pass

    def load_skill_images(self) -> None:
        for skill in SKILL_BOOKS:
            image_path = resource_path(SRC_IMAGE_DIR / f"{skill}.png")
            if image_path.exists():
                self.skill_images[skill] = tk.PhotoImage(file=str(image_path))

    def load_emoji_images(self) -> None:
        EMOJI_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        can_fetch_emoji = True
        for skill, emoji_text in SKILL_EMOJI.items():
            cache_path = EMOJI_CACHE_DIR / f"{EMOJI_CACHE_VERSION}_{skill}.png"
            if cache_path.exists():
                self.emoji_images[skill] = tk.PhotoImage(file=str(cache_path))
                continue
            if Image is None or not can_fetch_emoji:
                continue

            image = self.fetch_emoji_image(emoji_text)
            if image is None:
                can_fetch_emoji = False
                continue

            image = self.prepare_emoji_icon(image)
            image.save(cache_path)
            self.emoji_images[skill] = tk.PhotoImage(file=str(cache_path))

    def fetch_emoji_image(self, emoji_text: str) -> object | None:
        url = f"https://emojicdn.elk.sh/{quote_plus(emoji_text)}?style=twitter"
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urlopen(request, timeout=1.5) as response:
                data = response.read()
        except Exception:
            return None
        return Image.open(BytesIO(data)).convert("RGBA")

    def prepare_emoji_icon(self, image: object) -> object:
        image = self.crop_transparent_image(image)
        image.thumbnail((EMOJI_ICON_SIZE, EMOJI_ICON_SIZE), Image.LANCZOS)
        result = Image.new("RGBA", (EMOJI_ICON_SIZE, EMOJI_ICON_SIZE), (0, 0, 0, 0))
        x = (EMOJI_ICON_SIZE - image.width) // 2
        y = (EMOJI_ICON_SIZE - image.height) // 2
        result.paste(image, (x, y), image)
        return result

    def crop_transparent_image(self, image: object) -> object:
        alpha = image.getchannel("A")
        bounds = alpha.getbbox()
        if bounds is None:
            return image
        return image.crop(bounds)

    def create_widgets(self) -> None:
        palette = self.palette
        self.configure(bg=palette["app_bg"])
        root = tk.Frame(self, bg=palette["app_bg"], padx=18, pady=18)
        root.pack(fill=tk.BOTH, expand=True)
        self.root_frame = root

        header = tk.Frame(root, bg=palette["app_bg"])
        header.pack(fill=tk.X)
        self.header_frame = header
        self.title_label = tk.Label(
            header,
            text=self.t("app_title"),
            bg=palette["app_bg"],
            fg=palette["text"],
            font=("Segoe UI", 17, "bold"),
        )
        self.title_label.pack(side=tk.LEFT)
        self.status_label = tk.Label(
            header,
            textvariable=self.status_var,
            bg=palette["app_bg"],
            fg=palette["muted"],
            font=("Segoe UI", 9),
        )
        self.status_label.pack(side=tk.RIGHT)

        controls = tk.Frame(root, bg=palette["panel_bg"], padx=10, pady=8)
        controls.pack(fill=tk.X, pady=(14, 12))
        self.controls_frame = controls

        self.search_label = self.make_control_label(controls, self.t("search"))
        self.search_label.pack(side=tk.LEFT, padx=(2, 6))
        search_wrap = self.make_field(controls)
        search_wrap.pack(side=tk.LEFT, padx=(0, 12))
        self.search_entry = tk.Entry(
            search_wrap,
            textvariable=self.search_var,
            width=24,
            relief=tk.FLAT,
            bd=0,
            bg=palette["field_bg"],
            fg=palette["text"],
            insertbackground=palette["text"],
            font=("Segoe UI", 10),
        )
        self.search_entry.pack(side=tk.LEFT, padx=(10, 10), pady=7)
        self.search_entry.bind("<KeyRelease>", lambda _event: self.refresh())

        self.topic_label = self.make_control_label(controls, self.t("topic"))
        self.topic_label.pack(side=tk.LEFT, padx=(0, 6))
        select_wrap = self.make_field(controls)
        select_wrap.pack(side=tk.LEFT, padx=(0, 12))
        self.skill_menu_button = tk.Menubutton(
            select_wrap,
            text=self.skill_var.get(),
            compound=tk.LEFT,
            relief=tk.FLAT,
            bd=0,
            bg=palette["field_bg"],
            fg=palette["text"],
            activebackground=palette["control_hover"],
            activeforeground=palette["text"],
            font=("Segoe UI", 10),
            padx=8,
            pady=5,
            width=18,
            anchor="w",
        )
        self.skill_menu = tk.Menu(self.skill_menu_button, tearoff=False, bg=palette["field_bg"], fg=palette["text"])
        self.skill_menu_button.configure(menu=self.skill_menu)
        self.skill_menu_button.pack(side=tk.LEFT, padx=(8, 8), pady=4)
        self.rebuild_skill_menu()

        self.missing_button = self.make_toggle_button(
            controls,
            self.t("missing"),
            self.show_missing_only,
            self.toggle_missing_filter,
        )
        self.missing_button.pack(side=tk.LEFT, padx=(0, 8))

        self.theme_button = self.make_toggle_button(
            controls,
            self.t("theme_dark"),
            self.dark_theme_var,
            self.toggle_theme,
        )
        self.update_toggle_button(self.theme_button)
        self.theme_button.pack(side=tk.LEFT, padx=(0, 8))

        self.language_button = self.make_action_button(controls, self.t("language"), self.toggle_language)
        self.language_button.pack(side=tk.LEFT, padx=(0, 8))

        self.mark_button = self.make_action_button(controls, self.t("mark"), self.mark_visible_found)
        self.mark_button.pack(side=tk.RIGHT, padx=(8, 0))
        self.clear_button = self.make_action_button(controls, self.t("clear"), self.clear_visible)
        self.clear_button.pack(side=tk.RIGHT)

        content = tk.Frame(root, bg=palette["app_bg"])
        content.pack(fill=tk.BOTH, expand=True)
        self.content_frame = content

        self.canvas = tk.Canvas(content, bg=palette["app_bg"], highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(content, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.cards_frame = tk.Frame(self.canvas, bg=palette["app_bg"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        self.cards_frame.bind("<Configure>", self.on_cards_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        footer = tk.Frame(root, bg=palette["app_bg"])
        footer.pack(fill=tk.X, pady=(10, 0))
        self.footer_frame = footer
        self.save_button = self.make_action_button(footer, self.t("save"), self.save_progress)
        self.save_button.pack(side=tk.LEFT)
        self.reset_button = self.make_action_button(footer, self.t("reset"), self.reset_all)
        self.reset_button.pack(side=tk.LEFT, padx=(8, 0))
        self.source_label = tk.Label(
            footer,
            text=self.t("source", url=SOURCE_URL),
            bg=palette["app_bg"],
            fg=palette["muted"],
            font=("Segoe UI", 9),
        )
        self.source_label.pack(side=tk.RIGHT)

    def make_control_label(self, parent: tk.Widget, text: str) -> tk.Label:
        palette = self.palette
        label = tk.Label(
            parent,
            text=text,
            bg=palette["panel_bg"],
            fg=palette["muted"],
            font=("Segoe UI", 9, "bold"),
        )
        self.ui_widgets.append(label)
        return label

    def make_field(self, parent: tk.Widget) -> tk.Frame:
        palette = self.palette
        wrap = tk.Frame(parent, bg=palette["field_border"], padx=2, pady=2)
        self.ui_widgets.append(wrap)
        return wrap

    def make_action_button(self, parent: tk.Widget, text: str, command: object) -> tk.Button:
        palette = self.palette
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=palette["control_bg"],
            fg=palette["text"],
            activebackground=palette["control_hover"],
            activeforeground=palette["text"],
            relief=tk.FLAT,
            bd=0,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=8,
            cursor="hand2",
        )
        self.ui_widgets.append(button)
        return button

    def make_toggle_button(self, parent: tk.Widget, text: str, variable: tk.BooleanVar, command: object) -> tk.Button:
        button = self.make_action_button(parent, text, lambda: self.toggle_var(variable, command))
        button.variable = variable
        self.update_toggle_button(button)
        return button

    def toggle_var(self, variable: tk.BooleanVar, command: object) -> None:
        variable.set(not variable.get())
        command()

    def update_toggle_button(self, button: tk.Button) -> None:
        palette = self.palette
        active = button.variable.get()
        if button is getattr(self, "theme_button", None):
            button.configure(text=self.t("theme_dark") if active else self.t("theme_light"))
        button.configure(
            bg=palette["found_bg"] if active else palette["control_bg"],
            fg=palette["found_fg"] if active else palette["text"],
            activebackground=palette["found_active"] if active else palette["control_hover"],
            activeforeground=palette["found_fg"] if active else palette["text"],
        )

    def rebuild_skill_menu(self) -> None:
        palette = self.palette
        self.skill_menu.delete(0, tk.END)
        self.skill_menu.configure(bg=palette["field_bg"], fg=palette["text"], activebackground=palette["control_hover"])
        self.skill_menu.add_command(label=self.t("all_skills"), command=lambda: self.select_skill(None))
        for skill in SKILL_BOOKS:
            self.skill_menu.add_command(
                label=f"  {self.skill_label(skill)}",
                image=self.skill_images.get(skill),
                compound=tk.LEFT,
                command=lambda selected=skill: self.select_skill(selected),
            )

    def select_skill(self, skill: str | None) -> None:
        self.selected_skill_key = skill
        self.skill_var.set(self.t("all_skills") if skill is None else self.skill_label(skill))
        self.skill_menu_button.configure(
            text=self.skill_var.get(),
            image=self.skill_images.get(skill) if skill else "",
        )
        self.refresh()

    def toggle_missing_filter(self) -> None:
        self.update_toggle_button(self.missing_button)
        self.refresh()

    def on_cards_configure(self, _event: tk.Event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.canvas_window, width=event.width)
        self.layout_cards()

    def on_mousewheel(self, event: tk.Event) -> None:
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    @property
    def palette(self) -> dict[str, str]:
        return THEMES[self.theme_name]

    def t(self, key: str, **kwargs: object) -> str:
        template = TEXT[self.language][key]
        return template.format(**kwargs) if kwargs else template

    def skill_label(self, skill: str) -> str:
        return SKILL_LABELS[self.language][skill]

    def load_state(self) -> tuple[dict[str, bool], str, str]:
        save_file = SAVE_FILE if SAVE_FILE.exists() else LEGACY_SAVE_FILE
        if not save_file.exists():
            return {}, "light", "en"
        try:
            data = json.loads(save_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            messagebox.showwarning("Progress", "Could not read progress file. Starting fresh.")
            return {}, "light", "en"

        if "books" in data:
            progress = {str(key): bool(value) for key, value in data.get("books", {}).items()}
            theme = data.get("theme", "light")
            language = data.get("language", "en")
            return progress, theme if theme in THEMES else "light", language if language in TEXT else "en"

        return {str(key): bool(value) for key, value in data.items()}, "light", "en"

    def save_progress(self) -> None:
        self.save_after_id = None
        SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SAVE_FILE.write_text(
            json.dumps(
                {"theme": self.theme_name, "language": self.language, "books": self.progress},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        self.update_status()

    def schedule_save(self) -> None:
        if self.save_after_id is not None:
            self.after_cancel(self.save_after_id)
        self.save_after_id = self.after(180, self.save_progress)

    def visible_skills(self) -> list[str]:
        query = self.search_var.get().strip().lower()
        selected_skill = self.selected_skill()
        result = []
        for skill in SKILL_BOOKS:
            if selected_skill and skill != selected_skill:
                continue
            if self.show_missing_only.get() and self.skill_complete(skill):
                continue

            skill_books = self.books_for_skill(skill)
            haystack = " ".join(
                [
                    skill,
                    SKILL_RU[skill],
                    SKILL_EN[skill],
                    *[f"{book.volume} {book.levels} {book.title}" for book in skill_books],
                ]
            ).lower()
            if query and query not in haystack:
                continue
            result.append(skill)
        return result

    def filtered_books(self) -> list[Book]:
        visible = set(self.visible_skills())
        return [book for book in self.books if book.skill in visible]

    def books_for_skill(self, skill: str) -> list[Book]:
        return [book for book in self.books if book.skill == skill]

    def refresh(self) -> None:
        if not self.card_widgets:
            for skill in SKILL_BOOKS:
                self.create_skill_card(skill, self.books_for_skill(skill))

        visible_skills = self.visible_skills()
        visible_set = set(visible_skills)
        for skill, widgets in self.card_widgets.items():
            if skill not in visible_set:
                widgets["card"].grid_remove()

        if not visible_skills:
            if self.empty_label is None:
                self.empty_label = tk.Label(
                    self.cards_frame,
                    text=self.t("empty"),
                    bg=self.palette["app_bg"],
                    fg=self.palette["empty"],
                    font=("Segoe UI", 13),
                )
            self.empty_label.grid(row=0, column=0, sticky="nsew", padx=12, pady=24)
        elif self.empty_label is not None:
            self.empty_label.grid_remove()

        self.layout_cards(visible_skills)
        self.update_status()

    def toggle_theme(self) -> None:
        self.theme_name = "dark" if self.dark_theme_var.get() else "light"
        self.apply_theme()
        self.update_toggle_button(self.theme_button)
        self.schedule_save()

    def toggle_language(self) -> None:
        self.language = "en" if self.language == "ru" else "ru"
        self.skill_var.set(self.t("all_skills") if self.selected_skill_key is None else self.skill_label(self.selected_skill_key))
        self.apply_language()
        self.schedule_save()

    def apply_language(self) -> None:
        self.title_label.configure(text=self.t("app_title"))
        self.search_label.configure(text=self.t("search"))
        self.topic_label.configure(text=self.t("topic"))
        self.missing_button.configure(text=self.t("missing"))
        self.language_button.configure(text=self.t("language"))
        self.mark_button.configure(text=self.t("mark"))
        self.clear_button.configure(text=self.t("clear"))
        self.save_button.configure(text=self.t("save"))
        self.reset_button.configure(text=self.t("reset"))
        self.source_label.configure(text=self.t("source", url=SOURCE_URL))
        self.update_toggle_button(self.theme_button)
        self.skill_menu_button.configure(text=self.skill_var.get())
        self.rebuild_skill_menu()
        if self.empty_label is not None:
            self.empty_label.configure(text=self.t("empty"))
        for skill in self.card_widgets:
            self.update_skill_card(skill)
        self.refresh()

    def apply_theme(self) -> None:
        palette = self.palette
        self.configure_style()
        self.configure(bg=palette["app_bg"])
        self.root_frame.configure(bg=palette["app_bg"])
        self.header_frame.configure(bg=palette["app_bg"])
        self.controls_frame.configure(bg=palette["panel_bg"])
        self.content_frame.configure(bg=palette["app_bg"])
        self.footer_frame.configure(bg=palette["app_bg"])
        self.title_label.configure(bg=palette["app_bg"], fg=palette["text"])
        self.status_label.configure(bg=palette["app_bg"], fg=palette["muted"])
        self.source_label.configure(bg=palette["app_bg"], fg=palette["muted"])
        self.search_entry.configure(bg=palette["field_bg"], fg=palette["text"], insertbackground=palette["text"])
        self.skill_menu_button.configure(
            bg=palette["field_bg"],
            fg=palette["text"],
            activebackground=palette["control_hover"],
            activeforeground=palette["text"],
        )
        for widget in self.ui_widgets:
            if isinstance(widget, tk.Frame):
                widget.configure(bg=palette["field_border"])
            elif isinstance(widget, tk.Label):
                widget.configure(bg=palette["panel_bg"], fg=palette["muted"])
            elif isinstance(widget, tk.Button):
                if hasattr(widget, "variable"):
                    self.update_toggle_button(widget)
                else:
                    widget.configure(
                        bg=palette["control_bg"],
                        fg=palette["text"],
                        activebackground=palette["control_hover"],
                        activeforeground=palette["text"],
                    )
        self.rebuild_skill_menu()
        self.canvas.configure(bg=palette["app_bg"])
        self.cards_frame.configure(bg=palette["app_bg"])
        if self.empty_label is not None:
            self.empty_label.configure(bg=palette["app_bg"], fg=palette["empty"])
        for skill in self.card_widgets:
            self.update_skill_card(skill)
        self.update_status()

    def update_status(self) -> None:
        found_count = sum(1 for book in self.books if self.progress.get(book.key, False))
        complete_skills = sum(1 for skill in SKILL_BOOKS if self.skill_complete(skill))
        self.status_var.set(
            self.t(
                "found_status",
                found=found_count,
                total=len(self.books),
                complete=complete_skills,
                skills=len(SKILL_BOOKS),
            )
        )

    def selected_skill(self) -> str | None:
        return self.selected_skill_key

    def skill_complete(self, skill: str) -> bool:
        return all(self.progress.get(f"{skill}:{volume}", False) for volume, _levels, _pages in VOLUME_META)

    def create_skill_card(self, skill: str, books: list[Book]) -> None:
        palette = self.palette
        complete = self.skill_complete(skill)
        accent = SKILL_COLORS[skill]
        card_bg = self.skill_card_bg(skill, complete)
        border = self.skill_border(skill, complete)
        card = tk.Frame(self.cards_frame, bg=border, padx=1, pady=1)

        inner = tk.Frame(card, bg=card_bg, padx=12, pady=12)
        inner.pack(fill=tk.BOTH, expand=True)

        title_row = tk.Frame(inner, bg=card_bg)
        title_row.pack(fill=tk.X)

        image = self.skill_images.get(skill)
        image_label = tk.Label(title_row, bg=card_bg, bd=0)
        if image is not None:
            image_label.configure(image=image)
        image_label.pack(side=tk.LEFT, padx=(0, 8))

        title = tk.Label(
            title_row,
            text=self.skill_label(skill),
            bg=card_bg,
            fg=palette["text"],
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        emoji_image = self.emoji_images.get(skill)
        emoji_label = tk.Label(title_row, bg=card_bg, bd=0, width=EMOJI_ICON_SIZE, height=EMOJI_ICON_SIZE)
        if emoji_image is not None:
            emoji_label.configure(image=emoji_image)
            emoji_label.pack(side=tk.RIGHT, padx=(8, 0))

        subtitle_text = (
            self.t("volumes_complete") if complete else self.t("volumes", count=self.skill_found_count(skill))
        )
        subtitle = tk.Label(
            inner,
            text=subtitle_text,
            bg=card_bg,
            fg=palette["muted_complete"] if complete else palette["muted"],
            font=("Segoe UI", 9),
            anchor="w",
        )
        subtitle.pack(fill=tk.X, pady=(2, 10))

        buttons = tk.Frame(inner, bg=card_bg)
        buttons.pack(fill=tk.X)

        button_widgets = {}
        for book in books:
            found = self.progress.get(book.key, False)
            button = tk.Button(
                buttons,
                text=self.t("volume", volume=book.volume),
                command=lambda key=book.key: self.toggle_book(key),
                bg=palette["found_bg"] if found else palette["button_bg"],
                fg=palette["found_fg"] if found else palette["button_fg"],
                activebackground=palette["found_active"] if found else palette["button_active"],
                activeforeground=palette["found_fg"] if found else palette["button_fg"],
                relief=tk.FLAT,
                bd=0,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                padx=8,
                pady=8,
            )
            button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
            button.bind("<Enter>", lambda _event, text=book.title: self.status_var.set(text))
            button.bind("<Leave>", lambda _event: self.update_status())
            button_widgets[book.key] = button

        self.card_widgets[skill] = {
            "card": card,
            "inner": inner,
            "title_row": title_row,
            "emoji_label": emoji_label,
            "image_label": image_label,
            "title": title,
            "subtitle": subtitle,
            "buttons": buttons,
            "book_buttons": button_widgets,
        }

    def skill_found_count(self, skill: str) -> int:
        return sum(1 for volume, _levels, _pages in VOLUME_META if self.progress.get(f"{skill}:{volume}", False))

    def skill_card_bg(self, skill: str, complete: bool) -> str:
        if self.theme_name == "dark":
            return self.mix_colors(SKILL_COLORS[skill], self.palette["card_bg"], 0.24 if complete else 0.15)
        return self.mix_colors(SKILL_COLORS[skill], "#ffffff", 0.24 if complete else 0.12)

    def skill_border(self, skill: str, complete: bool) -> str:
        if self.theme_name == "dark":
            return self.mix_colors(SKILL_COLORS[skill], self.palette["border"], 0.55 if complete else 0.25)
        return SKILL_COLORS[skill] if complete else self.palette["border"]

    def mix_colors(self, first: str, second: str, amount: float) -> str:
        first_rgb = tuple(int(first[index : index + 2], 16) for index in (1, 3, 5))
        second_rgb = tuple(int(second[index : index + 2], 16) for index in (1, 3, 5))
        mixed = tuple(round(a * amount + b * (1 - amount)) for a, b in zip(first_rgb, second_rgb))
        return "#{:02x}{:02x}{:02x}".format(*mixed)

    def update_skill_card(self, skill: str) -> None:
        widgets = self.card_widgets.get(skill)
        if not widgets:
            return

        palette = self.palette
        complete = self.skill_complete(skill)
        accent = SKILL_COLORS[skill]
        card_bg = self.skill_card_bg(skill, complete)
        border = self.skill_border(skill, complete)
        subtitle_text = (
            self.t("volumes_complete") if complete else self.t("volumes", count=self.skill_found_count(skill))
        )

        widgets["card"].configure(bg=border)
        widgets["inner"].configure(bg=card_bg)
        widgets["title_row"].configure(bg=card_bg)
        widgets["emoji_label"].configure(bg=card_bg)
        widgets["image_label"].configure(bg=card_bg)
        widgets["title"].configure(bg=card_bg, fg=palette["text"])
        widgets["title"].configure(text=self.skill_label(skill))
        widgets["subtitle"].configure(
            text=subtitle_text,
            bg=card_bg,
            fg=palette["muted_complete"] if complete else palette["muted"],
        )
        widgets["buttons"].configure(bg=card_bg)

        for book in self.books_for_skill(skill):
            button = widgets["book_buttons"].get(book.key)
            if button is None:
                continue
            found = self.progress.get(book.key, False)
            button.configure(
                text=self.t("volume", volume=book.volume),
                bg=palette["found_bg"] if found else palette["button_bg"],
                fg=palette["found_fg"] if found else palette["button_fg"],
                activebackground=palette["found_active"] if found else palette["button_active"],
                activeforeground=palette["found_fg"] if found else palette["button_fg"],
            )

    def layout_cards(self, visible_skills: list[str] | None = None) -> None:
        if not self.card_widgets:
            return
        if visible_skills is None:
            visible_skills = self.visible_skills()
        width = max(self.canvas.winfo_width(), 1)
        columns = max(1, width // 370)
        for index, skill in enumerate(visible_skills):
            card = self.card_widgets[skill]["card"]
            row = index // columns
            column = index % columns
            card.grid(row=row, column=column, sticky="nsew", padx=8, pady=8)
        for column in range(columns):
            self.cards_frame.grid_columnconfigure(column, weight=1, minsize=350)

    def toggle_book(self, key: str) -> None:
        self.progress[key] = not self.progress.get(key, False)
        skill = key.split(":", 1)[0]
        self.update_skill_card(skill)
        self.update_status()
        self.schedule_save()

    def mark_visible_found(self) -> None:
        for book in self.filtered_books():
            self.progress[book.key] = True
        self.save_progress()
        self.refresh()

    def clear_visible(self) -> None:
        for book in self.filtered_books():
            self.progress[book.key] = False
        self.save_progress()
        self.refresh()

    def reset_all(self) -> None:
        if not messagebox.askyesno(self.t("reset_title"), self.t("reset_confirm")):
            return
        self.progress = {}
        self.save_progress()
        self.refresh()


if __name__ == "__main__":
    BookCheckerApp().mainloop()
