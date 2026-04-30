"""
azure_diagrams.py — Azure Architecture & Data Flow Diagram Module
==================================================================
Generates publication-quality architecture diagrams using actual Azure SVG icons.
Designed to be called by docx-beautify and pptx-beautify skills.

Dependencies: pip install matplotlib Pillow cairosvg cairocffi
              + MSYS2 64-bit cairo DLLs in C:\\Users\\<USER>\\tools\\cairo-dlls\\

Usage:
    from azure_diagrams import generate_architecture_diagram, generate_data_flow_diagram

    # Architecture diagram with Azure icons
    nodes = [
        Node("App Service", "app_services", x=2, y=3),
        Node("Azure OpenAI", "azure_openai", x=5, y=3),
        Node("Cosmos DB", "cosmos_db", x=8, y=3),
    ]
    connections = [
        Connection("App Service", "Azure OpenAI", "REST API"),
        Connection("Azure OpenAI", "Cosmos DB", "Session Store"),
    ]
    generate_architecture_diagram(nodes, connections, "output.png")
"""

import os
import sys
import io
import glob
import tempfile
import textwrap
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Union, Callable
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# CAIROSVG BOOTSTRAP — Must happen before any cairosvg import
# ═══════════════════════════════════════════════════════════════════════════

CAIRO_DLL_DIR = r"<USER_HOME>/tools\cairo-dlls"

def _bootstrap_cairo():
    """Add MSYS2 64-bit cairo DLLs to PATH so cairocffi can find libcairo-2.dll."""
    if os.path.isdir(CAIRO_DLL_DIR):
        try:
            os.add_dll_directory(CAIRO_DLL_DIR)
        except (OSError, AttributeError):
            pass
        if CAIRO_DLL_DIR not in os.environ.get("PATH", ""):
            os.environ["PATH"] = CAIRO_DLL_DIR + ";" + os.environ.get("PATH", "")

_bootstrap_cairo()

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except (ImportError, OSError):
    CAIROSVG_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    from matplotlib.lines import Line2D
    import matplotlib.patheffects as path_effects
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

ICON_BASE_DIR = (
    r"<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification"
    r"\Azure_Public_Service_Icons_V23\Azure_Public_Service_Icons\Icons"
)

# Output presets for different document formats
OUTPUT_PRESETS = {
    "docx_portrait": {
        "figsize": (6.5, 4.5),    # inches — fits portrait A4/Letter with margins
        "dpi": 200,
        "max_width_in": 6.1,
        "font_scale": 1.0,
        "icon_size": 48,
    },
    "docx_landscape": {
        "figsize": (9.5, 5.5),    # inches — fits landscape A4/Letter
        "dpi": 200,
        "max_width_in": 9.0,
        "font_scale": 1.1,
        "icon_size": 56,
    },
    "pptx": {
        "figsize": (11.5, 5.8),   # inches — fits 13.333" x 7.5" widescreen slide
        "dpi": 200,
        "max_width_in": 11.0,
        "font_scale": 1.2,
        "icon_size": 56,
    },
    "pptx_half": {
        "figsize": (5.5, 5.0),    # half-slide for side-by-side layouts
        "dpi": 200,
        "max_width_in": 5.0,
        "font_scale": 0.9,
        "icon_size": 40,
    },
    "standalone": {
        "figsize": (12, 8),       # large standalone image
        "dpi": 200,
        "max_width_in": 12.0,
        "font_scale": 1.3,
        "icon_size": 64,
    },
}

# Fluke/Fortive brand colors
COLORS = {
    "primary":       "#1E2761",
    "secondary":     "#4472C4",
    "accent":        "#ED7D31",
    "success":       "#70AD47",
    "warning":       "#FFC220",
    "danger":        "#C00000",
    "info":          "#17A2B8",
    "light_bg":      "#F8F9FA",
    "white":         "#FFFFFF",
    "dark_text":     "#2D2D2D",
    "medium_text":   "#555555",
    "light_text":    "#888888",
    "border":        "#CCCCCC",
    "boundary":      "#888888",
    "arrow":         "#555555",
    "arrow_label":   "#444444",
    # Azure service category colors (from official Azure portal palette)
    "azure_compute":   "#0078D4",
    "azure_network":   "#4A90D9",
    "azure_storage":   "#3AAA5B",
    "azure_database":  "#A060C0",
    "azure_ai":        "#0078D4",
    "azure_security":  "#E74856",
    "azure_identity":  "#FFB900",
    "azure_monitor":   "#00B7C3",
    "azure_devops":    "#0078D4",
    "azure_web":       "#0078D4",
    "azure_container": "#326DE6",
    "azure_integration": "#742774",
}

# Semi-transparent fills for boundary boxes
BOUNDARY_FILLS = {
    "subscription":    "#E8F0FE20",   # very light blue
    "resource_group":  "#F0F7FF40",   # light blue
    "vnet":            "#E8F5E920",   # light green
    "agent_group":     "#FFF8E120",   # light gold
    "security":        "#FDE8E820",   # light red
    "data":            "#F3E5F520",   # light purple
    "user":            "#FFF3E020",   # light orange
    "default":         "#F5F5F520",   # light gray
}


