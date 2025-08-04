import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def get_indonesia_stocks():
    """
    Get most active Indonesian stocks from Yahoo Finance
    Note: Yahoo Finance doesn't have a direct API for most active stocks by region
    We'll use a curated list of major Indonesian stocks
    """
    
    # Major Indonesian stocks (IDX - Indonesia Stock Exchange)
    indonesia_stocks = {
        'BBCA.JK': 'Bank Central Asia Tbk',
        'BBRI.JK': 'Bank Rakyat Indonesia Tbk',
        'BMRI.JK': 'Bank Mandiri Tbk',
        'ASII.JK': 'Astra International Tbk',
        'TLKM.JK': 'Telkom Indonesia Tbk',
        'ICBP.JK': 'Indofood CBP Sukses Makmur Tbk',
        'UNVR.JK': 'Unilever Indonesia Tbk',
        'PGAS.JK': 'Perusahaan Gas Negara Tbk',
        'KLBF.JK': 'Kalbe Farma Tbk',
        'INDF.JK': 'Indofood Sukses Makmur Tbk',
        'SMGR.JK': 'Semen Indonesia Tbk',
        'ANTM.JK': 'Aneka Tambang Tbk',
        'PTBA.JK': 'Bukit Asam Tbk',
        'INTP.JK': 'Indocement Tunggal Prakarsa Tbk',
        'JSMR.JK': 'Jasa Marga Tbk',
        'WIKA.JK': 'Wijaya Karya Tbk',
        'ADRO.JK': 'Adaro Energy Tbk',
        'BBNI.JK': 'Bank Negara Indonesia Tbk',
        'BRIS.JK': 'Bank Syariah Indonesia Tbk',
        'GOTO.JK': 'GoTo Gojek Tokopedia Tbk'
    }
    
    return indonesia_stocks

def fetch_stock_data(symbols, period='1mo'):
    """
    Fetch stock data for given symbols
    """
    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if not hist.empty:
                data[symbol] = hist
                print(f"✓ Fetched data for {symbol}")
            else:
                print(f"✗ No data for {symbol}")
        except Exception as e:
            print(f"✗ Error fetching {symbol}: {e}")
    
    return data

def calculate_metrics(stock_data):
    """
    Calculate key metrics for each stock
    """
    metrics = {}
    
    for symbol, data in stock_data.items():
        if len(data) < 5:  # Need at least 5 days of data
            continue
            
        # Calculate daily returns
        data['Returns'] = data['Close'].pct_change()
        
        # Calculate change percentage (from 30 days ago to today)
        if len(data) >= 30:
            change_pct = ((data['Close'].iloc[-1] - data['Close'].iloc[-30]) / data['Close'].iloc[-30]) * 100
        else:
            change_pct = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
        
        # Volume metrics
        avg_volume = data['Volume'].mean()
        recent_volume = data['Volume'].tail(5).mean()
        volume_trend = (recent_volume - avg_volume) / avg_volume * 100
        
        # Price metrics
        current_price = data['Close'].iloc[-1]
        price_volatility = data['Returns'].std() * np.sqrt(252) * 100  # Annualized volatility
        
        # Technical indicators
        sma_20 = data['Close'].rolling(window=20).mean().iloc[-1] if len(data) >= 20 else current_price
        sma_50 = data['Close'].rolling(window=50).mean().iloc[-1] if len(data) >= 50 else current_price
        
        # RSI calculation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
        
        metrics[symbol] = {
            'Current_Price': current_price,
            'Change_Pct': change_pct,
            'Avg_Volume': avg_volume,
            'Recent_Volume': recent_volume,
            'Volume_Trend': volume_trend,
            'Volatility': price_volatility,
            'SMA_20': sma_20,
            'SMA_50': sma_50,
            'RSI': current_rsi,
            'Price_vs_SMA20': ((current_price - sma_20) / sma_20) * 100,
            'Price_vs_SMA50': ((current_price - sma_50) / sma_50) * 100
        }
    
    return metrics

