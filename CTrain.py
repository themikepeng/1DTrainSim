import numpy as np
from scipy.integrate import quad

import matplotlib.pyplot as plt
import numpy as np

### metric conversion constants ###
LB_TO_KG = 0.45359237
HP_TO_W = 745.699872
LBF_TO_N = 4.4482216
MPH_TO_M_S = 0.44704
MI_TO_M = 1609.344
IN_TO_M = 0.0254

### braking performance params ###
### use default constants for now ###
### using constants 2.1.5 ###
'''
BRAKE_A1 = deceleration rate (m/s^2) from BRAKE_V1 (m/s) down to 0
BRAKE_A2 = deceleration rate for v above BRAKE_V1
'''
BRAKE_A1 = 2 * MPH_TO_M_S
BRAKE_A2 = 1.35 * MPH_TO_M_S
BRAKE_V1 = 70 * MPH_TO_M_S

### helpers to print dual units, given metric ###
def mass_units_str(m):
  return str(round(m, 2)) + " kg (" + str(round(m/LB_TO_KG, 2)) + " lb)"

def power_units_str(P):
  return str(round(P, 2)) + " W (" + str(round(P/HP_TO_W, 2)) + " hp)"

def force_units_str(F):
  return str(round(F, 2)) + " N (" + str(round(F/LBF_TO_N, 2)) + " lbf)"

def vel_units_str(v):
  return str(round(v, 2)) + " m/s (" + str(round(v/MPH_TO_M_S, 2)) + " mph)"

def dist_units_str(d):
  return str(round(d/1000, 2)) + " km (" + str(round(d/MI_TO_M, 2)) + " mi)"

def t_round_str(t):
  return str(round(t, 2)) + " s"

### helpers ###
def calc_D(h_in, w_in, rho = 1.2041, C_d = 1):
  '''
  args:
  h = max cross-section height (in)
  w = max cross-section width (in)
  C_d = coefficient of drag

  returns:
  D = combined coefficient of drag
  '''
  assert all([h_in > 0, w_in > 0, rho > 0, C_d > 0]), \
    "The following args must be positive: all"
  h = h_in * IN_TO_M
  w = w_in * IN_TO_M

  # implements equation 1.3.1
  D_final = 0.5 * h * w * rho * C_d
  return D_final

def calc_avg_vel(d, t):
  '''Returns v_avg given any distance and time'''
  assert all([d > 0, t > 0]), \
    "The following args must be positive: all"
  
  # implements equation 3.2.2
  return d / t


