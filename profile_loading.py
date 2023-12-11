from tqdm import tqdm
import pandas as pd
from pathlib import Path
from typing import List

def load_data(path: Path, header: List[str], ignore_index=True) -> pd.DataFrame:
    with open(path, mode='r') as f:
        lines = f.readlines()
    df = pd.DataFrame(map(parse_line, lines), columns=header)
    return df

def parse_line(line: str, sep="::", ignore_index=True) -> List[str]:
    row = line.split(sep=sep)
    row = [s.strip() for s in row]
    #row = dict(zip(header, row))
    if ignore_index: pass
        #row = row[1:]
    return row

if __name__ == "__main__":
    datapath = Path("../data/")
    ratings = load_data(datapath/"ratings.dat", header=['UserID', 'MovieID', 'Rating', 'Timestamp'])
    print(ratings)
    #users = load_data(datapath/"users.dat", header=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code'])
    #print(users)