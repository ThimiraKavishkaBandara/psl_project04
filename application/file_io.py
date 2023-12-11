from .__init__ import *

def load_data(path: Path, header: List[str], ignore_index=True) -> pd.DataFrame:
    with open(path, mode='r', encoding='iso8859-1') as f:
        lines = f.readlines()
    df = pd.DataFrame(map(parse_line, lines), columns=header)
    return df

def download_data(url: str, path: Path):
    try:
        print(f"Downloading data from {url} ...")
        r = requests.get(url, allow_redirects=True)
        with open(path, 'wb') as f:
            f.write(r.content)
    except Exception as e:
        print(e)
        return False

def parse_line(line: str, sep="::", ignore_index=True) -> List[str]:
    row = line.split(sep=sep)
    row = [s.strip() for s in row]
    #row = dict(zip(header, row))
    if ignore_index: pass
        #row = row[1:]
    return row

def download_from_s3(bucket_name: str, filename: str, path: Path):
    try:
        s3 = boto3.client('s3')
        s3.download_file(bucket_name, filename, path/filename)
    except Exception as e:
        print(e)
        return False
    