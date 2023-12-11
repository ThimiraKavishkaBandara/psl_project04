from .__init__ import *

# Read config file
with open('application/config.json') as f:
    cfg = json.load(f)
    
datapath = Path(cfg['datapath'])
similarity_matrix_path = Path(datapath/cfg['similarity_matrix_name'])
rating_matrix_path = Path(datapath/cfg['rating_matrix_name'])
data_url = cfg['data_url']
s3_bucket_name = cfg['s3_bucket_name']