# ═══════════════════════════════════════════════════════════════════════════
# ICON REGISTRY — Name-based lookup for Azure SVG icons
# ═══════════════════════════════════════════════════════════════════════════

# Canonical name → (search_pattern, category_hint)
# Search pattern matches against SVG filenames; category_hint for disambiguation
ICON_REGISTRY = {
    # AI + Machine Learning
    "azure_openai":          ("03438", "ai + machine learning"),
    "ai_services":           ("02749", "ai + machine learning"),
    "cognitive_search":      ("10044", "ai + machine learning"),
    "bot_services":          ("10165", "ai + machine learning"),
    "machine_learning":      ("00030", "ai + machine learning"),
    "cognitive_services":    ("03173", "ai + machine learning"),
    "ai_search":             ("10044", "ai + machine learning"),

    # Analytics
    "databricks":            ("10787", "analytics"),
    "data_factory":          ("10126", "analytics"),
    "data_factories":        ("10126", "analytics"),
    "adf":                   ("10126", "analytics"),
    "synapse":               ("00606", "analytics"),
    "event_hubs":            ("00039", "analytics"),
    "log_analytics":         ("00009", "analytics"),
    "analysis_services":     ("10148", "analytics"),
    "power_bi":              ("03332", "analytics"),
    "power_bi_embedded":     ("03332", "analytics"),
    "stream_analytics":      ("00042", "analytics"),

    # App Services
    "app_services":          ("10035", "app services"),
    "app_service_plan":      ("00046", "app services"),
    "cdn_profiles":          ("00056", "app services"),

    # Compute
    "virtual_machine":       ("10021", "compute"),
    "function_apps":         ("10029", "compute"),
    "kubernetes":            ("10023", "compute"),
    "batch":                 ("10031", "compute"),

    # Containers
    "container_registries":  ("10105", "containers"),
    "container_instances":   ("10104", "containers"),
    "container_apps":        ("02856", "containers"),

    # Databases
    "cosmos_db":             ("10121", "databases"),
    "sql_database":          ("10130", "databases"),
    "sql_server":            ("10132", "databases"),
    "mysql":                 ("10122", "databases"),
    "postgresql":            ("10131", "databases"),
    "cache_redis":           ("10137", "databases"),
    "sql_managed":           ("10136", "databases"),
    "oracle_database":       ("03490", "databases"),

    # DevOps
    "application_insights":  ("00012", "devops"),
    "api_management":        ("10042", "devops"),
    "devops_starter":        ("03339", "devops"),

    # General
    "resource_groups":       ("10007", "general"),
    "blob_block":            ("10780", "general"),
    "storage_queue":         ("10840", "general"),
    "tag":                   ("10006", "general"),

    # Identity
    "entra_connect":         ("02854", "identity"),
    "users":                 ("10230", "identity"),
    "managed_identities":    ("10227", "identity"),
    "entra_roles":           ("10340", "identity"),
    "entra_custom_roles":    ("02680", "identity"),
    "app_registrations":     ("10232", "identity"),

    # Integration
    "service_bus":           ("10836", "integration"),
    "logic_apps":            ("02631", "integration"),
    "event_grid":            ("10206", "integration"),
    "app_configuration":     ("10219", "integration"),

    # Management + Governance
    "policy":                ("10316", "management + governance"),
    "blueprints":            ("10313", "management + governance"),
    "cost_management":       ("10350", "management + governance"),

    # Monitor
    "monitor":               ("03585", "hybrid + multicloud"),
    "network_watcher":       ("10066", "monitor"),

    # Networking
    "virtual_networks":      ("10061", "networking"),
    "load_balancers":        ("10062", "networking"),
    "application_gateways":  ("10076", "networking"),
    "front_door":            ("10073", "networking"),
    "dns_zones":             ("10064", "networking"),
    "firewall":              ("00271", "networking"),
    "vnet_gateways":         ("10063", "networking"),
    "waf":                   ("10362", "networking"),
    "private_endpoints":     ("02579", "networking"),
    "nsg":                   ("10067", "networking"),

    # Security
    "key_vaults":            ("10245", "security"),
    "security_center":       ("10241", "security"),
    "sentinel":              ("10244", "security"),

    # Storage
    "storage_accounts":      ("10086", "storage"),
    "data_lake":             ("10091", "storage"),
    "file_shares":           ("10839", "storage"),

    # Web
    "signalr":               ("10052", "web"),
    "static_apps":           ("01007", "web"),

    # Azure Stack / Subscription
    "subscriptions":         ("10111", "azure stack"),

    # Other
    "web_app_database":      ("02515", "other"),
}

# Icon cache — avoid re-converting SVGs on repeated calls
_icon_cache: Dict[str, "Image.Image"] = {}


def _find_icon_path(icon_name: str) -> Optional[str]:
    """Resolve an icon name to its SVG file path."""
    if icon_name not in ICON_REGISTRY:
        # Try fuzzy match against filenames
        all_svgs = glob.glob(os.path.join(ICON_BASE_DIR, "**", "*.svg"), recursive=True)
        for svg in all_svgs:
            if icon_name.lower().replace("_", "-") in os.path.basename(svg).lower():
                return svg
        return None

    code, category = ICON_REGISTRY[icon_name]
    # Search in category first for speed
    category_dir = os.path.join(ICON_BASE_DIR, category)
    if os.path.isdir(category_dir):
        matches = glob.glob(os.path.join(category_dir, f"*{code}*.svg"))
        if matches:
            return matches[0]
    # Fallback: search all categories
    matches = glob.glob(os.path.join(ICON_BASE_DIR, "**", f"*{code}*.svg"), recursive=True)
    return matches[0] if matches else None


