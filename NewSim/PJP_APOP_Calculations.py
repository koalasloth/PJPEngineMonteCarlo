import random
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc



# Ideal Gas Properties Table
gas_prop_table_1 = open('ideal_gas_prop.csv')
gas_prop_table_2 = np.loadtxt(gas_prop_table_1, delimiter = ' ')

t = 0
h = 1
p = 2

def table_interp(val1, col_from, col_to):

    table_from = gas_prop_table_2[:, col_from]
    table_to = gas_prop_table_2[:, col_to]
    
    index = np.argmax(table_from >= val1)
    ratio = (val1 - table_from[index - 1]) / (table_from[index] - table_from[index - 1])
    val2 = ratio * (table_to[index] - table_to[index - 1]) + table_to[index - 1]

    return val2

# Pressure: kPa (relative pressure: no units)
# Temperature: K
# Power: kW
# Calorific Value: kJ/kg

def calc():

    # Input variables
    maxFuelFlow = 390 #ml/min
    Tmax = 100 # Newtons from max fuel flow
    v_in = 0 #km/hr, velocity in
    v_out = 1560 #km/hr
    exitExhaustTempMaxLB = 480 #deg 
    exitExhaustTempMaxUB = 720 #deg 
    pressureRatio_compressor = 2.9
    m_air = 0.23 #kg/s, air mass flow rate

    # Atmospheric condition inputs
    t_atm = 300 #k, atmospheric temperature
    p_atm = 101.3 #kPa, atmospheric pressure
    d_atm = 1.225 #kg/m^3, atmospheric density

    # Fuel inputs
    d_kerosene = 0.821 #kg/m^3
    LHV_kerosene = 43.0 #MJ/kg

    # Combusion Efficiency
    # eff_combustion = 0.9
    eff_combustion = np.random.normal(0.7, 0.1)

    # Atmosphere, 1
    t_1 = t_atm
    p_1 = p_atm
    h_1 = table_interp(t_1, t, h)

    # Post compressor, 2 (assume isentropic)
    p_2 = pressureRatio_compressor * p_1
    p_2r = pressureRatio_compressor * table_interp(t_1, t, p)
    t_2 = table_interp(p_2r, p, t)
    h_2 = table_interp(t_2, t, h)
    w_2 = m_air * (h_2 - h_1)

    # Energy provided by fuel (kJ)
    m_fuel = d_kerosene * maxFuelFlow / 1000 / 60 #kg/s, fuel mass flow rate
    q_fuel_ideal = m_fuel * LHV_kerosene * 1000 # kJ
    q_fuel_actual = eff_combustion * q_fuel_ideal #kJ

    # Post combustor, 3
    h_3 = (q_fuel_actual / m_air) + h_2
    t_3 = table_interp(h_3, h, t)
    p_3r = table_interp(t_3, t, p)

    # Post turbine, 4 (assume isentropic, p = p_atm)
    p_4r = p_3r / pressureRatio_compressor
    t_4 = table_interp(p_4r, p, t)
    h_4 = table_interp(t_4, t, h)
    w_4 = m_air * (h_3 - h_4)

    # Thrust
    f_thrust = m_air * ((v_out - v_in) * 1000 / 3600)

    # Output
    data = np.array([t_1, h_1, p_1, t_2, h_2, p_2, p_2r, w_2, q_fuel_actual, t_3, h_3, p_3r, t_4, h_4, p_4r, w_4, f_thrust])
    return data

# Output
'''
print("Pressure required by compressor: ", round(p_2, 2), "kPa")
print("Temperature required by compressor: ", round(t_2, 2), "K")
print("Power required by compressor: ", round(w_2, 2), "kW")
print("Energy provided by fuel (combustor): ", round(q_fuel_actual, 2), "kJ")
print("Temperature at exit of combustor: ", round(t_3, 2), "K")
print("Work done by turbine: ", round(w_4, 2), "kW")
print("Thrust:", round(f_thrust, 2), "N")
'''

# Monte Carlo Simulations

# Inputs
num_simulations = 1
num_runs = 10000

# Tracking

tracker_sim_data = np.zeros(shape = (num_simulations, len(calc())))
t3_data = np.zeros(shape = (num_simulations, num_runs))

# Simulations
for i in range(num_simulations):
    tracker_run_total = np.zeros(shape = len(calc()))
    tracker_run_data = np.zeros(shape = (num_runs, len(calc())))
    # Runs
    for j in range(num_runs):
        data = calc()
        new = np.zeros(shape = len(data))
        for k in range(len(data)):
            cur = tracker_run_total[k]
            new[k] = (cur * j + data[k]) / (j + 1)
        tracker_run_data[j] = new
        tracker_run_total = new
    # Simulation data
    tracker_sim_data[i] = tracker_run_total
    # Specific metric data
    t3_data[i] = tracker_run_data[:, 9] 


# Plot output

print(tracker_sim_data)

plt.xlim(0, num_runs)
plt.plot(t3_data[0])
plt.show()