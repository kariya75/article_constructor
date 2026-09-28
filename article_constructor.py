from pathlib import Path

import pandas as pd
import streamlit as st

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data():
    """Load constructor configuration from CSV files.

    Returns:
        tuple: Loaded parameters, values, rules, and article template.
    """
    parameters = pd.read_csv(
        DATA_DIR / "parameters.csv",
        encoding="utf-8-sig",
    )

    values = pd.read_csv(
        DATA_DIR / "values.csv",
        encoding="utf-8-sig",
    )

    rules = pd.read_csv(
        DATA_DIR / "rules.csv",
        encoding="utf-8-sig",
    )

    template = pd.read_csv(
        DATA_DIR / "article_template.csv",
        encoding="utf-8-sig",
    )

    return parameters, values, rules, template


# ============================================================
# HELPERS
# ============================================================

def get_values(values, parameter):
    """Get available values for a parameter.

    Args:
        values: DataFrame containing parameter values.
        parameter: Internal parameter name.

    Returns:
        DataFrame: Values belonging to the requested parameter.
    """
    return values[values["parameter"] == parameter].copy()


def get_rule(
        rules,
        rule_type,
        parameter,
        condition_parameter=None,
        condition_value=None,
):
    """Find a specific constructor rule.

    Args:
        rules: DataFrame containing constructor rules.
        rule_type: Rule type to search for.
        parameter: Parameter affected by the rule.
        condition_parameter: Optional parameter used as a condition.
        condition_value: Optional condition value.

    Returns:
        DataFrame: Matching rules.
    """
    result = rules[
        (rules["rule"] == rule_type)
        & (rules["parameter"] == parameter)
        ]

    if condition_parameter is not None:
        result = result[
            result["condition_parameter"] == condition_parameter
            ]

    if condition_value is not None:
        result = result[
            result["condition_value"].astype(str) == str(condition_value)
            ]

    return result


def generate_range(min_value, max_value, step):
    """Generate integer values for a numeric range.

    Args:
        min_value: Minimum value.
        max_value: Maximum value.
        step: Step between values.

    Returns:
        list: Generated integer values.
    """
    return list(
        range(
            int(min_value),
            int(max_value) + 1,
            int(step),
        )
    )


def format_lens(lens, angle=None, shb_size=None):
    """Format the lens part of the article.

    Args:
        lens: Lens type.
        angle: Lens angle.
        shb_size: Additional SHB lens angle.

    Returns:
        str: Formatted lens part of the article.
    """
    if lens == "Д":
        return "Д"

    if lens == "ШБ":
        return f"ШБ{angle}*{shb_size}"

    return f"{lens}{angle}"


def format_power(max_power, installed_power):
    """Format maximum and installed power.

    Args:
        max_power: Maximum factory power.
        installed_power: Installed power selected by the user.

    Returns:
        str: Formatted power part of the article.
    """
    return f"{max_power}/{installed_power}"


def format_article(
        model,
        max_power,
        installed_power,
        cri,
        lens,
        angle,
        shb_size,
        cct,
        ip,
        glass,
        mounting,
        lamps=None,
):
    """Generate a complete article from selected parameters.

    Args:
        model: Selected model.
        max_power: Maximum factory power.
        installed_power: Installed power.
        cri: Color rendering index.
        lens: Lens type.
        angle: Lens angle.
        shb_size: Additional SHB lens angle.
        cct: Color temperature.
        ip: Ingress protection rating.
        glass: Glass type.
        mounting: Mounting type.
        lamps: Number of lamps for Spinel.

    Returns:
        str: Complete article.
    """
    model_values = {
        "Шпинель": "ШПИНЕЛЬ",
        "Оникс": "ОНИКС",
    }

    cri_values = {
        70: "Ra70",
        80: "Ra80",
        90: "Ra90",
    }

    cct_values = {
        3000: "3000К",
        4000: "4000К",
        5000: "5000К",
    }

    ip_values = {
        66: "IP66",
        67: "IP67",
        68: "IP68",
    }

    glass_values = {
        "Прозрачный": "ПРОЗ",
        "Опал": "ОПАЛ",
    }

    mounting_values = {
        "Консоль": "1",
        "Кронштейн": "2",
        "Подвесное (трос)": "3",
        "Поворотное (лира)": "5",
        "Накладное": "6",
        "Грунт": "11",
        "Универсальное (консоль/кронштейн)": "12",
    }

    lamps_values = {
        1: "I",
        2: "II",
        3: "III",
    }

    article_parts = [
        "Светильник светодиодный",
        model_values[model],
        format_power(max_power, installed_power),
        cri_values[cri],
        format_lens(
            lens=lens,
            angle=angle,
            shb_size=shb_size,
        ),
        cct_values[cct],
        ip_values[ip],
        glass_values[glass],
        mounting_values[mounting],
    ]

    if model == "Шпинель":
        article_parts.append(lamps_values[lamps])

    return " ".join(article_parts)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Конструктор артикула",
    page_icon="💡",
    layout="centered",
)