def load_icon(icon_name: str, size: int = 64) -> Optional["Image.Image"]:
    """Load an Azure icon as a PIL Image, converting from SVG via cairosvg.

    Args:
        icon_name: Registry key (e.g., 'app_services', 'cosmos_db') or partial filename
        size: Output size in pixels (square)

    Returns:
        PIL Image or None if icon not found or cairosvg unavailable
    """
    cache_key = f"{icon_name}_{size}"
    if cache_key in _icon_cache:
        return _icon_cache[cache_key].copy()

    if not CAIROSVG_AVAILABLE or not PILLOW_AVAILABLE:
        return None

    svg_path = _find_icon_path(icon_name)
    if not svg_path:
        return None

    try:
        png_data = cairosvg.svg2png(url=svg_path, output_width=size, output_height=size)
        img = Image.open(io.BytesIO(png_data)).convert("RGBA")
        _icon_cache[cache_key] = img.copy()
        return img
    except Exception:
        return None


def list_icons() -> Dict[str, str]:
    """Return dict of all registered icon names → SVG paths (or 'NOT FOUND')."""
    result = {}
    for name in sorted(ICON_REGISTRY.keys()):
        path = _find_icon_path(name)
        result[name] = path or "NOT FOUND"
    return result


# ═══════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Node:
    """A service/component node in a diagram."""
    label: str                          # Display name (e.g., "App Service")
    icon: str = ""                      # Icon registry key (e.g., "app_services")
    x: float = 0.0                      # X position (in diagram units)
    y: float = 0.0                      # Y position (in diagram units)
    sublabel: str = ""                  # Subtitle text (e.g., "FastAPI Backend")
    color: str = ""                     # Override color (hex)
    width: float = 1.2                  # Node width
    height: float = 1.2                 # Node height
    style: str = "icon"                 # "icon", "box", "hexagon", "circle", "pill"
    metadata: Dict = field(default_factory=dict)


@dataclass
class Connection:
    """A connection/arrow between two nodes."""
    from_node: str                      # Source node label
    to_node: str                        # Target node label
    label: str = ""                     # Arrow label text
    style: str = "solid"               # "solid", "dashed", "dotted"
    color: str = ""                     # Override color
    arrow_style: str = "-|>"           # Matplotlib arrow style
    bidirectional: bool = False        # Double-headed arrow
    curve: float = 0.0                 # Connection curvature (0=straight)


@dataclass
class Boundary:
    """A boundary box grouping nodes."""
    label: str                          # Boundary title (e.g., "Azure Subscription")
    x: float = 0.0                      # Left edge
    y: float = 0.0                      # Bottom edge
    width: float = 5.0                  # Box width
    height: float = 3.0                 # Box height
    style: str = "dashed"              # "dashed", "solid", "dotted"
    color: str = ""                     # Border color override
    fill: str = ""                      # Fill color (hex with alpha)
    fill_type: str = "default"         # Key into BOUNDARY_FILLS
    corner_radius: float = 0.15        # Rounded corner radius
    label_position: str = "top_left"   # "top_left", "top_center", "bottom_left"
    nest_level: int = 0                # For nested boundaries (affects z-order)


@dataclass
class DiagramConfig:
    """Configuration for diagram generation."""
    output_preset: str = "docx_portrait"  # Key into OUTPUT_PRESETS
    title: str = ""                       # Diagram title
    subtitle: str = ""                    # Subtitle text
    background: str = "#FFFFFF"           # Background color
    padding: float = 0.5                  # Padding around content
    font_family: str = "Calibri"          # Primary font
    show_title: bool = True               # Show title on diagram
    show_legend: bool = False             # Show color legend
    # Overrides (take precedence over preset)
    figsize: Optional[Tuple[float, float]] = None
    dpi: Optional[int] = None
    icon_size: Optional[int] = None


# ═══════════════════════════════════════════════════════════════════════════
# CORE RENDERING ENGINE
# ═══════════════════════════════════════════════════════════════════════════

def _get_preset(config: DiagramConfig) -> dict:
    """Resolve output preset with any overrides."""
    preset = OUTPUT_PRESETS.get(config.output_preset, OUTPUT_PRESETS["docx_portrait"]).copy()
    if config.figsize:
        preset["figsize"] = config.figsize
    if config.dpi:
        preset["dpi"] = config.dpi
    if config.icon_size:
        preset["icon_size"] = config.icon_size
    return preset


def _create_figure(config: DiagramConfig) -> Tuple:
    """Create a matplotlib figure with proper sizing."""
    preset = _get_preset(config)
    fig, ax = plt.subplots(figsize=preset["figsize"])
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(config.background)
    ax.set_facecolor(config.background)
    return fig, ax, preset


