import json
import numpy as np

def trade_calc(trades):
    # dictionary for trade summaries for json
    trading_summary = {
        "wins": 0,
        "loss": 0,
        "avg_win": 0,
        "avg_loss": 0,
        "win_pnl": 0,
        "loss_pnl": 0,
        "exit_date": [],
        "exit_date_str": [],
        "cumulative_pnl": [],
        "drawdown": [],
        "pnl": []
    }

    # running calculations for trades
    pnl = []
    wins, loss = 0, 0
    gross_wins, gross_loss = [], []
    total_pnl_dashboard = 0
    total_pnl_charts = 0
    peak = float("-inf")
    drawdown = 0
    same_cumulative_pnl = 0
    prev_day = None


    for t in trades:
        curr_date = t.exit_date
        if t.exit_date is not None and t.price_exit is not None:

            if t.status == 'long':
                trade_pnl = float((t.price_exit - t.price_entry) * t.qty)
        
            elif t.status == 'short':
                trade_pnl = float((t.price_entry - t.price_exit) * t.qty)
            else:
                trade_pnl = 0
        
            pnl.append(trade_pnl)
            trading_summary['pnl'].append(trade_pnl)
            total_pnl_charts += trade_pnl 
          
    
            # first iteration
            if prev_day is None:
                trading_summary['cumulative_pnl'].append(total_pnl_charts)
                trading_summary['exit_date'].append(curr_date)
 
                #same_cumulative_pnl = trade_pnl
                
            
            elif curr_date == prev_day:               
                same_cumulative_pnl += trade_pnl
                
            else:
                total_pnl_charts += same_cumulative_pnl
                trading_summary['cumulative_pnl'].append(total_pnl_charts)       

                #trading_summary['cumulative_pnl'].append(total_pnl_charts)       
                trading_summary["exit_date"].append(t.exit_date)
                same_cumulative_pnl = 0
            
            prev_day = curr_date
            
                        
            if trade_pnl > 0:
                wins += 1
                trading_summary["wins"] += 1    
                trading_summary["win_pnl"] += trade_pnl
                gross_wins.append(trade_pnl)

            elif trade_pnl < 0:
                loss += 1
                trading_summary["loss"] += 1
                trading_summary["loss_pnl"] += trade_pnl
                gross_loss.append(abs(trade_pnl))
            else:
                continue

        else:
            continue



    for value in trading_summary['cumulative_pnl']:
        peak = max(peak, value)
        drawdown = value - peak
        trading_summary['drawdown'].append(drawdown)


    trading_summary["avg_win"] = round(trading_summary['win_pnl'] / wins if wins != 0 else 0, 2)
    trading_summary["avg_loss"] = round(trading_summary['loss_pnl'] / loss if loss != 0 else 0, 2)

   
    # data normalization for dates for each trade
    for d in trading_summary["exit_date"]:
        trading_summary["exit_date_str"].append(d.strftime('%Y-%m-%d'))
 
    del trading_summary["exit_date"] 



    total_pnl_dashboard = round(sum(pnl) if pnl else 0,2)
    total_trades = len(pnl)
    win_rate = round(((wins / (wins + loss)) * 100) if (wins+loss) else 0, 2)
    std_dev_win = round(np.std(gross_wins),2) if gross_wins else 0
    std_dev_loss = round(np.std(gross_loss),2) if gross_loss else 0
    largest_loss = max(gross_loss) if len(gross_loss) > 0 else 0
    largest_win = max(gross_wins) if len(gross_wins) > 0 else 0
    profit_factor = round(sum(gross_wins) / sum(gross_loss) if sum(gross_loss) != 0 and pnl else 1000, 2)

          
    trading_summary_json = json.dumps(trading_summary, indent=4)

    return {
        "trading_summary_json":trading_summary_json,
        "trading_summary":trading_summary, 
            "total_pnl_dashboard":total_pnl_dashboard, 
            "total_pnl_charts":total_pnl_charts,
            "wins":wins,
            "loss":loss, 
            "total_trades":total_trades, 
            "win_rate":win_rate, 
            "std_dev_win":std_dev_win, 
            "std_dev_loss":std_dev_loss,
            "largest_loss":largest_loss,
            "largest_win":largest_win,
            "profit_factor":profit_factor}