def predict_stocks(metrics, top_n=5):
    """
    Predict best stocks for next 14 days based on multiple factors
    """
    if not metrics:
        return []
    
    df = pd.DataFrame(metrics).T
    
    # Scoring system (higher score = better prediction)
    scores = {}
    
    for symbol in df.index:
        score = 0
        
        # Volume factor (30% weight)
        volume_score = min(df.loc[symbol, 'Volume_Trend'] / 10, 10)  # Cap at 10
        score += volume_score * 0.3
        
        # Price momentum (25% weight)
        change_score = min(df.loc[symbol, 'Change_Pct'] / 5, 10)  # Cap at 10
        score += change_score * 0.25
        
        # Technical indicators (25% weight)
        # RSI between 30-70 is good
        rsi_score = 10 - abs(df.loc[symbol, 'RSI'] - 50) / 5
        rsi_score = max(0, min(rsi_score, 10))
        score += rsi_score * 0.25
        
        # Price vs moving averages (20% weight)
        sma_score = (df.loc[symbol, 'Price_vs_SMA20'] + df.loc[symbol, 'Price_vs_SMA50']) / 2
        sma_score = min(sma_score / 2, 10)  # Cap at 10
        score += sma_score * 0.2
        
        scores[symbol] = score
    
    # Sort by score and return top N
    sorted_stocks = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_stocks[:top_n]

