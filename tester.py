from CTrain import *

if __name__ == "__main__":
    D = calc_D(h_in=15*12+7.5, w_in=10*12+3, C_d=0.8)
    print(f"combined coefficient of drag: {D}")
    
    train = Train(m_lb=1172000.0, P_hp=3900, F_lbf=65000.0, D=D)
    
    # edge test cases
    # expect no errors
    weak_train = Train(m_lb=0.1, P_hp=0.1, F_lbf=0.1, D=0)
    print(train.calc_accel_time(0))
    print(train.calc_accel_vel(0))
    print(train.calc_accel_dist(0.1))
    print(train.calc_brake_time(0))
    print(train.calc_brake_vel(0, 0))
    print(train.calc_brake_dist(0))
    print(train.stop_to_stop_time(d_tot_mi=0.1, v_max_mph=0.1, t_dwell=0))
    train.plot_vel_curve(0.1)
    
    # bad test cases (1)
    # expect assertion error if any line(s) activated
    #bad_train = Train(m_lb=0, P_hp=0.1, F_lbf=0.1, D=0)
    #bad_train2 = Train(m_lb=0.1, P_hp=0, F_lbf=0.1, D=0)
    #bad_train3 = Train(m_lb=0.1, P_hp=0.1, F_lbf=0, D=0)
    #bad_train4 = Train(m_lb=0.1, P_hp=0.1, F_lbf=0.1, D=-0.1)
    #train.calc_accel_time(-0.1)
    #train.calc_accel_vel(-0.1)
    #train.calc_accel_dist(0)
    #train.calc_brake_time(-0.1)
    #train.calc_brake_vel(-0.1, -0.1)
    #train.calc_brake_dist(-0.1)
    #train.stop_to_stop_time(d_tot_mi=0, v_max_mph=0.1, t_dwell=0)
    #train.stop_to_stop_time(d_tot_mi=0.1, v_max_mph=0, t_dwell=0)
    #train.stop_to_stop_time(d_tot_mi=0.1, v_max_mph=0.1, t_dwell=-0.1)
    #train.plot_vel_curve(0)
    
    # bad test cases (2)
    # calculating stop_to_stop_time with unrealistic params
    # expect -1 Error: v_max_mph is unrealistic; v_max_mph is not reachable
    unrealistic_test_vel = 99999999
    print(f"Expect error -1, got: {train.stop_to_stop_time(d_tot_mi=15, v_max_mph=unrealistic_test_vel)}")

    # expect -1 Error: d_tot_mi is unrealistic; distance is much too short vs. acceleration/deceleration time needed
    unrealistic_test_dist = 0.01
    print(f"Expect error -1, got: {train.stop_to_stop_time(d_tot_mi=unrealistic_test_dist, v_max_mph=125)}")