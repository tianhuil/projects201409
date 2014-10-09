# utils.py

# Place for functions I use in presenting my taxi data that otherwise don't have a home.

def quantiles_in_url(quantiles_list):
    return ','.join([str(num) for quantiles in quantiles_list for num in quantiles])