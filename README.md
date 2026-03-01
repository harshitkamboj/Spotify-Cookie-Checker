# 🎵 Spotify Cookie Checker V2

Fast, multi-threaded Spotify cookie checker with smart parsing, proxy rotation, retries, detailed account extraction, and Discord/Telegram notifications.

# 📢 Releasing Website soon with multiple cookie checker and much more is 1-2nd week of March

## ⬇️ Download (EXE)

Don’t use Python? Download the prebuilt `.exe`:

- 📦 Releases: https://github.com/harshitkamboj/Spotify-Cookie-Checker/releases
- 🚀 Latest: https://github.com/harshitkamboj/Spotify-Cookie-Checker/releases/latest

## ✨ Features

- ⚡ Fast multi-threaded cookie checking
- 🍪 Supports Netscape `.txt` and JSON cookie formats
- 🔍 Extracts account details:
- plan
- email
- country
- owner/member status (family/duo)
- child account
- family free slots, invite link, and address (when available)
- next payment date (when detectable)
- 🌐 Broad proxy format support (`http`, `https`, `socks4/5`, auth variants)
- 🔁 Retry system with proxy rotation on retryable errors
- 🧠 Built-in dedupe by email (duplicates skipped + counted)
- 🖥️ Two display modes:
- `log` (line-by-line)
- `simple` (dashboard counters)
- 🔔 Discord + Telegram notifications
- 🗂️ Organized output by run + plan + account role

## 📦 Requirements

```bash
pip install -r requirements.txt
```

Optional for SOCKS:

```bash
pip install requests[socks]
```

## 🚀 Quick Start

1. Clone the repo:

```bash
git clone https://github.com/harshitkamboj/Spotify-Cookie-Checker.git
cd Spotify-Cookie-Checker
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Put cookie files in `cookies/`
4. (Optional) Add proxies in `proxy.txt`
5. Configure `config.yml`
6. Run:

```bash
python main.py
```

## 📁 Folder Layout

```text
cookies/         # input cookies
failed/          # invalid/expired
broken/          # malformed/error cases
hits/            # successful outputs
proxy.txt
config.yml
main.py
```

## 🍪 Supported Cookie Formats

### Netscape (`.txt`)

```text
.spotify.com	TRUE	/	FALSE	1234567890	sp_dc	xxx
```

### JSON (`.json`)

```json
[
  {
    "domain": ".spotify.com",
    "path": "/",
    "secure": false,
    "expirationDate": 1234567890,
    "name": "sp_dc",
    "value": "xxx"
  }
]
```

## 🌐 Proxy Formats

One per line in `proxy.txt`:

```text
ip:port
user:pass@ip:port
ip:port@user:pass
http://ip:port
http://user:pass@ip:port
https://user:pass@ip:port
socks4://user:pass@ip:port
socks4a://user:pass@ip:port
socks5://user:pass@ip:port
socks5h://user:pass@ip:port
ip:port:user:pass
user:pass:ip:port
ip:port user:pass
ip:port|user:pass
ip:port;user:pass
ip:port,user:pass
```

Also accepted/normalized:

```text
http:/ip:port
```

## ⚙️ Config (`config.yml`)

### Sections

- `txt_fields` -> controls fields written in output txt files
- `notifications` -> Discord/Telegram settings and mode
- `display` -> console UI mode (`log` or `simple`)
- `retries` -> retry attempts for retryable request/proxy errors

### Example

```yml
txt_fields:
  plan: true
  email: true
  country: true
  owner: true
  free_slots: true
  invite_link: true
  address: true

notifications:
  webhook:
    enabled: false
    url: ""
    mode: "full" # full | invite_address_only
  telegram:
    enabled: false
    bot_token: ""
    chat_id: ""
    mode: "full" # full | invite_address_only

display:
  mode: "log" # log | simple

retries:
  error_proxy_attempts: 3
```

## 🔁 Retry Behavior

- Retries per cookie: `retries.error_proxy_attempts`
- Uses different proxies across retries when available
- Retry status codes: `403`, `429`, `500`, `502`, `503`, `504`
- Retryable failures exhausted -> `broken/`
- Invalid/dead cookie -> `failed/`

## 🧠 Email Dedupe (Built-in)

- First valid account for an email is kept
- Next valid cookies with same email are marked as duplicates
- Duplicates are skipped and counted in stats (no output file)

## 🔔 Notification Modes

### `full`

- Sends full account details
- Sends output txt file
- Discord/Telegram formatting optimized

### `invite_address_only`

- Sends family invite-focused message only for eligible family owners
- Includes free slots, invite link, and address

## 🧾 Output Notes

- Filename format: `<COUNTRY>_github-harshitkamboj_<PLAN>_<RANDOM>.txt`
- Branding line included:
  `Checker By: github.com/harshitkamboj | Website: harshitkamboj.in`

## 🧩 Plan Keys

- `premium`
- `premium_mini`
- `basic_premium`
- `student_premium`
- `student_premium_hulu`
- `duo_premium`
- `family_premium_v2`
- `family_basic`
- `free`
- `unknown`

## 🤝 Support

- ⭐ Star the repo: https://github.com/harshitkamboj/Spotify-Cookie-Checker

## 📬 Contact

- GitHub: https://github.com/harshitkamboj
- Website: https://harshitkamboj.in
- Discord: illuminatis69

## 📄 License

MIT License. See `LICENSE`.

## ⚠️ Disclaimer

Educational use only. Use only on accounts/cookies you are authorized to test.


