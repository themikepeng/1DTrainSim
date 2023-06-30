from CTrain import *

if __name__ == "__main__":  
    # 1. combined coefficient of drag
    print("\nDEMO 1. combined coefficient of drag")
    D = calc_D(h_in=15*12+7.5, w_in=10*12+3, C_d=0.8)
    print(f"combined coefficient of drag: {D}")
    
    # 2. initialize a Train
    print("\nDEMO 2. initialize a Train")
    train = Train(m_lb=1172000.0, P_hp=3900, F_lbf=65000.0, D=D)
    
    # 3. plot acceleration, braking curves (speed vs time)
    # sanity check: should not see any jagged lines
    print("\nDEMO 3. plot acceleration, braking curves (speed vs time)")
    test_vel = 125
    print("displaying accleration and braking curves...")
    train.plot_vel_curve(test_vel)
    train.plot_vel_curve(test_vel, accel=False)

    # 4. time, distance, speed relations for acceleration, deceleration 
    print("\nDEMO 4. time, distance, speed relations for acceleration, deceleration")
    print(f"time to reach {test_vel} mph: ")
    test_time = train.calc_accel_time(test_vel)
    print(f"{test_time} s")

    print(f"speed at time {test_time} s: ")
    print(vel_units_str(train.calc_accel_vel(test_time)))

    print(f"distance traveled accelerating for {test_time} s: ")
    print(dist_units_str(train.calc_accel_dist(test_time)))

    print()
    brake_time = train.calc_brake_time(test_vel)
    print(f"time to brake from {test_vel} mph: ")
    print(f"{brake_time} s")

    print(f"speed after {brake_time} s of braking from {test_vel} mph: ")
    print(vel_units_str(train.calc_brake_vel(brake_time, test_vel)))

    print(f"distance traveled while braking from {test_vel} mph: ")
    print(dist_units_str(train.calc_brake_dist(test_vel)))

    # 5. arrival-to-arrival travel time (stop-to-stop)
    print("\nDEMO 5. arrival-to-arrival travel time (stop-to-stop)")
    test_total_dist = 15
    test_total_dist_m = test_total_dist * MI_TO_M
    test_total_time = train.stop_to_stop_time(d_tot_mi=test_total_dist, v_max_mph=test_vel)
    print(f"{test_total_time} s")
    print(f"average speed: {vel_units_str(calc_avg_vel(test_total_dist_m, test_total_time))} mph")
    
    # 5. special case: distance-constrained stop-to-stop calculation
    print("\nDEMO 5. special case: distance-constrained stop-to-stop calculation")
    test_total_dist = 5
    test_total_dist_m = test_total_dist * MI_TO_M
    test_total_time = train.stop_to_stop_time(d_tot_mi=test_total_dist, v_max_mph=test_vel)
    print(f"{test_total_time} s")
    print(f"average speed: {vel_units_str(calc_avg_vel(test_total_dist_m, test_total_time))} mph")