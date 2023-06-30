from CTrain import *
import json
import pandas as pd
import argparse
import time

def load_train(train_json):
    '''
    Wrapper:
    loads a .json file representing a train consist
    See sample .json for format
    Extracts, aggregates necessary performance parameters, dimensions
    Initializes a Train to be used for performance calculations
    '''
    # load json from path
    j_file = open(train_json)
    train_data = json.load(j_file)
    
    ### Extract params at train level ###
    # extract the coefficient of drag
    C_d = train_data["LeadingCoefDrag"]
    # extract braking performance params (optional)
    brake_params_defined = False
    try:
        brake_a1_mphps = train_data["BrakePerfA1"]
        brake_a2_mphps = train_data["BrakePerfA2"]
        brake_v1_mph = train_data["BrakePerfV1"]
        brake_params_defined = True
    except KeyError:
        # case: braking performance params not defined
        pass
    
    ### Extract params at unit level, aggregate across train level (all units) ###
    # (max) height and width
    h_in_max = max([power_unit["Height"] for power_unit in train_data["PowerUnits"]] + \
        [trailer_car["Height"] for trailer_car in train_data["TrailerCars"]])
    w_in_max = max([power_unit["Width"] for power_unit in train_data["PowerUnits"]] + \
        [trailer_car["Width"] for trailer_car in train_data["TrailerCars"]])
    # (sum, power units) traction power and force
    P_hp_tot = sum([power_unit["TractionPower"] for power_unit in train_data["PowerUnits"]])
    F_lbf_tot = sum([power_unit["TractionForce"] for power_unit in train_data["PowerUnits"]])
    # (sum, all units) mass
    m_lb_total = sum([power_unit["Mass"] for power_unit in train_data["PowerUnits"]] + \
        [trailer_car["Mass"] for trailer_car in train_data["TrailerCars"]])
        
    # calculate combined coefficient of drag (D)
    D = calc_D(h_in_max, w_in_max, C_d = C_d)
        
    # put it all together to initialize a Train
    if brake_params_defined:
        train = Train(m_lb_total, \
            P_hp_tot, \
            F_lbf_tot, \
            brake_a1_mphps=brake_a1_mphps, \
            brake_a2_mphps=brake_a2_mphps, \
            brake_v1_mph=brake_v1_mph, \
            D=D)
    else:
        train = Train(m_lb_total, \
            P_hp_tot, \
            F_lbf_tot, \
            D=D)
    return train
    
def gen_timetable(train_json, route_csv, t_dwell=120):
    '''
    Wrapper: 
    Initializes a Train to be used for performance calculations (load_train)
    Loads a .csv file representing a route
    See sample .csv for format
    Calculates time required to arrive at each stop from previous stop
    Calculates avg speed of each segment
    Generates .csv with two new columns
    '''
    
    # initialize Train
    train = load_train(train_json)
    
    # load csv into dataframe
    route_df = pd.read_csv(route_csv)
    
    # sanity check: necessary columns present, no missing values
    assert all(['track speed (mph)' in route_df, 'dist (mi)' in route_df]), \
        "Route .csv must contain columns: 'track speed (mph)' and 'dist (mi)'!"
    assert not (route_df['track speed (mph)'].isnull().values.any()), \
        "Column 'track speed (mph)' cannot be missing values!"
    assert not (route_df['dist (mi)'].isnull().values.any()), \
        "Column 'dist (mi)' cannot be missing values!"
    
    # sanity check: cannot have 0 values, except in the first row
    if 0 in route_df.iloc[1:].values:
        raise ValueError("Route .csv cannot contain zeroes except in the first row!")
        
    # sanity check: first row must have zeroes, in both dist and track speed columns, or neither
    first_row_zero = False
    if 0 in route_df.iloc[0].values:
        assert all([route_df['track speed (mph)'].iloc[0] == 0, route_df['dist (mi)'].iloc[0] == 0]), \
            "First row 'track speed (mph)' and 'dist (mi)' must both be 0, or neither be 0!"
        first_row_zero = True
    
    # cannot apply stop_to_stop_time or calc_avg_vel, with any 'dist (mi)' or 'track speed (mph)' equal to 0
    # if first row contains zeroes: save, remove, add back after applying
    if first_row_zero:
        first_row = route_df.head(1)
        route_df.drop(0, inplace=True)
    
    # apply train stop_to_stop_time on 'dist (mi)', 'track speed (mph)', to get 'time (min)'
    # / 60 to get 'time (min)' from secs
    # apply calc_avg_vel to get 'avg spd (mph)'
    # / 60 again to use 'time (min)' in hours
    s2s_lambda = lambda x: train.stop_to_stop_time(x['dist (mi)'], x['track speed (mph)'], t_dwell) / 60
    route_df['time (min)'] = route_df.apply(s2s_lambda, axis=1)
    avg_lambda = lambda x: calc_avg_vel(x['dist (mi)'], x['time (min)'] / 60)
    route_df['avg spd (mph)'] = route_df.apply(avg_lambda, axis=1)
    
    # fill zeroes in first row's new columns; add back first row
    if first_row_zero:
        first_row.insert(len(first_row.columns), 'time (min)', [0])
        first_row.insert(len(first_row.columns), 'avg spd (mph)', [0])
        route_df = first_row.append(route_df, ignore_index=True)

    # generate new timetable csv
    out_name = route_csv[0:-4] + '_timetable.csv'
    route_df.to_csv(out_name, index=False)
    
if __name__ == "__main__":
    '''
    Command line interface
    Calculates timetable from train consist .json file, and route .csv file
    Sample usage: timetable.py -t sample_train_A.json -r sample_route_A.csv -d 120
    '''
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--trainfile", required=True, help=".json file representing a train consist")
    parser.add_argument("-r", "--routefile", required=True, help=".csv file representing a route")
    parser.add_argument("-d", "--dwelltime", required=False, default=120, type=float, help="(optional) dwell/buffer time at each stop in seconds")
    args = parser.parse_args()
    
    assert all([isinstance(args.trainfile, str), ".json" in args.trainfile]), \
        "--trainfile must be a path to file in .json format!"
    assert all([isinstance(args.routefile, str), ".csv" in args.routefile]), \
        "--routefile must be a path to file in .csv format!"
    assert all([args.dwelltime >= 0]), \
        "--dwelltime must be a nonnegative number!"
        
    print(f"Generating timetable .csv from {args.trainfile} and {args.routefile}...")
    print("-"*75)
    gen_timetable(args.trainfile, args.routefile, args.dwelltime)
    print("Done")
    time.sleep(5)