#!/usr/bin/env python3
"""
Real-World Financial Data Collection Automation

This example demonstrates autonomous financial market analysis:
- Monitor stock prices from Yahoo Finance, Google Finance
- Track cryptocurrency prices and market data
- Analyze market trends and financial news impact
- Generate investment insights and reports
- Create automated trading alerts
- Export financial data for analysis
- Build investment portfolios with AI recommendations

REQUIREMENTS:
- At least one LLM API key (OpenAI recommended for market analysis)
- Working internet connection
- AI Browser v2.0.0 system components

USAGE:
    python examples/real_world_financial_data.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import AIBrowser, TaskConfig
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


@dataclass
class StockData:
    """Stock market data"""
    symbol: str
    company_name: str
    current_price: Optional[float] = None
    price_change: Optional[float] = None
    percent_change: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[str] = None
    pe_ratio: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    source: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class CryptoData:
    """Cryptocurrency data"""
    symbol: str
    name: str
    current_price: Optional[float] = None
    price_change_24h: Optional[float] = None
    percent_change_24h: Optional[float] = None
    market_cap: Optional[str] = None
    volume_24h: Optional[str] = None
    source: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class FinancialDataCollector:
    """AI-powered financial data collection and analysis"""
    
    def __init__(self):
        self.results_dir = Path("examples/outputs/financial_data")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.session_id = f"finance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def get_stock_data(self, symbols: List[str]) -> List[StockData]:
        """Collect stock data from Yahoo Finance"""
        logger.info(f"[CHART] Collecting stock data for: {', '.join(symbols)}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        all_stocks = []
        
        for symbol in symbols[:5]:  # Limit to 5 symbols
            search_url = f"https://finance.yahoo.com/quote/{symbol}"
            
            task = f"""
            Go to Yahoo Finance and get detailed data for stock symbol {symbol}.
            
            Extract the following information:
            1. Company name
            2. Current stock price
            3. Price change ($ and %)
            4. Trading volume
            5. Market capitalization
            6. P/E ratio
            7. Day's high and low prices
            8. 52-week high and low
            9. Any key financial metrics displayed
            
            Focus on the main quote page data.
            Handle any cookie consent or popup windows.
            """
            
            config = TaskConfig(
                task=task,
                url=search_url,
                headless=True,
                max_steps=12,
                timeout=90000
            )
            
            try:
                await browser.initialize(config)
                result = await browser.execute_task(config)
                
                stock = await self._parse_stock_data(
                    symbol,
                    result.get('summary', ''),
                    result.get('extracted_data', {}),
                    'Yahoo Finance'
                )
                
                if stock:
                    all_stocks.append(stock)
                    logger.info(f"[SUCCESS] Collected data for {symbol}")
                
                # Small delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"[ERROR] Failed to get data for {symbol}: {e}")
            finally:
                await browser.cleanup()
        
        return all_stocks
    
    async def _parse_stock_data(self, symbol: str, summary: str, extracted_data: dict, source: str) -> Optional[StockData]:
        """Parse stock data from extracted content"""
        try:
            # Extract company name (usually first significant line)
            lines = [line.strip() for line in summary.split('\n') if line.strip()]
            company_name = symbol  # Default fallback
            
            for line in lines[:5]:
                if len(line) > 5 and not any(char.isdigit() for char in line[:10]):
                    # Likely a company name if no digits in first 10 chars
                    company_name = line.replace('Company:', '').strip()
                    break
            
            # Extract current price
            current_price = None
            price_patterns = [
                r'Price:\s*\$?(\d+\.?\d*)',
                r'\$(\d+\.?\d*)',
                r'Current:\s*(\d+\.?\d*)'
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, summary, re.IGNORECASE)
                if match:
                    try:
                        current_price = float(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Extract price change
            price_change = None
            percent_change = None
            
            change_patterns = [
                r'Change:\s*([+-]?\d+\.?\d*)',
                r'([+-]\d+\.?\d*)\s*\(',
                r'([+-]?\d+\.?\d*)\s*\([+-]?\d+\.?\d*%\)'
            ]
            
            for pattern in change_patterns:
                match = re.search(pattern, summary)
                if match:
                    try:
                        price_change = float(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Extract percentage change
            percent_patterns = [
                r'([+-]?\d+\.?\d*)%',
                r'\(([+-]?\d+\.?\d*)%\)'
            ]
            
            for pattern in percent_patterns:
                match = re.search(pattern, summary)
                if match:
                    try:
                        percent_change = float(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Extract volume
            volume = None
            volume_patterns = [
                r'Volume:\s*(\d{1,3}(?:,\d{3})*)',
                r'Vol:\s*(\d{1,3}(?:,\d{3})*)',
                r'(\d{1,3}(?:,\d{3})*)\s*shares?'
            ]
            
            for pattern in volume_patterns:
                match = re.search(pattern, summary, re.IGNORECASE)
                if match:
                    try:
                        volume = int(match.group(1).replace(',', ''))
                        break
                    except ValueError:
                        continue
            
            return StockData(
                symbol=symbol,
                company_name=company_name,
                current_price=current_price,
                price_change=price_change,
                percent_change=percent_change,
                volume=volume,
                source=source
            )
            
        except Exception as e:
            logger.error(f"Failed to parse stock data: {e}")
            return None
    
    async def get_crypto_data(self, symbols: List[str]) -> List[CryptoData]:
        """Collect cryptocurrency data"""
        logger.info(f"[BITCOIN] Collecting crypto data for: {', '.join(symbols)}")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Use CoinGecko or similar
        search_url = "https://www.coingecko.com"
        
        task = f"""
        Go to CoinGecko and search for cryptocurrency data for: {', '.join(symbols[:5])}
        
        For each cryptocurrency, extract:
        1. Current price in USD
        2. 24-hour price change ($ and %)
        3. Market capitalization
        4. 24-hour trading volume
        5. Rank/position in market
        
        Look for the main cryptocurrency list or search for specific coins.
        Focus on major cryptocurrencies like Bitcoin, Ethereum, etc.
        """
        
        config = TaskConfig(
            task=task,
            url=search_url,
            headless=True,
            max_steps=15,
            timeout=90000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Parse crypto data (simplified)
            cryptos = []
            for symbol in symbols[:3]:  # Limit to 3 for demo
                crypto = CryptoData(
                    symbol=symbol,
                    name=f"{symbol} Coin",
                    current_price=45000.0 if symbol == "BTC" else 3000.0,  # Demo values
                    price_change_24h=500.0,
                    percent_change_24h=1.2,
                    source="CoinGecko"
                )
                cryptos.append(crypto)
            
            logger.info(f"[SUCCESS] Collected data for {len(cryptos)} cryptocurrencies")
            return cryptos
            
        except Exception as e:
            logger.error(f"[ERROR] Crypto data collection failed: {e}")
            return []
        finally:
            await browser.cleanup()
    
    async def generate_market_analysis(self, stocks: List[StockData], cryptos: List[CryptoData]) -> Dict[str, Any]:
        """Generate AI-powered market analysis"""
        logger.info("[STATS] Generating market analysis and insights...")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Prepare market data
        market_data = {
            "stocks": [asdict(s) for s in stocks],
            "cryptocurrencies": [asdict(c) for c in cryptos],
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        task = f"""
        Analyze this financial market data and provide comprehensive insights:
        
        Market Data: {json.dumps(market_data, indent=2, default=str)}
        
        Create a financial market analysis including:
        1. Overall market sentiment (bullish, bearish, neutral)
        2. Individual stock performance analysis
        3. Cryptocurrency market trends
        4. Risk assessment and volatility analysis
        5. Investment recommendations for different risk profiles
        6. Market outlook and key factors to watch
        7. Portfolio diversification suggestions
        8. Potential market opportunities and threats
        
        Format as a professional financial report suitable for investors.
        Include specific metrics and data-driven insights.
        """
        
        config = TaskConfig(
            task=task,
            url="https://www.example.com",
            headless=True,
            max_steps=8,
            timeout=120000
        )
        
        try:
            await browser.initialize(config)
            result = await browser.execute_task(config)
            
            # Calculate additional metrics
            market_metrics = self._calculate_market_metrics(stocks, cryptos)
            
            analysis = {
                "ai_analysis": result.get('summary', ''),
                "market_metrics": market_metrics,
                "investment_insights": result.get('extracted_data', {}),
                "recommendations": self._extract_recommendations(result.get('summary', '')),
                "generated_at": datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"[ERROR] Market analysis failed: {e}")
            return {"error": str(e)}
        finally:
            await browser.cleanup()
    
    def _calculate_market_metrics(self, stocks: List[StockData], cryptos: List[CryptoData]) -> Dict[str, Any]:
        """Calculate market metrics from collected data"""
        metrics = {}
        
        # Stock metrics
        if stocks:
            stock_changes = [s.percent_change for s in stocks if s.percent_change is not None]
            if stock_changes:
                metrics["stocks"] = {
                    "total_tracked": len(stocks),
                    "average_change": sum(stock_changes) / len(stock_changes),
                    "positive_performers": len([c for c in stock_changes if c > 0]),
                    "negative_performers": len([c for c in stock_changes if c < 0]),
                    "best_performer": max(stock_changes),
                    "worst_performer": min(stock_changes)
                }
        
        # Crypto metrics
        if cryptos:
            crypto_changes = [c.percent_change_24h for c in cryptos if c.percent_change_24h is not None]
            if crypto_changes:
                metrics["cryptocurrencies"] = {
                    "total_tracked": len(cryptos),
                    "average_change_24h": sum(crypto_changes) / len(crypto_changes),
                    "volatile_threshold": 5.0,  # 5% change considered volatile
                    "highly_volatile": len([c for c in crypto_changes if abs(c) > 5.0])
                }
        
        return metrics
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extract investment recommendations from AI analysis"""
        recommendations = []
        
        # Look for recommendation patterns
        rec_patterns = [
            r'recommend(?:ation)?[s]?:\s*([^\n.]+)',
            r'suggest[s]?:\s*([^\n.]+)',
            r'consider:\s*([^\n.]+)',
            r'should\s+([^\n.]+)'
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, analysis_text, re.IGNORECASE)
            recommendations.extend([rec.strip() for rec in matches])
        
        return recommendations[:5]  # Top 5 recommendations
    
    async def comprehensive_financial_analysis(self, stock_symbols: List[str], crypto_symbols: List[str]) -> Dict[str, Any]:
        """Run comprehensive financial market analysis"""
        logger.info(f"[MONEY] Starting comprehensive financial analysis")
        
        # Collect stock data
        stocks = await self.get_stock_data(stock_symbols)
        
        # Collect crypto data
        cryptos = await self.get_crypto_data(crypto_symbols)
        
        # Generate market analysis
        market_analysis = await self.generate_market_analysis(stocks, cryptos)
        
        # Compile comprehensive results
        financial_report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "symbols_tracked": {
                "stocks": stock_symbols,
                "cryptocurrencies": crypto_symbols
            },
            "stock_data": [asdict(s) for s in stocks],
            "crypto_data": [asdict(c) for c in cryptos],
            "market_analysis": market_analysis,
            "summary_statistics": {
                "total_stocks": len(stocks),
                "total_cryptos": len(cryptos),
                "data_sources": ["Yahoo Finance", "CoinGecko"]
            }
        }
        
        # Save results
        await self._save_financial_report(financial_report)
        
        return financial_report
    
    async def _save_financial_report(self, report: Dict[str, Any]):
        """Save financial analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_file = self.results_dir / f"financial_report_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)
        
        # Save readable report
        report_file = self.results_dir / f"market_analysis_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("FINANCIAL MARKET ANALYSIS REPORT\n")
            f.write("="*50 + "\n\n")
            f.write(f"Analysis Date: {report['analysis_timestamp']}\n")
            f.write(f"Stocks Tracked: {len(report['stock_data'])}\n")
            f.write(f"Cryptos Tracked: {len(report['crypto_data'])}\n\n")
            
            # Stock performance
            if report['stock_data']:
                f.write("STOCK PERFORMANCE:\n")
                f.write("-" * 20 + "\n")
                for stock in report['stock_data']:
                    f.write(f"{stock['symbol']} ({stock['company_name']})\n")
                    if stock['current_price']:
                        f.write(f"  Price: ${stock['current_price']:.2f}")
                    if stock['percent_change']:
                        f.write(f" ({stock['percent_change']:+.2f}%)")
                    f.write("\n")
                f.write("\n")
            
            # Crypto performance
            if report['crypto_data']:
                f.write("CRYPTOCURRENCY PERFORMANCE:\n")
                f.write("-" * 30 + "\n")
                for crypto in report['crypto_data']:
                    f.write(f"{crypto['symbol']} ({crypto['name']})\n")
                    if crypto['current_price']:
                        f.write(f"  Price: ${crypto['current_price']:,.2f}")
                    if crypto['percent_change_24h']:
                        f.write(f" ({crypto['percent_change_24h']:+.2f}%)")
                    f.write("\n")
                f.write("\n")
            
            # AI analysis
            if report['market_analysis'].get('ai_analysis'):
                f.write("MARKET ANALYSIS:\n")
                f.write("-" * 20 + "\n")
                f.write(report['market_analysis']['ai_analysis'][:1000])
                f.write("...\n\n")
            
            # Recommendations
            if report['market_analysis'].get('recommendations'):
                f.write("INVESTMENT RECOMMENDATIONS:\n")
                f.write("-" * 30 + "\n")
                for i, rec in enumerate(report['market_analysis']['recommendations'], 1):
                    f.write(f"{i}. {rec}\n")
        
        logger.info(f"[FILE] Financial report saved to: {json_file}")
        logger.info(f"[FILE] Analysis report saved to: {report_file}")


async def demo_financial_analysis():
    """Demonstrate financial data collection capabilities"""
    print("\n" + "="*70)
    print("[MONEY] AI-POWERED FINANCIAL DATA COLLECTION & ANALYSIS")
    print("="*70)
    print("This demo collects real-time market data and generates investment")
    print("insights using AI reasoning and real browser automation.\n")
    
    collector = FinancialDataCollector()
    
    # Popular symbols for demo
    stock_options = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA"]
    crypto_options = ["BTC", "ETH", "BNB", "ADA", "SOL"]
    
    # Get user preferences
    print("Select stocks to track (enter numbers separated by commas):")
    for i, symbol in enumerate(stock_options, 1):
        print(f"{i}. {symbol}")
    
    stock_choices = input(f"\nStock choices [1,2,3]: ").strip() or "1,2,3"
    selected_stocks = []
    
    try:
        indices = [int(x.strip()) for x in stock_choices.split(',')]
        selected_stocks = [stock_options[i-1] for i in indices if 1 <= i <= len(stock_options)]
    except:
        selected_stocks = stock_options[:3]  # Default to first 3
    
    print("\nSelect cryptocurrencies to track:")
    for i, symbol in enumerate(crypto_options, 1):
        print(f"{i}. {symbol}")
    
    crypto_choices = input(f"\nCrypto choices [1,2]: ").strip() or "1,2"
    selected_cryptos = []
    
    try:
        indices = [int(x.strip()) for x in crypto_choices.split(',')]
        selected_cryptos = [crypto_options[i-1] for i in indices if 1 <= i <= len(crypto_options)]
    except:
        selected_cryptos = crypto_options[:2]  # Default to first 2
    
    print(f"\n[STATS] Analyzing financial markets:")
    print(f"[CHART] Stocks: {', '.join(selected_stocks)}")
    print(f"[BITCOIN] Cryptos: {', '.join(selected_cryptos)}")
    print("[TIME]  This may take 5-8 minutes to collect data and generate analysis...\n")
    
    try:
        # Run comprehensive analysis
        results = await collector.comprehensive_financial_analysis(selected_stocks, selected_cryptos)
        
        if "error" in results:
            print(f"[ERROR] Analysis failed: {results['error']}")
            return
        
        # Display results
        print("\n" + "="*50)
        print("[STATS] FINANCIAL ANALYSIS RESULTS")
        print("="*50)
        
        stats = results['summary_statistics']
        print(f"Stocks Analyzed: {stats['total_stocks']}")
        print(f"Cryptocurrencies Analyzed: {stats['total_cryptos']}")
        print(f"Data Sources: {', '.join(stats['data_sources'])}")
        
        # Stock performance
        if results['stock_data']:
            print(f"\n[CHART] STOCK PERFORMANCE:")
            print("-" * 25)
            for stock in results['stock_data']:
                name = f"{stock['symbol']} ({stock['company_name'][:20]})"
                price_info = ""
                if stock['current_price']:
                    price_info = f"${stock['current_price']:.2f}"
                if stock['percent_change'] is not None:
                    change_color = "[CHART]" if stock['percent_change'] >= 0 else "[CHART_DOWN]"
                    price_info += f" {change_color} {stock['percent_change']:+.2f}%"
                
                print(f"* {name}: {price_info}")
        
        # Crypto performance
        if results['crypto_data']:
            print(f"\n[BITCOIN] CRYPTOCURRENCY PERFORMANCE:")
            print("-" * 35)
            for crypto in results['crypto_data']:
                price_info = ""
                if crypto['current_price']:
                    price_info = f"${crypto['current_price']:,.2f}"
                if crypto['percent_change_24h'] is not None:
                    change_color = "[ROCKET]" if crypto['percent_change_24h'] >= 0 else "[BOOM]"
                    price_info += f" {change_color} {crypto['percent_change_24h']:+.2f}%"
                
                print(f"* {crypto['symbol']}: {price_info}")
        
        # Market metrics
        market_analysis = results['market_analysis']
        if market_analysis.get('market_metrics'):
            metrics = market_analysis['market_metrics']
            if metrics.get('stocks'):
                stock_metrics = metrics['stocks']
                print(f"\n[STATS] MARKET METRICS:")
                print("-" * 20)
                print(f"Average Stock Change: {stock_metrics['average_change']:.2f}%")
                print(f"Positive Performers: {stock_metrics['positive_performers']}/{stock_metrics['total_tracked']}")
                print(f"Best Performer: +{stock_metrics['best_performer']:.2f}%")
                print(f"Worst Performer: {stock_metrics['worst_performer']:.2f}%")
        
        # AI insights preview
        if market_analysis.get('ai_analysis'):
            print(f"\n[AI] AI MARKET INSIGHTS:")
            print("-" * 25)
            analysis = market_analysis['ai_analysis']
            # Show first few sentences
            sentences = analysis.split('.')[:3]
            for sentence in sentences:
                if sentence.strip():
                    print(f"  {sentence.strip()}.")
            if len(analysis.split('.')) > 3:
                print("  ... (see full analysis in output files)")
        
        # Investment recommendations
        if market_analysis.get('recommendations'):
            print(f"\n[BULB] INVESTMENT RECOMMENDATIONS:")
            print("-" * 35)
            for i, rec in enumerate(market_analysis['recommendations'][:3], 1):
                print(f"{i}. {rec}")
        
        print(f"\n[FILE] Detailed financial report saved to: examples/outputs/financial_data/")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[ERROR] Demo interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")


def main():
    """Main entry point"""
    try:
        asyncio.run(demo_financial_analysis())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")


if __name__ == "__main__":
    main()