class Train():
  def __init__(self, m_lb, P_hp, F_lbf, D=0.77):
    '''
    Initialize a Train from args:
    m_lb = mass of train (lb)
    P = traction power (hp)
    F_lbf = max tractive effort (lbf)
    D = combined coefficient of drag (optional)
    '''
    assert all([m_lb > 0, P_hp > 0, F_lbf > 0]), \
      "The following args must be positive: m_lb, P_hp, F_lbf"
    assert D >= 0, \
      "The following args must be nonnegative: D"
    
    self.m = m_lb * LB_TO_KG
    self.P = P_hp * HP_TO_W
    self.F = F_lbf * LBF_TO_N
    self.D = D
    print(f"Initializing train with weight {mass_units_str(self.m)}, power {power_units_str(self.P)}, tractive force {force_units_str(self.F)}")
    self.calc_power_limit()

  def calc_power_limit(self):
    '''
    Calculate v_1, the highest v where full F can be applied
    and t_1, the time to accelerate to v_1
    '''
    # implements equation 1.1.1
    self.v_1 = self.P/self.F
    # implements equation 1.1.2
    self.t_1 = self.m * self.P / (self.F**2)
    print(f"Traction limited by power above {vel_units_str(self.v_1)}, after {t_round_str(self.t_1)}")

  def calc_accel_time(self, v_mph):
    '''Returns the time required to reach v_mph, -1 if unable'''
    assert v_mph >= 0, \
      "The following args must be nonnegative: v_mph"
    v = v_mph * MPH_TO_M_S

    if v <= self.v_1:
      # implements equation 1.2.2
      t_final = self.m * v / self.F
    else:
      # implements equation 1.3.2
      numer = self.m * (v**2 - (self.v_1 ** 2))
      denom = 2 * (self.P - (self.D * v**3))
      if denom < 0:
        return -1
      t_final = (numer / denom) + self.t_1
    return t_final

  def calc_accel_vel(self, t):
    '''
    Returns the velocity after t s of acceleration
    by solving for v in equation of form av^3 + bv^2 + c = 0
    '''
    assert t >= 0, \
      "The following args must be nonnegative: t"

    if t < self.t_1:
      # implements equation 1.2.1
      vel_final = self.F * t / self.m
    else:
      # implements equation 1.3.3
      a = 2 * self.D * (t - self.t_1)
      b = self.m
      c = (2 * self.P * (self.t_1 - t)) - (self.m * (self.v_1 ** 2))
      p = [a, b, 0, c]
      roots = np.roots(p)
      # required to extract real solution
      vel_final = abs(roots[-1])
    return vel_final

  def calc_accel_dist(self, t):
    '''
    Returns the dist traveled after t s of acceleration
    by integrating v(t)dt over [0, t]
    '''
    assert t > 0, \
      "The following args must be positive: t"

    # implements equation 1.3.4
    res, err = quad(self.calc_accel_vel, 0, t)
    # ensure integral calculation is accurate
    assert err < res * 0.01, f"Distance calculated with high error +-{err}%"
    return res

  def calc_brake_time(self, v_mph):
    '''Returns the time required to brake to a stop from v_mph'''
    assert v_mph >= 0, \
      "The following args must be nonnegative: v_mph"
    
    # implements equation 2.1.1
    v = v_mph * MPH_TO_M_S
    if v < BRAKE_V1:
      t_final = v * (1 / BRAKE_A1)
    else:
      t_final = (v - BRAKE_V1) * (1 / BRAKE_A2) + BRAKE_V1 * (1 / BRAKE_A1)
    return t_final

  def calc_brake_vel(self, t, v_mph):
    '''
    Returns the velocity after t s of braking from v_mph
    '''
    assert all([t >= 0, v_mph >= 0]), \
      "The following args must be nonnegative: t, v_mph"

    v = v_mph * MPH_TO_M_S
    
    if v < BRAKE_V1:
      # implements equation 2.1.3
      vel_final = max(0, v - BRAKE_A1 * t)
    else:
      # implements equation 2.1.4
      t_1 = (v - BRAKE_V1) / BRAKE_A2
      
      if t < t_1:
        vel_final = v - (BRAKE_A2 * t)
      else:
        vel_final = max(0, BRAKE_V1 - (BRAKE_A1 * (t - t_1))) 

    return vel_final
  
  def calc_brake_dist(self, v_mph):
    '''Returns the dist required to brake to a stop from v_mph'''
    assert v_mph >= 0, \
      "The following args must be nonnegative: v_mph"
    v = v_mph * MPH_TO_M_S

    # implements equation 2.1.2
    if v < BRAKE_V1:
      d_final = 0.5 * (v ** 2) / BRAKE_A1
    else:
      add1 = BRAKE_V1 * (v - BRAKE_V1) * (1 / BRAKE_A2)
      add2 = 0.5 * ((v - BRAKE_V1) ** 2) / BRAKE_A2
      add3 = 0.5 * (BRAKE_V1 ** 2) / BRAKE_A1
      d_final = add1 + add2 + add3
    return d_final

  def stop_to_stop_time(self, d_tot_mi, v_max_mph, t_dwell=60):
    '''
    Returns the total arrival-to-arrival travel time from one stop to the next
    Returns -1 if travel time cannot be calculated
    d_mi = track distance between the two stops
    vmax_mph = practical top track speed
    t_dwell (optional) = dwell time at first stop
    '''
    assert all([d_tot_mi > 0, v_max_mph > 0]), \
      "The following args must be positive: d_tot_mi, v_max_mph"
    assert t_dwell >= 0, \
      "The following args must be nonnegative: t_dwell"
    
    v_max = v_max_mph * MPH_TO_M_S
    d_tot = d_tot_mi * MI_TO_M

    t_acc = self.calc_accel_time(v_max_mph)
    # v_max_mph error case
    if t_acc == -1:
        print("Error: v_max_mph is unrealistic; speed is not reachable! Travel time cannot be calculated! Check params and their units!")
        return -1
    d_acc = self.calc_accel_dist(t_acc)
    t_brake = self.calc_brake_time(v_max_mph)
    d_brake = self.calc_brake_dist(v_max_mph)

    #implements algorithm 3.3.2
    i = 0
    while not (d_acc + d_brake <= d_tot):
      print(f"{dist_units_str(d_tot)} is insufficient to accelerate to and brake from {vel_units_str(v_max)}! Lowering v_max by 0.5%")
      v_max_mph =  v_max_mph * 0.995
      v_max = v_max_mph * MPH_TO_M_S

      t_acc = self.calc_accel_time(v_max_mph)
      d_acc = self.calc_accel_dist(t_acc)
      t_brake = self.calc_brake_time(v_max_mph)
      d_brake = self.calc_brake_dist(v_max_mph)

      # d_tot_mi error case
      if i > 100:
        print("Error: d_tot_mi is unrealistic; distance is much too short vs. acceleration/deceleration time needed! Travel time cannot be calculated! Check params and their units!")
        return -1
      i += 1

    print(f"Returning stop-to-stop travel time: distance {dist_units_str(d_tot)}, practical top speed {vel_units_str(v_max)}, dwell time {t_dwell} s")
    #implements equation 3.1.1
    d_vmax = d_tot - d_acc - d_brake
    #implements equation 3.1.2
    t_vmax = d_vmax / v_max

    #implements equation 3.2.1
    t_total = t_dwell + t_acc + t_vmax + t_brake
    
    return t_total

  def plot_vel_curve(self, v_max_mph, accel=True):
    '''accel=True: Displays a plot of v (acceleration up to v_max_mph) as a function of t'''
    '''accel=False: Displays a plot of v (braking down from v_max_mph) as a function of t'''
    assert v_max_mph > 0, \
      "The following args must be positive: v_max_mph"

    if accel:
      t_max = self.calc_accel_time(v_max_mph)
      # get v vs t at 1000 evenly-distributed points
      x_t = np.linspace(0, t_max, 1000)
      y_v = np.array([self.calc_accel_vel(t) for t in x_t])
      title = "Acceleration"
    else:
      t_max = self.calc_brake_time(v_max_mph)
      x_t = np.linspace(0, t_max, 1000)
      y_v = np.array([self.calc_brake_vel(t, v_max_mph) for t in x_t])
      title = "Braking"

    # convert speeds back to mph
    y_v = y_v / MPH_TO_M_S

    fig, ax = plt.subplots()
    # show v ticks every 5 mph
    ax.set_yticks([i for i in range(0, int(np.ceil(v_max_mph)) + 6, 5)])

    # t granularity to show at most 20 ticks
    if t_max <= 20: t_gran = 1
    elif t_max < 40: t_gran = 2
    elif t_max < 100: t_gran = 5
    elif t_max < 200: t_gran = 10
    elif t_max < 300: t_gran = 15
    elif t_max < 400: t_gran = 20
    else: t_gran = 30

    ax.set_xticks([i for i in range(0, int(np.ceil(t_max)) + t_gran + 1, t_gran)])
    
    
    plt.plot(x_t, y_v)
    plt.grid(linestyle = 'dotted')
    plt.title(title)
    plt.xlabel('Time (s)')
    plt.ylabel('Speed (mph)')
    plt.show()