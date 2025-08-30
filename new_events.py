import pandas as pd

events_sheet = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRPT5wfb1Eh7r7RqGXJNtXeUhbAlokMvIiZdB6PdAQZoRb4JkwCy5Lw4XylvAwnsr7lmVbqPdPrVsMO/pub?gid=1446227550&single=true&output=tsv'

def load_sheet():
    df = pd.read_csv(events_sheet, sep='\t')

    # print(df.head())

    current_dates = set()
    for row in df.values:
        if not pd.isna(row[0]):
            current_dates.add(int(row[0]))

    return current_dates

def get_new_dates(path):
    out = set()
    mapping = dict()
    with open(path, 'r', encoding='utf-8') as f:
        for l in f.read().splitlines():
            if 'fromis_9' not in l:
                continue

            if len(l) >= 6:
                split = l[0:6]
                if split.isdigit():
                    date = int(split)
                    out.add(date)
                    mapping[date] = l[7:].replace(',', '')

    return out, mapping



if __name__ == '__main__':
    new_dates, mapping = get_new_dates('channels/syeonnysideup1442.txt')
    dates = load_sheet()
    print(new_dates)
    print(dates)
    new = new_dates - dates
    for d in new:
        print(f'{d},,{mapping[d]}')
