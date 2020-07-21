# this file provides supporting stuff for the telegram bot

import numpy as np
import pandas as pd
import yfinance as yf
import re
import random

from datetime import datetime, timedelta
from datetime import date as datetype ## clumsy code but works for now

import requests

vocab_dict = {
    'no_change': ['remained flat at {}'],
    'small_up': ['inched up {}', 'edged up {}'],
    'reg_up': ['gained {}', 'climbed {}', 'advanced {}', 'rose {}', 'added {}', 'was {} higher'],
    'big_up': ['jumped {}', 'surged {}', 'rallied {}', 'shot up {}', 'spiked up {}'],
    'small_down': ['inched down {}', 'edged down {}'],
    'reg_down': ['slid {}', 'dropped {}', 'declined {}', 'fell by {}', 'eased {}', 'retreated by {}', 'slipped by {}',  'was {} lower', 'pulled back {}', 'shedded {}'],
    'big_down': ['sunk {}', 'tumbled {}', 'collapsed {}', 'slumped {}']
}

def write_sentence(pct_chg, close_price, vocab_dict=vocab_dict, precision=2):
    '''
    Crafts a descriptive sentence given the parameters passed
    '''
    if pct_chg < -0.025:
        a = 'big_down'
    elif -0.025 <= pct_chg < -0.002:
        a = 'reg_down'
    elif -0.002 <= pct_chg < 0:
        a = 'small_down'
    elif pct_chg == 0:
        a = 'no_change'
    elif 0 < pct_chg < 0.002:
        a = 'small_up'
    elif 0.002 <= pct_chg < 0.025:
        a = 'reg_up'
    elif 0.025 <= pct_chg:
        a = 'big_up'
    else:
        if pd.isnull(pct_chg) and pd.isnull(close_price):
            return 'has not been traded yet'
        else:
            return "was unchanged today" 
            
    if a == 'no_change':
        out_str = 'remained flat at ' + str(round(close_price, 2))
    else:
        out_str = random.choice(vocab_dict[a]).format(str(round(abs(pct_chg) * 100, 2)) + '%')
        if out_str[-1] == '%':
            out_str += ' to '
        else:
            out_str += ' at '
        out_str += str(round(close_price, precision))
    return out_str

def format_content(df):
    '''
    writes sentences for every row in the df, 
    provided that rows are indexed by the tickers
    returns a dictionary of sentences, with tickers as key
    '''
    out = {}
    for i in range(len(df)):
        # check if the series is a currency, if so use 4dp precision
        if len(str(df.iloc[i]['short_name'])) == 7 and str(df.iloc[i]['short_name'][3]) == '/':
            out[df.iloc[i].name] = write_sentence(pct_chg=df.iloc[i][2], close_price=df.iloc[i][1], precision=4)
        else:
            out[df.iloc[i].name] = write_sentence(pct_chg=df.iloc[i][2], close_price=df.iloc[i][1])
    return out

def tellme(a):
    if all(x > 0 for x in a):
        return "up"
    elif all(x < 0 for x in a):
        return "down"
    else:
        return "mixed"

