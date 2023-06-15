import numpy as np
from scipy.integrate import quad

### metric conversion constants ###
LB_TO_KG = 0.45359237
HP_TO_W = 745.699872
LBF_TO_N = 4.4482216
MPH_TO_M_S = 0.44704
MI_TO_M = 1609.344
IN_TO_M = 0.0254

### print() helpers to show dual units ###
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
  h = max cross-section height
  w = max cross-section width
  C_d = coefficient of drag

  returns:
  D = simplified coefficient of drag
  '''
  h = h_in * IN_TO_M
  w = w_in * IN_TO_M
  D_final = 0.5 * h * w * rho * C_d
  return D_final


class Train():
  def __init__(self, m_lb, P_hp, F_lbf, D=0):
    '''
    Initialize a Train from args:
    m_lb = mass of train (lb)
    P = traction power (hp)
    F_lbf = max tractive effort (lbf)
    D = simplified coefficient of drag
    '''
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
    # implement formula <FILL IN>
    self.v_1 = self.P/self.F
    # implement formula <FILL IN>
    self.t_1 = self.m * self.P / (self.F**2)
    print(f"Power limits traction above {vel_units_str(self.v_1)}, after {t_round_str(self.t_1)}")

  def calc_time_vel(self, v_mph):
    '''Returns the time required to reach v_mph (-1 if never)'''
    v = v_mph * MPH_TO_M_S
    if v <= self.v_1:
      # implement formula <FILL IN>
      t_final = self.m * v / self.F
    else:
      # implement formula <FILL IN>
      numer = self.m * (v**2 - self.v_1)
      denom = 2 * (self.P - (self.D * v**3))
      if denom < 0:
        return -1
      t_final = (numer / denom) + self.t_1
    return t_final

  def calc_vel_time(self, t):
    '''
    Returns the velocity after t s of acceleration
    by solving for v in equation of form av^3 + bv^2 + c = 0
    '''
    if t < self.t_1:
      # implement formula <FILL IN>
      vel_final = self.F * t / self.m
    else:
      # implement formula <FILL IN>
      a = 2 * self.D * (t - self.t_1)
      b = self.m
      c = (2 * self.P * (self.t_1 - t)) - (self.m * self.v_1)
      p = [a, b, 0, c]
      roots = np.roots(p)
      # required to extract real solution
      vel_final = abs(roots[-1])
    return vel_final

  def calc_dist_time(self, t):
    '''
    Returns the dist traveled (displacement) after t s of acceleration
    by integrating v(t)dt over [0, t]
    '''
    res, err = quad(self.calc_vel_time, 0, t)
    # ensure integral calculation is accurate
    assert err < res * 0.01, f"Distance calculated with high error +-{err}%"
    return res
