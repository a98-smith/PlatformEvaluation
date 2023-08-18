import os, pandas as pd

data_dir = os.path.join( os.getcwd(), 'Output logs')
filename = 'combined_df.csv'

if __name__ == '__main__':
    
    filepath = os.path.join(data_dir, filename)
    data = pd.read_csv(filepath, delimiter=',', index_col=0)
    print(data.iloc[90])
    data.fillna(value=0.1, inplace=True)
    print(data.iloc[90])
    data.to_csv(filepath)

    
    nl_data = data[data.Loading == 'NL']
    cl_data = data[data.Loading == 'CL']
    
    nl_data.reset_index(inplace=True, drop=True)
    cl_data.reset_index(inplace=True, drop=True)
    
    nl_data.to_csv(os.path.join(data_dir, 'nl_df.csv'))
    cl_data.to_csv(os.path.join(data_dir, 'cl_df.csv'))