def _draw_boundary(ax, boundary: Boundary, preset: dict):
    """Draw a boundary box on the diagram."""
    color = boundary.color or COLORS["boundary"]
    linestyle = {"dashed": "--", "solid": "-", "dotted": ":"}[boundary.style]

    # Fill color
    if boundary.fill:
        fill_color = boundary.fill
    else:
        fill_color = BOUNDARY_FILLS.get(boundary.fill_type, BOUNDARY_FILLS["default"])

    # Parse fill with alpha
    fc = fill_color
    alpha = 0.08
    if len(fill_color) > 7:
        fc = fill_color[:7]
        alpha = int(fill_color[7:9], 16) / 255.0

    rect = FancyBboxPatch(
        (boundary.x, boundary.y), boundary.width, boundary.height,
        boxstyle=f"round,pad={boundary.corner_radius}",
        facecolor=fc, edgecolor=color,
        linewidth=1.5, linestyle=linestyle, alpha=max(alpha, 0.05),
        zorder=1 + boundary.nest_level
    )
    ax.add_patch(rect)

    # Re-draw border on top (since fill alpha affects border too)
    border = FancyBboxPatch(
        (boundary.x, boundary.y), boundary.width, boundary.height,
        boxstyle=f"round,pad={boundary.corner_radius}",
        facecolor="none", edgecolor=color,
        linewidth=1.5, linestyle=linestyle,
        zorder=5 + boundary.nest_level
    )
    ax.add_patch(border)

    # Label
    font_scale = preset.get("font_scale", 1.0)
    label_fs = 8 * font_scale
    if boundary.label_position == "top_left":
        lx, ly = boundary.x + 0.15, boundary.y + boundary.height - 0.05
        ha, va = "left", "top"
    elif boundary.label_position == "top_center":
        lx, ly = boundary.x + boundary.width / 2, boundary.y + boundary.height - 0.05
        ha, va = "center", "top"
    else:
        lx, ly = boundary.x + 0.15, boundary.y + 0.15
        ha, va = "left", "bottom"

    ax.text(lx, ly, boundary.label,
            fontsize=label_fs, fontweight="bold", color=color,
            ha=ha, va=va, fontstyle="italic",
            zorder=10 + boundary.nest_level)


def _draw_node(ax, node: Node, preset: dict):
    """Draw a node (icon + label) on the diagram."""
    icon_size = preset.get("icon_size", 48)
    font_scale = preset.get("font_scale", 1.0)

    if node.style == "icon" and node.icon:
        # Load and render Azure icon
        icon_img = load_icon(node.icon, size=icon_size)
        if icon_img:
            imagebox = OffsetImage(icon_img, zoom=icon_size / 100.0)
            ab = AnnotationBbox(imagebox, (node.x, node.y),
                                frameon=False, zorder=15)
            ax.add_artist(ab)
        else:
            # Fallback: colored circle with first letter
            _draw_fallback_node(ax, node, preset)
    elif node.style == "box":
        color = node.color or COLORS["secondary"]
        box = FancyBboxPatch(
            (node.x - node.width / 2, node.y - node.height / 2),
            node.width, node.height,
            boxstyle="round,pad=0.06",
            facecolor=color, edgecolor="none",
            alpha=0.9, zorder=15
        )
        ax.add_patch(box)
        ax.text(node.x, node.y, node.label,
                fontsize=8 * font_scale, fontweight="bold",
                color="white", ha="center", va="center", zorder=16)
        return  # box style handles its own label
    elif node.style == "hexagon":
        _draw_hexagon(ax, node, preset)
    elif node.style == "pill":
        _draw_pill(ax, node, preset)
    elif node.style == "circle":
        color = node.color or COLORS["secondary"]
        circle = plt.Circle((node.x, node.y), node.width / 2,
                             facecolor=color, edgecolor="none",
                             alpha=0.9, zorder=15)
        ax.add_patch(circle)
        ax.text(node.x, node.y, node.label,
                fontsize=7 * font_scale, fontweight="bold",
                color="white", ha="center", va="center", zorder=16,
                wrap=True)
        return
    else:
        _draw_fallback_node(ax, node, preset)

    # Label below icon — use smaller font to prevent overlap on dense diagrams
    label_y = node.y - 0.50
    label_fontsize = min(8, 7.5) * font_scale
    ax.text(node.x, label_y, node.label,
            fontsize=label_fontsize, fontweight="bold",
            color=COLORS["dark_text"], ha="center", va="top",
            zorder=20)

    # Sublabel below label
    if node.sublabel:
        sublabel_y = label_y - 0.25
        ax.text(node.x, sublabel_y, node.sublabel,
                fontsize=6 * font_scale, color=COLORS["medium_text"],
                ha="center", va="top", zorder=20)


def _draw_fallback_node(ax, node: Node, preset: dict):
    """Draw a colored rounded box when icon is not available."""
    color = node.color or COLORS["secondary"]
    font_scale = preset.get("font_scale", 1.0)
    box = FancyBboxPatch(
        (node.x - 0.35, node.y - 0.35), 0.7, 0.7,
        boxstyle="round,pad=0.08",
        facecolor=color, edgecolor="none", alpha=0.85, zorder=15
    )
    ax.add_patch(box)
    # First letter as icon substitute
    initials = "".join(w[0] for w in node.label.split()[:2]).upper()
    ax.text(node.x, node.y, initials,
            fontsize=14 * font_scale, fontweight="bold",
            color="white", ha="center", va="center", zorder=16)


