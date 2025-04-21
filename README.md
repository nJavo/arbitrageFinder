# BetMock - Sports Arbitrage Calculator

A powerful tool for identifying arbitrage betting opportunities across multiple sports and bookmakers worldwide.

## What is Arbitrage Betting?

Arbitrage betting (or "arbing") is a technique where you place bets on all possible outcomes of an event at odds that guarantee a profit regardless of the result. This is possible when bookmakers have different opinions about the odds of an event, creating price discrepancies you can exploit.

## Features

- **Multi-Sport Support**: Automatically fetches odds from all active sports including soccer, basketball, American football, baseball, ice hockey, tennis, and more
- **Global Coverage**: Compares odds from bookmakers across multiple regions (US, Europe, UK, Australia)
- **Real-time Data**: Fetches the latest odds from The Odds API
- **Arbitrage Detection**: Automatically identifies profitable arbitrage opportunities
- **Stake Calculator**: Calculates optimal stake distribution for maximum profit
- **Detailed Analysis**: View detailed odds from all bookmakers for any match
- **Interactive UI**: Easy-to-use interface with sortable tables and filtering

## Setup

1. **Get an API Key**:
   - Sign up for a free API key at [The Odds API](https://the-odds-api.com)
   - Create a `.local.env` file in the project root with: `ODDS_API_KEY=your_api_key_here`

2. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```
   python main.py
   ```

## How It Works

1. The application fetches a list of all active sports from The Odds API
2. It then retrieves upcoming events and odds from various bookmakers
3. For each event, it analyzes the odds to identify arbitrage opportunities
4. Profitable arbitrages are displayed in the UI with calculated profit percentages
5. Users can double-click on any event to see detailed information and analyze all possible bookmaker combinations

## Interface

- **Profitable Arbitrages Tab**: Shows only events with guaranteed profit opportunities
- **All Odds Scanned Tab**: Shows all events that have been analyzed
- **Detail View**: Double-click on any event to see detailed bookmaker odds and combinations

## Regions and Bookmakers

The application fetches odds from bookmakers in multiple regions:
- **US**: DraftKings, FanDuel, BetMGM, PointsBet, etc.
- **Europe**: Pinnacle, 1xBet, Unibet, etc.
- **UK**: William Hill, Betfair, Ladbrokes, etc.
- **Australia**: Sportsbet, TAB, Neds, etc.

## Notes

- The free tier of The Odds API has limited requests, so the application is designed to be efficient with API calls
- The application updates data every 2 minutes to stay within API rate limits
- Currently supports both 2-way (Home/Away) and 3-way (Home/Draw/Away) betting markets

## License

This project is open source and available for personal use.
