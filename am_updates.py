from datetime import datetime, timedelta
import jx_telebot2 as jx

# set the reference date - default by referencing today()
date_t = datetime.today()
date = date_t.date()
date

# Gather necessary financial data
## list of US/EU indices we're interested in
useu_indices = [
    '^GSPC',
    '^DJI',
    '^IXIC',
    '^RUT',
    '^STOXX',
    '^FTSE',
    '^STOXX50E',
    '^GDAXI',
    '^FCHI',
]

## list of other indicators we're interested in
othr_list = [
    '^VIX',
    'ES=F',
    'YM=F',
    'NQ=F',
    'GC=F',
    'CL=F',
    'SGD=X',
    '^IRX',
    '^FVX',
    '^TNX',
    '^TYX',
]

## list of equities we want data for
stocks_list_us = ['AMZN', 'FB', 'AAPL', 'GOOG']
stocks_list_sg = ['D05.SI', 'U11.SI', 'O39.SI']

# Capture data in our dataframes
useu_df = jx.get_prev_summary(useu_indices, date - timedelta(1), series_type='useu')
othr_df = jx.get_prev_summary(othr_list, date - timedelta(1), series_type='othr')
stocks_df_us = jx.get_prev_summary(stocks_list_us, date - timedelta(1))
print('Markets data retrieved')

# Create the working dataframe for the draft message
working_df_am = useu_df.append([othr_df, stocks_df_us])

# Save data to csv file -- contingency
print('updating csv files')
jx.update_csv(useu_df, date - timedelta(1), path='useu_timeseries.csv')
jx.update_csv(othr_df, date - timedelta(1), path='othr_timeseries.csv')
print('csv files updated')

# Prepare the output text 
## recall: date_t = datetime.today() - timedelta(whatever)
out_path = './sent/am_msg {}.txt'.format(date.strftime(format='%Y%m%d'))
author = 'JX'
text = jx.message_draft_am(df=working_df_am, out_path=out_path, author=author, date=date_t)
print('output text generated')

#preview message
if input('Preview message? [Y/N]: ').upper() == 'Y':
    print('Message preview below:', '\n') 
    print(text)

# Use the telegram api to send message
msg = input('Send message? [Y/N]: ')
if msg.upper() == 'Y':
    bot = jx.telegram_bot()
    bot.send_msg_file(out_path)

# all done! 
msg_status = 'sent' if msg.upper() == 'Y' else 'not sent'
print('All done, message {}!'.format(msg_status))