def create_analysis_plots(stock_data, metrics, predictions):
    """
    Create comprehensive analysis plots
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Indonesia Stock Market Analysis - Most Active Stocks', fontsize=16, fontweight='bold')
    
    # Plot 1: Change Percentage
    symbols = list(metrics.keys())
    changes = [metrics[s]['Change_Pct'] for s in symbols]
    
    colors = ['green' if x > 0 else 'red' for x in changes]
    bars1 = axes[0, 0].bar(range(len(symbols)), changes, color=colors, alpha=0.7)
    axes[0, 0].set_title('Change Percentage (Last 30 Days)', fontweight='bold')
    axes[0, 0].set_ylabel('Change (%)')
    axes[0, 0].set_xticks(range(len(symbols)))
    axes[0, 0].set_xticklabels([s.replace('.JK', '') for s in symbols], rotation=45)
    axes[0, 0].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Add value labels on bars
    for bar, change in zip(bars1, changes):
        height = bar.get_height()
        axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + (0.1 if height > 0 else -0.5),
                        f'{change:.1f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=8)
    
    # Plot 2: Volume Trend
    volume_trends = [metrics[s]['Volume_Trend'] for s in symbols]
    colors = ['blue' if x > 0 else 'orange' for x in volume_trends]
    bars2 = axes[0, 1].bar(range(len(symbols)), volume_trends, color=colors, alpha=0.7)
    axes[0, 1].set_title('Volume Trend (Recent vs Average)', fontweight='bold')
    axes[0, 1].set_ylabel('Volume Change (%)')
    axes[0, 1].set_xticks(range(len(symbols)))
    axes[0, 1].set_xticklabels([s.replace('.JK', '') for s in symbols], rotation=45)
    axes[0, 1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Plot 3: RSI Analysis
    rsi_values = [metrics[s]['RSI'] for s in symbols]
    colors = ['red' if x > 70 else 'green' if x < 30 else 'blue' for x in rsi_values]
    bars3 = axes[1, 0].bar(range(len(symbols)), rsi_values, color=colors, alpha=0.7)
    axes[1, 0].set_title('RSI (Relative Strength Index)', fontweight='bold')
    axes[1, 0].set_ylabel('RSI Value')
    axes[1, 0].set_xticks(range(len(symbols)))
    axes[1, 0].set_xticklabels([s.replace('.JK', '') for s in symbols], rotation=45)
    axes[1, 0].axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought')
    axes[1, 0].axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold')
    axes[1, 0].legend()
    
    # Plot 4: Prediction Scores
    if predictions:
        pred_symbols = [p[0].replace('.JK', '') for p in predictions]
        pred_scores = [p[1] for p in predictions]
        colors = plt.cm.viridis(np.linspace(0, 1, len(pred_scores)))
        bars4 = axes[1, 1].bar(range(len(pred_symbols)), pred_scores, color=colors, alpha=0.8)
        axes[1, 1].set_title('Top 5 Predicted Stocks (14-Day Outlook)', fontweight='bold')
        axes[1, 1].set_ylabel('Prediction Score')
        axes[1, 1].set_xticks(range(len(pred_symbols)))
        axes[1, 1].set_xticklabels(pred_symbols, rotation=45)
        
        # Add score labels
        for bar, score in zip(bars4, pred_scores):
            height = bar.get_height()
            axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('indonesia_stock_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """
    Main analysis function
    """
    print("🚀 Indonesia Stock Market Analysis")
    print("=" * 50)
    
    # Get Indonesian stocks
    indonesia_stocks = get_indonesia_stocks()
    print(f"📊 Analyzing {len(indonesia_stocks)} major Indonesian stocks...")
    
    # Fetch stock data
    stock_data = fetch_stock_data(indonesia_stocks.keys(), period='2mo')
    
    if not stock_data:
        print("❌ No stock data available. Please check your internet connection.")
        return
    
    print(f"\n📈 Successfully fetched data for {len(stock_data)} stocks")
    
    # Calculate metrics
    metrics = calculate_metrics(stock_data)
    
    if not metrics:
        print("❌ No metrics calculated. Insufficient data.")
        return
    
    # Sort by change percentage
    sorted_by_change = sorted(metrics.items(), key=lambda x: x[1]['Change_Pct'], reverse=True)
    
    print("\n📋 Most Active Indonesian Stocks (Sorted by Change %):")
    print("-" * 80)
    print(f"{'Symbol':<10} {'Name':<30} {'Change%':<10} {'Price':<10} {'Volume Trend%':<15}")
    print("-" * 80)
    
    for symbol, metric in sorted_by_change:
        name = indonesia_stocks.get(symbol, 'Unknown')
        print(f"{symbol.replace('.JK', ''):<10} {name[:28]:<30} {metric['Change_Pct']:>8.1f}% {metric['Current_Price']:>8.0f} {metric['Volume_Trend']:>12.1f}%")
    
    # Predict top 5 stocks
    predictions = predict_stocks(metrics, top_n=5)
    
    print("\n🎯 Top 5 Predicted Stocks for Next 14 Days:")
    print("-" * 80)
    print(f"{'Rank':<5} {'Symbol':<10} {'Name':<30} {'Score':<8} {'Current Price':<15} {'Change%':<10}")
    print("-" * 80)
    
    for i, (symbol, score) in enumerate(predictions, 1):
        name = indonesia_stocks.get(symbol, 'Unknown')
        metric = metrics[symbol]
        print(f"{i:<5} {symbol.replace('.JK', ''):<10} {name[:28]:<30} {score:>6.1f} {metric['Current_Price']:>12.0f} {metric['Change_Pct']:>8.1f}%")
    
    # Create detailed analysis for top predictions
    print("\n📊 Detailed Analysis of Top Predictions:")
    print("=" * 80)
    
    for i, (symbol, score) in enumerate(predictions, 1):
        metric = metrics[symbol]
        name = indonesia_stocks.get(symbol, 'Unknown')
        
        print(f"\n{i}. {symbol} - {name}")
        print(f"   Prediction Score: {score:.1f}/10")
        print(f"   Current Price: IDR {metric['Current_Price']:,.0f}")
        print(f"   Change (30d): {metric['Change_Pct']:.1f}%")
        print(f"   Volume Trend: {metric['Volume_Trend']:.1f}%")
        print(f"   RSI: {metric['RSI']:.1f}")
        print(f"   Volatility: {metric['Volatility']:.1f}%")
        
        # Prediction reasoning
        print("   📈 Prediction Factors:")
        if metric['Volume_Trend'] > 0:
            print(f"      ✅ High volume activity (+{metric['Volume_Trend']:.1f}%)")
        if metric['Change_Pct'] > 0:
            print(f"      ✅ Positive price momentum (+{metric['Change_Pct']:.1f}%)")
        if 30 <= metric['RSI'] <= 70:
            print(f"      ✅ Healthy RSI ({metric['RSI']:.1f})")
        if metric['Price_vs_SMA20'] > 0:
            print(f"      ✅ Above 20-day moving average")
    
    # Create visualization
    print("\n📊 Generating analysis plots...")
    create_analysis_plots(stock_data, metrics, predictions)
    
    print("\n✅ Analysis complete! Check 'indonesia_stock_analysis.png' for visualizations.")
    print("\n⚠️  Disclaimer: This analysis is for educational purposes only.")
    print("   Always do your own research before making investment decisions.")

if __name__ == "__main__":
    main() 