def message_draft_pm(df, author, date=datetime.today(), out_path=None):
    '''
    Drafts a message given a reference df, template, and date
    Saves message as a txt file if provided an out_path
    '''
    weekday = date.strftime(format='%A')
    now = date.strftime(format='%I:%M %p')
    date = date.strftime(format='%d %b %Y')
    if date[0] == '0':
        date = date[1:]
    
    template = './msg_templates/msg_template_pm.txt'
    sentences = format_content(df)

    with open(template, 'r') as f:
        text = f.read()
    
    bank_rets = df.loc[['D05.SI', 'U11.SI', 'O39.SI']].pct_chg.values
    bank_mvmt = tellme(bank_rets)
    
    textformats = {
        'weekday': weekday,
        'now': now,
        'msg_date': date,
        'author_name': author,
        'sti': sentences['^STI'],
        'hsi': sentences['^HSI'],
        'csi': sentences['000300.SS'],
        'sse': sentences['000001.SS'],
        'chnxt': sentences['399006.SZ'],
        'n225': sentences['^N225'],
        'asx': sentences['^AXJO'],
        'aord': sentences['^AORD'],
        'ftse': sentences['^FTSE'],
        'cac': sentences['^FCHI'],
        'dax': sentences['^GDAXI'],
        'sxxp': sentences['^STOXX'],
        'sx5e': sentences['^STOXX50E'],
        'spf': df.loc['ES=F', 'short_name'],
        'spfs': sentences['ES=F'],
        'nqf': df.loc['NQ=F', 'short_name'],
        'nqfs': sentences['NQ=F'],
        'sgdx': sentences['SGD=X'],
        'tnx': sentences['^TNX'],
        'gcf': df.loc['GC=F', 'short_name'],
        'gcfs': sentences['GC=F'],
        'clf': df.loc['CL=F', 'short_name'],
        'clfs': sentences['CL=F'],
        'dbs': sentences['D05.SI'],
        'uob': sentences['U11.SI'],
        'ocbc': sentences['O39.SI'],
        'bank_mvmt': bank_mvmt
    }
    text = text.format(**textformats)
    
    if out_path != None:
        with open(out_path, 'w') as f:
            f.write(text)
    return text

def message_draft_am(df, author, date=datetime.today(), out_path=None):
    '''
    Drafts a message given a reference df, template, and date
    Saves message as a txt file if provided an out_path
    '''
    weekday_today = date.strftime(format='%A')
    weekday = (date.date() - timedelta(1)).strftime(format='%A')
    now = date.strftime(format='%I:%M %p')
    date = date.strftime(format='%d %b %Y')
    
    if date[0] == '0':
        date = date[1:]
    
    template = './msg_templates/msg_template_am.txt'
    sentences = format_content(df)

    with open(template, 'r') as f:
        text = f.read()
    
    textformats = {
        'weekday': weekday,
        'weekday_today': weekday_today,
        'msg_date': date,
        'now': now,
        'author_name': author,
        'spx': sentences['^GSPC'],
        'ndq': sentences['^IXIC'],
        'dji': sentences['^DJI'],
        'fb': sentences['FB'],
        'amzn': sentences['AMZN'],
        'aapl': sentences['AAPL'],
        'goog': sentences['GOOG'],
        'ftse': sentences['^FTSE'],
        'cac': sentences['^FCHI'],
        'dax': sentences['^GDAXI'],
        'sxxp': sentences['^STOXX'],
        'sx5e': sentences['^STOXX50E'],
        'sgdx': sentences['SGD=X'],
        'tnx': sentences['^TNX'],
        'gcf': df.loc['GC=F', 'short_name'],
        'gcfs': sentences['GC=F'],
        'clf': df.loc['CL=F', 'short_name'],
        'clfs': sentences['CL=F']
    }
    text = text.format(**textformats)
    
    if out_path != None:
        with open(out_path, 'w') as f:
            f.write(text)
    
    return text

def get_prev_summary(tick_list, date, series_type=None):
    '''
    Get descriptive statistics of tickers given:
      tick list - list of tickers
      date - reference date
    Returns data in a DataFrame
    '''
    if not isinstance(date, datetype):
        date = datetime.strftime(format='%Y-%m-%d')
    names = []
    close_price = []
    pct_chg = []
    for t in tick_list:
        print('Retrieving data for', str(t))
        # initialise the ticker, get quotes and info
        ticker = yf.Ticker(t)
        quotes = ticker.history(period='5d') #5d quote used as 1d has some issues
        
        # append short name
        try:
            info = ticker.info
            names.append(info['shortName'])
        except:
            names.append(np.nan)
        
        # append close prices
        try:
            close_price.append(quotes.loc[date, 'Close'])
        except:
            close_price.append(np.nan)
        
        # this part handles percent changes
        try:
            a = quotes.pct_change().loc[date, 'Close']
        except:
            a = np.nan
        
        if pd.isnull(a):
            try:
                spare_df = return_csv(series_type)
                mydate = spare_df.iloc[[spare_df.shape[0]-1]].index.values[0]
                print("{} doesn't have historical data. Attempting to retrieve values from local data dated {}.".format(t, str(mydate)[:10]))
                prev_close = spare_df.iloc[[spare_df.shape[0]-1]].loc[:, t][0]
                today_close = quotes.loc[date, 'Close']
                pct_chg.append(today_close/prev_close - 1)
            except:
                print('Data for {} is unavailable, filling with NaN value instead.'.format(t))
                pct_chg.append(np.nan)
        else:
            pct_chg.append(a)
            
    output = pd.DataFrame({
        'short_name': names,
        'close_price': close_price,
        'pct_chg': pct_chg
    }, index=tick_list)
    return output

