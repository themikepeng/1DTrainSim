# 1-Dimensional Train Simulator
## Problem Statement


1.   Given performance specs and dimensions of a train, how much **time** and **distance** will it take to accelerate? To Brake?
2.   Given the distance between two consecutive stops, how much **time** is required between arrivals (factoring in track speed, acceleration, and braking)?
3.   How can the simulation be extended to obtain a **reasonable timetable** for an entire route?

## 1DTrainSim Features
1.   Simulates a **Train**, given performance specs and dimensions of a train consist

        a. The **Train** then provides functions to calculate relations between **time, distance, and speed** during acceleration or braking

       b. Visualization: to show acceleration and braking performance curves, plot **speed** vs **time**

2.   Finds **Train's arrival-to-arrival time** between stops
    
        a. By combining **time** calculations for acceleration, deceleration, (constant) track speed, and stop dwell time

3.   Includes wrapper script to generate a **timetable file**

        a. Wrapper takes in and parses **train file** and **route file**, then performs necessary calculations
    
       b. See respective sections for file definitions

## Prerequisites
*   Python3 environment with standard libraries
*   Import statements

	```
	from CTrain import *
	from timetable import *
	```

## Note about units
Function inputs are in US units, while outputs are in metric units

Helper constants/functions are provided for converting/printing back and forth

## API usage: standalone calculations
Refer to function dosctrings in ***CTrain.py*** for parameters, output, and unit conversions

Refer to ***demo.py*** for a full example flow
1. Calculate combined coefficient of drag (optional; only if enabling drag calculations)
	```
	D = calc_D(h_in, w_in, rho=1.2041, C_d=1)
	```
2. Initialize a **Train**

	Using default braking params:

	```
	train = Train(m_lb, P_hp, F_lbf, D=0)
	```

	Using custom braking params:

	```
	train = Train(m_lb, \
			P_hp, \
			F_lbf, \
			brake_a1_mphps=2.0, \
			brake_a2_mphps=1.35, \
			brake_v1_mph=70, \
			D=D)
	```
	Can also load consist from .json file (see later section for file format)

	```
	train = load_train("sample_train_A.json")
	```

### Train can now perform any of the following

3. Plot acceleration or braking curve
	```
	train.plot_vel_curve(v_max_mph, accel=True)
	train.plot_vel_curve(v_max_mph, accel=False)
	```
	See example plot: ***accel_plot_eg.png***

4. Calculate relations between **time, distance, and speed** during acceleration or braking, using any of the following
	```
	train.calc_accel_time(v_mph)
	train.calc_accel_vel(t)
	train.calc_accel_dist(t)
	train.calc_brake_time(v_mph)
	train.calc_brake_vel(t, v_mph)
	train.calc_brake_dist(v_mph)
	```
5. Calculate arrival-to-arrival travel **time** from one stop to the next
	```
	train.stop_to_stop_time(d_tot_mi, v_max_mph, t_dwell=120)
	```

## CLI usage: create timetable from user-defined train and route files

1.  Define **train** .json file and **route** .csv file (see sections for format)
2.  Pass files into wrapper script: ***timetable.py***
	```
	usage: timetable.py [-h] -t TRAINFILE -r ROUTEFILE [-d DWELLTIME]
	optional arguments:
	  -h, --help            show this help message and exit
	  -t TRAINFILE, --trainfile TRAINFILE
							.json file representing a train consist
	  -r ROUTEFILE, --routefile ROUTEFILE
							.csv file representing a route
	  -d DWELLTIME, --dwelltime DWELLTIME
							(optional) dwell/buffer time at each stop in seconds
	```
	
	eg.

	```
	timetable.py -t sample_train_A.json -r sample_route_A.csv -d 120
	```
3.  Wrapper will create **timetable** .csv file (see sections for format)

### Train .json file format

See sample file: ***sample_train_A.json***

A **train** file defines the train consist to run

A train consists of two types of rolling stock units:
*   "PowerUnits" = locomotives or multiple units, defined by dimensions and performance
*   "TrailerCars" = non-powered cars, defined by dimensions

Params defined at the (entire) train level:

*   "LeadingCoefDrag"
*   "BrakePerfA1" (optional)
*   "BrakePerfA2" (optional)
*   "BrakePerfV1" (optional)

Params defined at the unit level:

*   "Class"
*   "Subclass"
*   "Mass"
*   "TractionPower" ("PowerUnits" only)
*   "TractionForce" ("PowerUnits" only)
*   "Height"
*   "Width"

**Note**: **Train** initialization is done at the train level; params defined at the unit level in .json will be aggregated

### Route .csv file format

See sample file: ***sample_route_A.csv***

A **route** file defines a route stop-by-stop

Each row corresponds to one stop; stops are ordered consecutively, from one terminus to the opposite terminus

Stops are defined by columns:

*   **arrival stop** = stop name
*   **track speed (mph)** = practical top speed of preceeding track section (considering terrain, curvature, speed restrictions etc.) 
*   **dist (mi)** = distance from preceeding stop

Thus, the .csv must have header format: **arrival stop,track speed (mph),dist (mi)**

By definition, with the exception of loop routes, the initial stop's **track speed** and **dist** must be 0

### Timetable .csv file format

A **timetable** file has similar format to a **route** file, but with additional columns:

*   **time (min)** = time between arriving previous stop, and arriving current stop (dwell time at previous stop + time to traverse preceeding track section)
*   **avg spd (mph)** = average speed over **time (min)**

## References
*   Constants, variables, equations, and algorithms are defined and derived in ***derivations.pdf***

*   Performance specs and dimensions for specific rolling stock can be found by searching: technical documents, manufacturer sites, rail enthusiast sites and forums
    *   **Note:** traction power (hp), to be used for calculations, is typically about 10% lower than official rated horsepower

*   Coefficient of drag can be estimated from train's frontal shape-- typically ranging from conventional (approx 1.0) to high-speed streamlined (approx 0.25)