st.title("Конструктор артикула")
st.caption("Прототип конструктора светильников")

# ============================================================
# LOAD DATA
# ============================================================

try:
    parameters, values, rules, template = load_data()
except FileNotFoundError as error:
    st.error(
        "Не удалось найти один из файлов конфигурации: "
        f"{error.filename}"
    )
    st.stop()

# ============================================================
# MODEL
# ============================================================

model_options = get_values(values, "model")

model = st.selectbox(
    "Модель",
    model_options["display"].tolist(),
)

# ============================================================
# MAXIMUM POWER
# ============================================================

max_power_rule = get_rule(
    rules,
    rule_type="range",
    parameter="max_power",
)

max_power_row = max_power_rule.iloc[0]

max_power_values = generate_range(
    max_power_row["min_value"],
    max_power_row["max_value"],
    max_power_row["step"],
)

max_power = st.selectbox(
    "Мощность максимальная, Вт",
    max_power_values,
)

# ============================================================
# INSTALLED POWER
# ============================================================

installed_power = st.number_input(
    "Мощность установленная, Вт",
    min_value=20,
    max_value=int(max_power),
    value=min(20, int(max_power)),
    step=2,
)

if installed_power > max_power:
    st.error(
        "Установленная мощность не может быть больше "
        "максимальной мощности."
    )
    st.stop()

if installed_power % 2 != 0:
    st.warning(
        "Установленная мощность должна задаваться с шагом 2 Вт."
    )

# ============================================================
# CRI
# ============================================================

cri_values = get_values(values, "cri")

cri = st.selectbox(
    "Индекс цветопередачи",
    cri_values["value"].astype(int).tolist(),
    format_func=lambda value: f"Ra{value}",
)

# ============================================================
# LENS
# ============================================================

lens_values = get_values(values, "lens")

lens = st.selectbox(
    "Тип линзы",
    lens_values["value"].tolist(),
)

# ============================================================
# LENS ANGLE
# ============================================================

angle = None

if lens == "Д":
    angle = None

elif lens == "ШБ":
    angle_values = generate_range(
        15,
        180,
        5,
    )

    angle = st.selectbox(
        "Угол линзы",
        angle_values,
    )

else:
    angle_rule = get_rule(
        rules,
        rule_type="range",
        parameter="angle",
        condition_parameter="lens",
        condition_value=lens,
    )

    if angle_rule.empty:
        st.error(
            f"Для линзы «{lens}» пока не задано правило "
            "допустимых углов."
        )
        st.stop()

    angle_row = angle_rule.iloc[0]

    angle_values = generate_range(
        angle_row["min_value"],
        angle_row["max_value"],
        angle_row["step"],
    )

    angle = st.selectbox(
        "Угол линзы",
        angle_values,
    )

# ============================================================
# SHB SIDE LENS ANGLE
# ============================================================

shb_size = None

if lens == "ШБ":
    shb_size = st.selectbox(
        "Угол боковой линзы",
        [50, 75],
    )

# ============================================================
# CCT
# ============================================================

cct_values = get_values(values, "cct")

cct = st.selectbox(
    "Цветовая температура",
    cct_values["value"].astype(int).tolist(),
    format_func=lambda value: f"{value} К",
)

# ============================================================
# IP
# ============================================================

ip_values = get_values(values, "ip")

ip = st.selectbox(
    "Степень защиты",
    ip_values["value"].astype(int).tolist(),
    format_func=lambda value: f"IP{value}",
)

# ============================================================
# GLASS
# ============================================================

glass_values = get_values(values, "glass")

glass = st.selectbox(
    "Тип стекла",
    glass_values["display"].tolist(),
)

# ============================================================
# MOUNTING
# ============================================================

mounting_values = get_values(values, "mounting")

mounting = st.selectbox(
    "Тип крепления",
    mounting_values["display"].tolist(),
)

# ============================================================
# NUMBER OF LAMPS
# ============================================================

lamps = None

if model == "Шпинель":
    lamps_values = get_values(values, "lamps")

    lamps = st.selectbox(
        "Количество оптических блоков",
        lamps_values["value"].astype(int).tolist(),
    )

# ============================================================
# ARTICLE GENERATION
# ============================================================

st.divider()

if st.button(
    "Получить артикул",
    type="primary",
    use_container_width=True,
):
    article = format_article(
        model=model,
        max_power=max_power,
        installed_power=installed_power,
        cri=cri,
        lens=lens,
        angle=angle,
        shb_size=shb_size,
        cct=cct,
        ip=ip,
        glass=glass,
        mounting=mounting,
        lamps=lamps,
    )

    st.session_state["article"] = article

if "article" in st.session_state:
    st.success("Артикул сформирован")

    st.code(
        st.session_state["article"],
        language=None,
    )

    if st.button(
        "Сформировать паспорт изделия",
        use_container_width=True,
    ):
        st.success("Паспорт сформирован")