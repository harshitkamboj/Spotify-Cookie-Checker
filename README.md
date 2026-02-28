# Spotify Cookie Checker V2

Multi-threaded Spotify cookie checker with account data extraction, proxy rotation, configurable retries, and organized output.

## Features

- Fast multi-threaded cookie checking
- Supports both Netscape `.txt` and JSON cookie formats
- Extracts plan, email, and country
- Extracts owner/member status for family/duo
- Detects child-account status when true
- Extracts family free slots, invite link, and address when available
- Detects next payment date when available
- Broad proxy format support (`http`, `https`, `socks4/5`, auth variants)
- Smart retry system with proxy rotation on retryable errors
- Built-in email dedupe (duplicates are skipped and counted)
- `log` mode for detailed per-cookie output
- `simple` mode for clean live dashboard counters
- Telegram + Discord notifications
- `full` and `invite_address_only` notification modes
- Plan-based output organization by run folder and account type

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional (for SOCKS proxies):

```bash
pip install requests[socks]
```

## Quick Start

1. Clone:
```bash
git clone https://github.com/harshitkamboj/Spotify-Cookie-Checker.git
cd Spotify-Cookie-Checker
```
2. Install requirements:
```bash
pip install -r requirements.txt
```
3. Put cookie files in `cookies/`
4. Add proxies in `proxy.txt` (optional)
5. Configure `config.yml` if needed
6. Run:
```bash
python main.py
```

## Folder Layout

```text
cookies/         # input cookies
failed/          # invalid/expired
broken/          # malformed/error cases
hits/
  run_YYYY-MM-DD_HH-MM-SS/
    Premium/
    Free/
    Duo Premium/
      owner_account/
      non_owner_account/
      unknown/
    Family Premium/
      owner_account/
      non_owner_account/
      unknown/
    Family Basic/
      owner_account/
      non_owner_account/
      unknown/
proxy.txt
config.yml
main.py
```

## Cookie Formats

Netscape example:

```text
.spotify.com	TRUE	/	FALSE	1234567890	sp_dc	xxx
```

JSON array example:

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

## Proxy Formats

One proxy per line in `proxy.txt`.

Supported examples:

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

## Config (`config.yml`)

The checker reads settings from `config.yml`.

### Sections

- `txt_fields`: controls which fields are written in output txt files
- `notifications`: Discord/Telegram delivery settings and mode
- `display`: console UI mode
- `retries`: retry count for retryable request/proxy errors

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
    mode: "full"
  telegram:
    enabled: false
    bot_token: ""
    chat_id: ""
    mode: "full"

display:
  mode: "log"

retries:
  error_proxy_attempts: 3
```

### Key options

- `notifications.webhook.mode`
- `full`: sends full account details + file
- `invite_address_only`: sends only family invite/address style message for eligible family owners

- `notifications.telegram.mode`
- `full`: sends full account details + file
- `invite_address_only`: sends only family invite/address style message for eligible family owners

- `display.mode`
- `log`: per-cookie status logs
- `simple`: dashboard-style counters

- `retries.error_proxy_attempts`
- Number of total attempts per cookie (example: `3` = first try + 2 retries)

## Retry Behavior

For each cookie, checker retries up to `retries.error_proxy_attempts` when request/proxy errors happen.

- Each retry uses a different proxy when available
- Retry-trigger status codes: `403`, `429`, `500`, `502`, `503`, `504`
- If all retries fail on error conditions, file moves to `broken/`
- Normal invalid cookie flow moves file to `failed/`

## Email Dedupe

Built-in behavior (always enabled):

- First valid account for an email is kept
- Next valid cookies with same email are treated as duplicates
- Duplicate cookies are skipped (counted in console stats only; no output file)

## Output Notes

- File name format: `<COUNTRY>_github-harshitkamboj_<PLAN>_<RANDOM>.txt`
- Output includes: `Checker By: github.com/harshitkamboj | Website: harshitkamboj.in`

## Account Plan Mapping

Detected and mapped plans include:

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

## Contact

- GitHub: https://github.com/harshitkamboj
- Website: https://harshitkamboj.in
- Discord: illuminatis69

## Support

- Star the repo: https://github.com/harshitkamboj/Spotify-Cookie-Checker

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Disclaimer

Educational use only. Use only on accounts/cookies you are authorized to test.