def create_csv(df, date, path):
    '''
    creates a csv containing closing price timeseries. 
    doesn't really need to be called day-to-day
    '''
    if not isinstance(date, datetype):
        date = datetime.strptime(date, '%Y-%m-%d')
    data_df = pd.DataFrame(data = df['close_price'].values.reshape(df.shape[0], 1).T,
                           columns = df.index, 
                           index = pd.DatetimeIndex([date]))
    data_df.index.name = 'date'
    data_df.to_csv(path, encoding='utf-8-sig')
        
def update_csv(df, date, path):
    '''
    updates the csv file containing the closing price timeseries
    '''
    if not isinstance(date, datetype):
        date = datetime.strptime(date, '%Y-%m-%d')
    data_df = pd.DataFrame(data = df['close_price'].values.reshape(df.shape[0], 1).T,
                           columns = df.index, 
                           index = pd.DatetimeIndex([date]))
    data_df.index.name = 'date'
    source_df = pd.read_csv(path, index_col='date')
    source_df = source_df.append(data_df)
    source_df.to_csv(path, encoding='utf-8-sig')

def undo_csv(path):
    '''
    removes the last row of the csv file
    '''
    df = pd.read_csv(path, index_col='date')
    df.iloc[:len(df)-1].to_csv(path)
    
def retrieve_csv(path):
    df = pd.read_csv(path, parse_dates=True, index_col='date')
    return df

def return_csv(series_type):
    path_dict = {
        'apac': './data_files/apac_timeseries.csv',
        'useu': './data_files/useu_timeseries.csv',
        'othr': './data_files/othr_timeseries.csv'
    }
    if series_type not in path_dict.keys():
        raise ValueError("Bad series_type passed. Series type must be one of the following: 'apac', 'useu', 'othr'.")
    return retrieve_csv(path_dict[series_type])
    
class telegram_bot():
    '''
    contains info on our telegram bot
    '''
    def __init__(self):
        self.token = '<YOUR_BOT_TOKEN_HERE>'
        self.channel_id = '<YOUR_CHANNEL_ID_HERE>'
        self.api_url = 'https://api.telegram.org/bot{}/sendMessage'.format(self.token)
        
    def get_details(self):
        return self.token, self.channel_id, self.api_url
    
    def __msgformat__(self, text):
        replacements = {
            '.': '\\.',
            '>': '\\>',
            '-': '\\-',
            '(': '\\(',
            ')': '\\)',
            '+': '\\+'
        }
        replacements = dict((re.escape(k), v) for k, v in replacements.items())
        pattern = re.compile("|".join(replacements.keys()))
        return pattern.sub(lambda m: replacements[re.escape(m.group(0))], text)
    
    def send_msg_str(self, str_in):
        '''
        Sends a message using the telegram bot, given: 
        str_in: a string to be used as the message content
        '''
        content = self.__msgformat__(str_in)
        
        payload = {
            'chat_id': '-100'+self.channel_id,
            'text': content,
            'parse_mode': 'MarkdownV2'
        }
        
        r = requests.post(self.api_url, data=payload)
        return r.json()
        
    def send_msg_file(self, path):
        '''
        Sends a message using the telegram bot, given: 
        path: a path to a .txt file containing the message content
        '''
        with open(path, 'r') as f:
            content = f.read()
        
        content = self.__msgformat__(content)
        
        payload = {
            'chat_id': '-100'+self.channel_id,
            'text': content,
            'parse_mode': 'MarkdownV2'
        }
        
        r = requests.post(url=self.api_url, data=payload)
        return r.json()