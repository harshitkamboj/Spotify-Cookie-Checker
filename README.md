# ⚠️ STATUS: NOT-WORKING | FIXING RELEASING SOON
### UPDATED 24-02-2026
## Donate cookies on discord for fast fixing 
👉Discord: [harshitkamboj.in](https://harshitkamboj.in/) Or see details here: [click here](https://harshitkamboj.in/)


# 🎵 Spotify Cookie Checker V2

A powerful, multi-threaded Spotify cookie validator that checks cookie validity, extracts account information, and organizes results efficiently.

## ✨ Features

- 🚀 **Multi-threaded Processing** - Fast concurrent cookie validation
- 🌐 **Proxy Support** - Rotate through proxies to avoid rate limiting
- 📊 **Detailed Account Info** - Extract plan, country, recurring status, trial, owner, and more
- 🔄 **Auto Format Conversion** - Convert JSON cookies to Netscape format automatically
- 📁 **Smart Organization** - Automatically sorts results into structured folders
- 📈 **Real-time Statistics** - Live progress tracking in the console and window title
- 🎨 **Colorful Interface** - Console output with status indicators

## 📋 Requirements
```
pip install requests
```

## 🚀 Quick Start

1. **Clone the repository**
    ```
    git clone https://github.com/harshitkamboj/Spotify-Cookie-Checker.git
    cd Spotify-Cookie-Checker
    ```

2. **Install dependencies**
    ```
    pip install -r requirements.txt
    ```

3. **Setup your files**
    - Add your Spotify cookies (`.txt` or `.json` format) to the `cookies/` folder
    - Add proxies to `proxy.txt` (optional but recommended)

4. **Run the checker**
    ```
    python main.py
    ```

## 📁 Folder Structure
```
├── cookies/ # Input folder for your cookies
├── hits/ # Working subscribed accounts
├── failed/ # Invalid/expired cookies
├── broken/ # Malformed cookie files
├── proxy.txt # Your proxy list (optional)
└── main.py # Main script
```

## 🍪 Cookie Formats Supported

### Netscape Format (.txt)
```
.spotify.com TRUE / FALSE 1234567890 cookie_name cookie_value
```

### JSON Format (.json)
```
[
{
"domain": ".spotify.com",
"flag": "TRUE",
"path": "/",
"secure": false,
"expirationDate": 1234567890,
"name": "cookie_name",
"value": "cookie_value"
}
]
```

## 🌐 Proxy Setup

Create a `proxy.txt` file with your proxies (one per line):
```
ip:port
user:pass@ip:port
http://ip:port
http://user:pass@ip:port
```

## 📊 Output Examples

### Working Subscribed Account (hits/)
```
Filename: US_github-harshitkamboj_Premium_12345678.txt

Plan: Premium
Country: US
Autopay: True
Trial: False
Owner: True
Checker By: github.com/harshitkamboj
Spotify COOKIE :👇

[original cookie content]
```

## ⚙️ Configuration

You can modify these settings in the script:

- **Thread Count**: Change `num_threads` parameter (default: 10)
- **Timeout**: Modify request timeout (default: 15 seconds)

## 📈 Statistics

The checker provides detailed statistics:
- 📈 Total cookies checked
- ✅ Working subscribed accounts
- ❌ Working but unsubscribed accounts
- 💀 Dead/expired cookies

## 🔧 Advanced Features

### Smart Error Handling
- Handles malformed cookies gracefully
- Proxy fallback mechanism
- Automatic retry on network errors

### Account Information Extraction
- Plan type and pricing tier
- Country of registration
- Owner status
- Recurring/Trial status

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This tool is for educational purposes only. Please ensure you have permission to test the cookies you're using. Respect Spotify's terms of service and rate limits.

## 🌟 Support

If you found this tool helpful, please:
- ⭐ Star this repository
- 🍴 Fork and share with others
- 🐛 Report any issues you find
- 💡 Suggest new features

## 📞 Contact

- **GitHub**: [@harshitkamboj](https://github.com/harshitkamboj)
- **Discord**: illuminatis69

---

<div align="center">
  <b>Made with ❤️</b>
  <br>
  <i>Star ⭐ this repo if you found it useful!</i>
</div>