def _draw_hexagon(ax, node: Node, preset: dict):
    """Draw a hexagon node (for middleware, proxies, etc.)."""
    import numpy as np
    color = node.color or COLORS["accent"]
    font_scale = preset.get("font_scale", 1.0)
    r = node.width / 2
    angles = np.linspace(0, 2 * np.pi, 7)
    xs = node.x + r * np.cos(angles)
    ys = node.y + r * np.sin(angles)
    hex_patch = plt.Polygon(list(zip(xs, ys)),
                             facecolor=color, edgecolor="none",
                             alpha=0.9, zorder=15)
    ax.add_patch(hex_patch)
    ax.text(node.x, node.y, node.label,
            fontsize=7 * font_scale, fontweight="bold",
            color="white", ha="center", va="center", zorder=16)


def _draw_pill(ax, node: Node, preset: dict):
    """Draw a pill/capsule shaped node."""
    color = node.color or COLORS["success"]
    font_scale = preset.get("font_scale", 1.0)
    pill = FancyBboxPatch(
        (node.x - node.width / 2, node.y - node.height / 4),
        node.width, node.height / 2,
        boxstyle="round,pad=0.2",
        facecolor=color, edgecolor="none",
        alpha=0.9, zorder=15
    )
    ax.add_patch(pill)
    ax.text(node.x, node.y, node.label,
            fontsize=7 * font_scale, fontweight="bold",
            color="white", ha="center", va="center", zorder=16)


def _draw_connection(ax, conn: Connection, nodes: List[Node], preset: dict):
    """Draw a connection arrow between two nodes."""
    font_scale = preset.get("font_scale", 1.0)

    # Find source and target nodes
    src = next((n for n in nodes if n.label == conn.from_node), None)
    tgt = next((n for n in nodes if n.label == conn.to_node), None)
    if not src or not tgt:
        return

    color = conn.color or COLORS["arrow"]
    linestyle = {"solid": "-", "dashed": "--", "dotted": ":"}[conn.style]

    # Determine connection style
    connectionstyle = "arc3,rad=0"
    if conn.curve != 0:
        connectionstyle = f"arc3,rad={conn.curve}"

    arrow_style = conn.arrow_style
    if conn.bidirectional:
        arrow_style = "<|-|>"

    arrow = FancyArrowPatch(
        (src.x, src.y), (tgt.x, tgt.y),
        arrowstyle=arrow_style,
        connectionstyle=connectionstyle,
        color=color, linewidth=1.5,
        linestyle=linestyle,
        mutation_scale=12,
        shrinkA=30, shrinkB=30,
        zorder=10
    )
    ax.add_patch(arrow)

    # Label at midpoint
    if conn.label:
        mid_x = (src.x + tgt.x) / 2
        mid_y = (src.y + tgt.y) / 2
        # Offset label slightly above the line
        dx = tgt.x - src.x
        dy = tgt.y - src.y
        length = max((dx ** 2 + dy ** 2) ** 0.5, 0.01)
        offset_x = -dy / length * 0.2
        offset_y = dx / length * 0.2

        ax.text(mid_x + offset_x, mid_y + offset_y, conn.label,
                fontsize=6.5 * font_scale, color=COLORS["arrow_label"],
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                          edgecolor="none", alpha=0.85),
                zorder=12)


def _draw_title(ax, config: DiagramConfig, preset: dict):
    """Draw diagram title and subtitle."""
    if not config.show_title or not config.title:
        return
    font_scale = preset.get("font_scale", 1.0)
    fig_w, fig_h = preset["figsize"]

    ax.text(0.5, 0.98, config.title,
            transform=ax.transAxes,
            fontsize=12 * font_scale, fontweight="bold",
            color=COLORS["primary"], ha="center", va="top",
            zorder=30)

    if config.subtitle:
        ax.text(0.5, 0.93, config.subtitle,
                transform=ax.transAxes,
                fontsize=8 * font_scale, color=COLORS["medium_text"],
                ha="center", va="top", zorder=30)


# ═══════════════════════════════════════════════════════════════════════════
# HIGH-LEVEL PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════

