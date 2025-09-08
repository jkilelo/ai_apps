def calculate_trade_levels_simplified(btc_price, trade_size=1.0):
    """
    Calculate entry cost and exit prices for 1-4% profit targets
    Entry at UTC 00:00:00 market price (no discount)
    
    Args:
        btc_price: BTC price at UTC midnight
        trade_size: USD amount per trade (default $1)
    
    Returns:
        Dict with calculations for each strategy
    """
    from decimal import Decimal, getcontext
    getcontext().prec = 10
    
    # Convert to Decimal
    entry_price = Decimal(str(btc_price))
    size = Decimal(str(trade_size))
    
    # Fees
    MAKER_FEE = Decimal('0.0025')  # 0.25%
    TAKER_FEE = Decimal('0.004')   # 0.40%
    
    # BTC amount purchased
    btc_amount = size / entry_price
    
    # Total cost including maker fee
    total_entry_cost = size * (Decimal('1') + MAKER_FEE)
    
    results = {
        'entry_price': float(entry_price),
        'btc_amount': float(btc_amount),
        'total_entry_cost': float(total_entry_cost),
        'strategies': {}
    }
    
    # Calculate for each profit target
    for target in [0.01, 0.02, 0.03, 0.04, 0.05]:
        target_decimal = Decimal(str(target))
        
        # Required proceeds after fees
        required_net = total_entry_cost + (size * target_decimal)
        
        # Exit price (accounting for taker fee on exit)
        exit_price = required_net / (btc_amount * (Decimal('1') - TAKER_FEE))
        
        # Actual proceeds
        gross_proceeds = exit_price * btc_amount
        taker_fee_amount = gross_proceeds * TAKER_FEE
        net_proceeds = gross_proceeds - taker_fee_amount
        
        # Net profit
        net_profit = net_proceeds - total_entry_cost
        
        # Price movement required
        price_move = ((exit_price - entry_price) / entry_price) * Decimal('100')
        
        results['strategies'][f'{int(target*100)}%'] = {
            'exit_price': float(exit_price),
            'price_move_required': float(price_move),
            'net_profit': float(net_profit)
        }
    
    return results

# Display function
def show_daily_trades(btc_price=100000):
    """Show trade levels for daily entry"""
    
    calc = calculate_trade_levels_simplified(btc_price)
    
    print(f"Entry at UTC 00:00:00")
    print(f"BTC Price: ${calc['entry_price']:,.2f}")
    print(f"Cost with fees: ${calc['total_entry_cost']:.4f}")
    print(f"\n{'Target':<8} {'Exit Price':<12} {'Move Required':<15} {'Net Profit'}")
    print("-" * 55)
    
    for strategy, data in calc['strategies'].items():
        print(f"{strategy:<8} ${data['exit_price']:,.2f}     "
              f"{data['price_move_required']:.2f}%            "
              f"${data['net_profit']:.4f}")

# Example
show_daily_trades(100000)