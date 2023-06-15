from CTrain import *

if __name__ == "__main__":
    D = calc_D(h_in=15*12+7.5, w_in=10*12+3, C_d=0.77)
    print(D)
    train = Train(m_lb=1030000, P_hp=3900, F_lbf=50000, D=D)
    test_vel = 125
    print(f"time (s) to reach {test_vel} mph: ")
    test_time = train.calc_time_vel(test_vel)
    print(test_time)
    print(f"speed at time {test_time}: ")
    print(vel_units_str(train.calc_vel_time(test_time)))
    print(f"distance traveled at time {test_time}: ")
    print(dist_units_str(train.calc_dist_time(test_time)))