def generate_architecture_diagram(
    nodes: List[Node],
    connections: List[Connection],
    output_path: str,
    boundaries: Optional[List[Boundary]] = None,
    config: Optional[DiagramConfig] = None,
) -> str:
    """Generate an architecture diagram with Azure icons, boundaries, and connections.

    Args:
        nodes: List of Node objects defining services/components
        connections: List of Connection objects defining arrows
        output_path: Path to save PNG output
        boundaries: Optional list of Boundary boxes
        config: Diagram configuration (sizing, title, etc.)

    Returns:
        Path to generated PNG file
    """
    if not MATPLOTLIB_AVAILABLE:
        raise RuntimeError("matplotlib is required: pip install matplotlib")

    config = config or DiagramConfig()
    preset = _get_preset(config)

    fig, ax, preset = _create_figure(config)

    # Auto-calculate bounds if not set
    if nodes:
        all_x = [n.x for n in nodes]
        all_y = [n.y for n in nodes]
        pad = config.padding
        x_min, x_max = min(all_x) - pad - 0.5, max(all_x) + pad + 0.5
        y_min, y_max = min(all_y) - pad - 0.8, max(all_y) + pad + 0.5

        if boundaries:
            for b in boundaries:
                x_min = min(x_min, b.x - 0.2)
                x_max = max(x_max, b.x + b.width + 0.2)
                y_min = min(y_min, b.y - 0.2)
                y_max = max(y_max, b.y + b.height + 0.2)

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

    # Draw layers: boundaries → connections → nodes → title
    if boundaries:
        for b in sorted(boundaries, key=lambda b: b.nest_level):
            _draw_boundary(ax, b, preset)

    for conn in connections:
        _draw_connection(ax, conn, nodes, preset)

    for node in nodes:
        _draw_node(ax, node, preset)

    _draw_title(ax, config, preset)

    # Save
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fig.savefig(output_path, dpi=preset["dpi"], bbox_inches="tight",
                facecolor=fig.get_facecolor(), pad_inches=0.1)
    plt.close(fig)
    return output_path


def generate_data_flow_diagram(
    stages: List[Node],
    connections: Optional[List[Connection]] = None,
    output_path: str = "data_flow.png",
    config: Optional[DiagramConfig] = None,
    direction: str = "horizontal",
    boundaries: Optional[List[Boundary]] = None,
) -> str:
    """Generate a data flow diagram with sequential stages.

    If connections are not provided, auto-connects stages in order.
    Direction controls layout: "horizontal" (L→R) or "vertical" (T→B).

    Args:
        stages: Ordered list of Node objects (auto-positioned if x/y are 0)
        connections: Optional explicit connections (auto-generated if None)
        output_path: Path to save PNG
        config: Diagram configuration
        direction: "horizontal" or "vertical"
        boundaries: Optional boundary boxes

    Returns:
        Path to generated PNG
    """
    config = config or DiagramConfig()
    preset = _get_preset(config)

    # Auto-position stages if needed — wider spacing to prevent text overlap
    spacing = 2.6
    for i, stage in enumerate(stages):
        if stage.x == 0 and stage.y == 0:
            if direction == "horizontal":
                stage.x = 1 + i * spacing
                stage.y = 3
            else:
                stage.x = 3
                stage.y = len(stages) * spacing - i * spacing

    # Auto-generate connections
    if connections is None:
        connections = []
        for i in range(len(stages) - 1):
            connections.append(Connection(
                from_node=stages[i].label,
                to_node=stages[i + 1].label,
                style="solid",
            ))

    return generate_architecture_diagram(
        nodes=stages,
        connections=connections,
        output_path=output_path,
        boundaries=boundaries,
        config=config,
    )


def generate_resource_landscape(
    subscriptions: List[Dict],
    output_path: str = "resource_landscape.png",
    config: Optional[DiagramConfig] = None,
) -> str:
    """Generate an Azure resource landscape diagram with nested subscription/RG/service layout.

    Args:
        subscriptions: List of dicts with structure:
            {
                "name": "My Subscription",
                "resource_groups": [
                    {
                        "name": "rg-production",
                        "services": [
                            {"label": "App Service", "icon": "app_services", "sublabel": "FastAPI"},
                            {"label": "Cosmos DB", "icon": "cosmos_db"},
                        ]
                    }
                ]
            }
        output_path: Path to save PNG
        config: Diagram configuration

    Returns:
        Path to generated PNG
    """
    config = config or DiagramConfig()
    preset = _get_preset(config)

    nodes = []
    boundaries = []
    connections = []

    y_offset = 0.5
    sub_padding = 0.4

    for sub_idx, sub in enumerate(subscriptions):
        rg_x = 0.5
        rg_max_y = y_offset
        rg_boundaries = []

        for rg_idx, rg in enumerate(sub.get("resource_groups", [])):
            services = rg.get("services", [])
            cols = min(len(services), 4)
            rows = (len(services) + cols - 1) // cols

            svc_spacing_x = 2.6
            svc_spacing_y = 2.0

            rg_width = max(cols * svc_spacing_x + 0.8, 3.0)
            rg_height = max(rows * svc_spacing_y + 1.0, 2.5)

            # Position services in grid
            for svc_idx, svc in enumerate(services):
                col = svc_idx % cols
                row = svc_idx // cols
                svc_x = rg_x + 1.0 + col * svc_spacing_x
                svc_y = y_offset + rg_height - 0.8 - row * svc_spacing_y

                n = Node(
                    label=svc["label"],
                    icon=svc.get("icon", ""),
                    sublabel=svc.get("sublabel", ""),
                    x=svc_x, y=svc_y,
                    color=svc.get("color", ""),
                )
                nodes.append(n)

            # RG boundary
            rg_boundaries.append(Boundary(
                label=rg["name"],
                x=rg_x, y=y_offset,
                width=rg_width, height=rg_height,
                style="dashed", fill_type="resource_group",
                nest_level=1,
            ))

            rg_max_y = max(rg_max_y, y_offset + rg_height)
            rg_x += rg_width + 0.6

        # Subscription boundary
        sub_width = rg_x - 0.5 + sub_padding
        sub_height = rg_max_y - y_offset + sub_padding * 2 + 0.3
        boundaries.append(Boundary(
            label=sub["name"],
            x=0.1, y=y_offset - sub_padding,
            width=sub_width, height=sub_height,
            style="solid", fill_type="subscription",
            color=COLORS["primary"], nest_level=0,
            label_position="top_left",
        ))
        boundaries.extend(rg_boundaries)

        y_offset = rg_max_y + 1.0

    # Add any explicit connections from subscription data
    for sub in subscriptions:
        for rg in sub.get("resource_groups", []):
            for svc in rg.get("services", []):
                for conn in svc.get("connections", []):
                    connections.append(Connection(
                        from_node=svc["label"],
                        to_node=conn["to"],
                        label=conn.get("label", ""),
                        style=conn.get("style", "solid"),
                    ))

    return generate_architecture_diagram(
        nodes=nodes,
        connections=connections,
        output_path=output_path,
        boundaries=boundaries,
        config=config,
    )


