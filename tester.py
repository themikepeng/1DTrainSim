from CTrain import *

if __name__ == "__main__":
    # demonstration pt. 1
    # instantiation, acceleration, deceleration, stop-to-stop calculations
    # expect no errors
    D = calc_D(h_in=15*12+7.5, w_in=10*12+3, C_d=0.77)
    print(f"combined coefficient of drag: {D}")
    train = Train(m_lb=1030000, P_hp=3900, F_lbf=50000, D=D)

    print()
    test_vel = 125
    print(f"time to reach {test_vel} mph: ")
    test_time = train.calc_accel_time(test_vel)
    print(f"{test_time} s")

    print(f"speed at time {test_time} s: ")
    print(vel_units_str(train.calc_accel_vel(test_time)))

    print(f"distance traveled accelerating for {test_time} s: ")
    print(dist_units_str(train.calc_accel_dist(test_time)))

    print()
    print(f"time to brake from {test_vel} mph: ")
    print(f"{train.calc_brake_time(test_vel)} s")

    print(f"distance traveled while braking from {test_vel} mph: ")
    print(dist_units_str(train.calc_brake_dist(test_vel)))

    print()
    test_total_dist = 15
    test_total_dist_m = test_total_dist * MI_TO_M
    test_total_time = train.stop_to_stop_time(d_tot_mi=test_total_dist, v_max_mph=test_vel)
    print(f"{test_total_time} s")
    print(f"average speed: {vel_units_str(calc_avg_vel(test_total_dist_m, test_total_time))} mph")
    
    
    # demonstration pt. 2
    # special case: distance-constrained stop-to-stop calculation
    # expect no errors
    test_total_dist = 5
    test_total_dist_m = test_total_dist * MI_TO_M
    test_total_time = train.stop_to_stop_time(d_tot_mi=test_total_dist, v_max_mph=test_vel)
    print(f"{test_total_time} s")
    print(f"average speed: {vel_units_str(calc_avg_vel(test_total_dist_m, test_total_time))} mph")
    
    # edge test cases
    # expect no errors
    weak_train = Train(m_lb=0.1, P_hp=0.1, F_lbf=0.1, D=0)
    train.calc_accel_time(0)
    train.calc_accel_vel(0)
    train.calc_accel_dist(0.1)
    train.calc_brake_time(0)
    train.calc_brake_dist(0)
    train.stop_to_stop_time(d_tot_mi=0.1, v_max_mph=0.1, t_dwell=0)
    
    # bad test cases
    # expect error if any line(s) activated
    #bad_train = Train(m_lb=0, P_hp=0.1, F_lbf=0.1, D=0)
    #bad_train2 = Train(m_lb=0.1, P_hp=0, F_lbf=0.1, D=0)
    #bad_train3 = Train(m_lb=0.1, P_hp=0.1, F_lbf=0, D=0)
    #bad_train4 = Train(m_lb=0.1, P_hp=0.1, F_lbf=0.1, D=-0.1)
    #train.calc_accel_time(-0.1)
    #train.calc_accel_vel(-0.1)
    #train.calc_accel_dist(0)
    #train.calc_brake_time(-0.1)
    #train.calc_brake_dist(-0.1)
    #train.stop_to_stop_time(d_tot_mi=0, v_max_mph=0.1, t_dwell=0)
    #train.stop_to_stop_time(d_tot_mi=0.1, v_max_mph=0, t_dwell=0)
    #train.stop_to_stop_time(d_tot_mi=0.1, v_max_mph=0.1, t_dwell=-0.1)