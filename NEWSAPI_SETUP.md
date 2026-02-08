# Real News API Setup Guide

## Quick Start: Enable Live Trending News

### 1. Get a Free NewsAPI Key

1. Visit **https://newsapi.org/register**
2. Sign up with your email (free tier available)
3. Copy your **API Key** from the dashboard

### 2. Add to `.env` File

Edit your `.env` file in the project root and add:

```env
NEWSAPI_KEY=your-api-key-here
NEWS_COUNTRY=us
NEWS_CATEGORY=general
```

**Available Options:**

Countries: `us`, `gb`, `de`, `fr`, `it`, `es`, `in`, `ru`, `cn`, `br`, `pt`, `nl`, `be`, `ua`, `se`, `ch`

Categories: `general`, `business`, `entertainment`, `health`, `science`, `sports`, `technology`

### 3. Restart the App

```bash
python run.py
```

### 4. Verify Live News

- Navigate to **http://localhost:5000/**
- You should see **real trending news** from NewsAPI
- Click on article titles to open the **actual source links**

---

## Features

✅ **Real-time headlines** - Updated from NewsAPI.org  
✅ **Actual source links** - Click titles to read full articles  
✅ **Live categorization** - Filter by country and category  
✅ **Fallback support** - Mocked data if API fails  
✅ **Free tier** - 100 requests/day on NewsAPI free plan  

---

## Troubleshooting

### No trending news appearing?

1. Check `.env` has `NEWSAPI_KEY` set correctly
2. Verify API key is valid at https://newsapi.org/account
3. Check logs for API errors: `python run.py` output
4. Ensure requests library is installed: `pip install requests`

### API rate limit exceeded?

NewsAPI free tier: **100 requests/day**

- Trending news refreshes on each dashboard visit
- Consider caching results or upgrading API plan

### Wrong country/category?

Update `.env`:
```env
NEWS_COUNTRY=gb
NEWS_CATEGORY=technology
```

Then restart: `python run.py`

---

## Alternative APIs

If you prefer a different news source:

### Guardian API
- URL: `https://open-platform.theguardian.com/documentation/`
- Free tier: 5,000 requests/day
- Good for UK/international news

### NewsData.io
- URL: `https://newsdata.io/`
- Free tier: 200 requests/day
- Covers 150+ countries

### Bing News Search
- Using Azure Cognitive Services
- Requires Azure subscription

---

## Production Deployment

For production, consider:

1. **API Key Security**: Store in secure environment variable manager (not in code)
2. **Caching**: Cache trending news for 1 hour to reduce API calls
3. **Fallback**: Always have mocked data as backup
4. **Monitoring**: Log API failures and alert if service is down

---

## Support

For issues with NewsAPI, visit: https://newsapi.org/support