def generate_sequence_flow(
    participants: List[Node],
    messages: List[Dict],
    output_path: str = "sequence_flow.png",
    config: Optional[DiagramConfig] = None,
) -> str:
    """Generate a sequence-style flow diagram showing interactions between participants.

    Args:
        participants: List of Node objects (positioned in a row)
        messages: List of dicts:
            {"from": "Service A", "to": "Service B", "label": "REST API call", "style": "solid"}
        output_path: Path to save PNG
        config: Diagram configuration

    Returns:
        Path to generated PNG
    """
    config = config or DiagramConfig()
    preset = _get_preset(config)

    # Auto-position participants in a horizontal row
    spacing = 2.5
    for i, p in enumerate(participants):
        if p.x == 0 and p.y == 0:
            p.x = 1 + i * spacing
            p.y = len(messages) * 0.6 + 1.5  # top

    fig, ax, preset = _create_figure(config)
    font_scale = preset.get("font_scale", 1.0)

    # Draw participants at top
    for p in participants:
        _draw_node(ax, p, preset)

    # Draw vertical lifelines
    y_bottom = 0.5
    for p in participants:
        ax.plot([p.x, p.x], [p.y - 0.6, y_bottom],
                color=COLORS["border"], linewidth=1, linestyle="--", zorder=5)

    # Draw messages
    for i, msg in enumerate(messages):
        y = participants[0].y - 1.0 - i * 0.6
        src = next((p for p in participants if p.label == msg["from"]), None)
        tgt = next((p for p in participants if p.label == msg["to"]), None)
        if not src or not tgt:
            continue

        color = msg.get("color", COLORS["arrow"])
        style = msg.get("style", "solid")
        linestyle = {"solid": "-", "dashed": "--", "dotted": ":"}[style]

        arrow = FancyArrowPatch(
            (src.x, y), (tgt.x, y),
            arrowstyle="-|>", color=color,
            linewidth=1.5, linestyle=linestyle,
            mutation_scale=10, zorder=10,
        )
        ax.add_patch(arrow)

        # Label above arrow
        mid_x = (src.x + tgt.x) / 2
        ax.text(mid_x, y + 0.12, msg.get("label", ""),
                fontsize=7 * font_scale, color=COLORS["dark_text"],
                ha="center", va="bottom", zorder=12)

        # Step number
        ax.text(0.3, y, f"{i + 1}",
                fontsize=7 * font_scale, fontweight="bold",
                color=COLORS["secondary"], ha="center", va="center",
                zorder=12)

    # Set bounds
    all_x = [p.x for p in participants]
    ax.set_xlim(min(all_x) - 1.5, max(all_x) + 1.0)
    ax.set_ylim(y_bottom - 0.5, max(p.y for p in participants) + 0.8)

    _draw_title(ax, config, preset)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fig.savefig(output_path, dpi=preset["dpi"], bbox_inches="tight",
                facecolor=fig.get_facecolor(), pad_inches=0.1)
    plt.close(fig)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS — Quick diagram generation
# ═══════════════════════════════════════════════════════════════════════════

def quick_architecture(
    services: List[Dict],
    connections: List[Dict],
    output_path: str,
    title: str = "",
    output_preset: str = "docx_portrait",
    boundaries: Optional[List[Dict]] = None,
) -> str:
    """Simplified interface — pass dicts instead of dataclass instances.

    Args:
        services: List of dicts with keys: label, icon, x, y, sublabel (optional)
        connections: List of dicts with keys: from_node, to_node, label (optional), style
        output_path: PNG output path
        title: Diagram title
        output_preset: "docx_portrait", "docx_landscape", "pptx", "pptx_half", "standalone"
        boundaries: Optional list of boundary dicts

    Example:
        quick_architecture(
            services=[
                {"label": "App Service", "icon": "app_services", "x": 2, "y": 3, "sublabel": "FastAPI"},
                {"label": "Azure OpenAI", "icon": "azure_openai", "x": 5, "y": 3},
                {"label": "Cosmos DB", "icon": "cosmos_db", "x": 8, "y": 3},
            ],
            connections=[
                {"from_node": "App Service", "to_node": "Azure OpenAI", "label": "REST API"},
                {"from_node": "App Service", "to_node": "Cosmos DB", "label": "Sessions"},
            ],
            output_path="architecture.png",
            title="System Architecture",
            output_preset="pptx",
        )
    """
    nodes = [Node(**s) for s in services]
    conns = [Connection(**c) for c in connections]
    bounds = [Boundary(**b) for b in (boundaries or [])]
    config = DiagramConfig(
        output_preset=output_preset,
        title=title,
    )
    return generate_architecture_diagram(nodes, conns, output_path, bounds, config)


def quick_flow(
    stages: List[Dict],
    output_path: str,
    title: str = "",
    output_preset: str = "docx_landscape",
    direction: str = "horizontal",
    connections: Optional[List[Dict]] = None,
) -> str:
    """Simplified data flow diagram.

    Args:
        stages: Ordered list of dicts with: label, icon, sublabel (optional)
        output_path: PNG output path
        title: Diagram title
        output_preset: Output format preset
        direction: "horizontal" or "vertical"
        connections: Optional explicit connections (auto-generated if None)

    Example:
        quick_flow(
            stages=[
                {"label": "SharePoint", "icon": "static_apps", "sublabel": "User Interface"},
                {"label": "FastAPI", "icon": "app_services", "sublabel": "Backend"},
                {"label": "Azure OpenAI", "icon": "azure_openai", "sublabel": "LLM"},
                {"label": "Cosmos DB", "icon": "cosmos_db", "sublabel": "Sessions"},
            ],
            output_path="data_flow.png",
            title="End-to-End Data Flow",
            output_preset="pptx",
        )
    """
    stage_nodes = [Node(**s) for s in stages]
    conns = [Connection(**c) for c in connections] if connections else None
    config = DiagramConfig(output_preset=output_preset, title=title)
    return generate_data_flow_diagram(stage_nodes, conns, output_path, config, direction)


def quick_landscape(
    subscriptions: List[Dict],
    output_path: str,
    title: str = "",
    output_preset: str = "docx_landscape",
) -> str:
    """Simplified resource landscape diagram.

    Example:
        quick_landscape(
            subscriptions=[{
                "name": "Fluke AI ML Technology",
                "resource_groups": [{
                    "name": "rg-ai-bi-tool-dev",
                    "services": [
                        {"label": "App Service", "icon": "app_services", "sublabel": "FastAPI"},
                        {"label": "Azure OpenAI", "icon": "azure_openai", "sublabel": "Sonnet + Haiku"},
                        {"label": "Cosmos DB", "icon": "cosmos_db", "sublabel": "Sessions"},
                        {"label": "Key Vault", "icon": "key_vaults", "sublabel": "Secrets"},
                    ]
                }]
            }],
            output_path="landscape.png",
            title="Azure Resource Landscape",
            output_preset="docx_landscape",
        )
    """
    config = DiagramConfig(output_preset=output_preset, title=title)
    return generate_resource_landscape(subscriptions, output_path, config)


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION HELPERS — For use by docx_beautify and pptx_beautify
# ═══════════════════════════════════════════════════════════════════════════

def generate_for_docx(
    diagram_func: Callable,
    output_path: str,
    landscape: bool = False,
    **kwargs,
) -> str:
    """Generate a diagram sized for DOCX embedding.

    Args:
        diagram_func: One of generate_architecture_diagram, generate_data_flow_diagram, etc.
        output_path: Where to save the PNG
        landscape: True for landscape page, False for portrait
        **kwargs: Passed to the diagram function

    Returns:
        Path to generated PNG
    """
    preset_name = "docx_landscape" if landscape else "docx_portrait"
    config = kwargs.pop("config", None) or DiagramConfig()
    config.output_preset = preset_name
    kwargs["config"] = config
    kwargs["output_path"] = output_path
    return diagram_func(**kwargs)


def generate_for_pptx(
    diagram_func: Callable,
    output_path: str,
    half_slide: bool = False,
    **kwargs,
) -> str:
    """Generate a diagram sized for PPTX embedding.

    Args:
        diagram_func: One of generate_architecture_diagram, generate_data_flow_diagram, etc.
        output_path: Where to save the PNG
        half_slide: True for half-slide width (side-by-side layouts)
        **kwargs: Passed to the diagram function

    Returns:
        Path to generated PNG
    """
    preset_name = "pptx_half" if half_slide else "pptx"
    config = kwargs.pop("config", None) or DiagramConfig()
    config.output_preset = preset_name
    kwargs["config"] = config
    kwargs["output_path"] = output_path
    return diagram_func(**kwargs)


# ═══════════════════════════════════════════════════════════════════════════
# MODULE INFO
# ═══════════════════════════════════════════════════════════════════════════

__version__ = "1.0.0"
__all__ = [
    # Data models
    "Node", "Connection", "Boundary", "DiagramConfig",
    # High-level API
    "generate_architecture_diagram",
    "generate_data_flow_diagram",
    "generate_resource_landscape",
    "generate_sequence_flow",
    # Quick convenience functions
    "quick_architecture", "quick_flow", "quick_landscape",
    # Integration helpers
    "generate_for_docx", "generate_for_pptx",
    # Icon utilities
    "load_icon", "list_icons",
    # Constants
    "COLORS", "BOUNDARY_FILLS", "OUTPUT_PRESETS", "ICON_REGISTRY",
]
