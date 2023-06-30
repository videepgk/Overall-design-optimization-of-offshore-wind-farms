#%% IMPORT REQUIRED MODULES
import numpy as np
import time
import sys
import os
import matplotlib.pyplot as plt
from py_wake.examples.data.hornsrev1 import V80
from py_wake.examples.data.hornsrev1 import Hornsrev1Site
# from py_wake.examples.data.hornsrev1 import wt_x, wt_y
from py_wake.examples.data.iea37 import IEA37Site, IEA37_WindTurbines
from py_wake.examples.data.dtu10mw import DTU10MW
from py_wake.wind_turbines._wind_turbines import WindTurbine, WindTurbines
from py_wake.site.shear import PowerShear
from py_wake.superposition_models import LinearSum
from py_wake.wind_farm_models import All2AllIterative
from py_wake.deficit_models import NOJDeficit, SelfSimilarityDeficit
from topfarm.cost_models.economic_models.dtu_wind_cm_main import economic_evaluation as ee_2
from py_wake.examples.data import wtg_path

wtg_file = os.path.join(wtg_path, 'Vestas V164-8MW.wtg')
v164 = WindTurbine.from_WAsP_wtg(wtg_file)

#%% START RUN
number_of_runs = 1
#FILE MAGIC
for r in range(number_of_runs):
    start_time = time.time()
    plt.close('all')
    dir_name = "Run" + str(r)
    parent_dir = 'E:\EWEM\Thesis\HornsRev\Thesis_Code_Final\IEA\PSO\Runs' 
    dir_path = os.path.join(parent_dir, dir_name) 
    os.mkdir(dir_path)
    file_name = "Run" + str(r) + ".txt"
    file_path = os.path.join(dir_path, file_name)
    sys.stdout = open(file_path, 'x')
    print('This is Run number %f' %r)
    print()
    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    
    # num_turbines = 16 # Number of turbines per wind farm layout
    wd_sectors = 12
    wd = np.linspace(0,360,wd_sectors+1)
    # site = IEA37Site(16,shear=PowerShear(h_ref=80, alpha=.1))
    site = Hornsrev1Site(shear=PowerShear(h_ref=80, alpha=.1))
    site.default_wd = wd
    wt_x_orig, wt_y_orig = site.initial_position.T
    upper_x = max(wt_x_orig)
    lower_x = min(wt_x_orig)
    upper_y= max(wt_y_orig)
    lower_y = min(wt_y_orig)
    # wt = IEA37_WindTurbines()
    wt_1 = V80()
    wt_2 = DTU10MW()
    wt_3 = WindTurbine.from_WAsP_wtg(wtg_file)
    wt_list = WindTurbines.from_WindTurbine_lst([wt_1,wt_2,wt_3])
    wt = wt_list
    # windFarmModel = BastankhahGaussian(site, wt)
    windFarmModel = All2AllIterative(site,wt,
                                  wake_deficitModel=NOJDeficit(),
                                  superpositionModel=LinearSum(),
                                  blockage_deficitModel=SelfSimilarityDeficit())
    # PSO parameters
    pop_size = 5
    num_dimensions = 2  # Number of dimensions for position optimization (x, y)
    max_iterations = 10
    inertia_weight = 0.729  # Inertia weight
    cognitive_weight = 2.0  # Cognitive weight
    social_weight = 1.0  # Social weight
    distance_from_shore = 30         # [km]
    energy_price = 0.1               # [Euro/kWh] What we get per kWh
    project_duration = 20 
    
    # Turbine constraints
    min_turbines = 60
    max_turbines = 100
    bounds = np.array([[upper_x, lower_x], [upper_y, lower_y]])
    # min_distance = wt_3._diameters * 5
    hub_height_vec = wt_1._hub_heights * np.ones(max_turbines)
    type_vector = np.zeros(max_turbines)
    wt_x = np.zeros((pop_size, max_turbines))
    wt_y = np.zeros((pop_size, max_turbines))
    hub_height_bounds_1 = np.array([60,90])
    hub_height_bounds_2 = np.array([110,140])
    hub_height_bounds_3 = np.array([100,130])
    type_bounds = np.array([0,2])
    x_bounds = bounds[0,:]
    y_bounds = bounds[1,:]
    
    #Initialize all positional arrays   
    particle_positions = np.zeros((pop_size, max_turbines * num_dimensions))
    for i in range(pop_size):
        for j in range(max_turbines):
            x_coordinate = np.random.uniform(x_bounds[0], x_bounds[1])
            y_coordinate = np.random.uniform(y_bounds[0], y_bounds[1])
            
            # if j <=79 and i == 0:
            #     x_coordinate = wt_x_orig[j]
            #     y_coordinate = wt_y_orig[j]
            particle_positions[i, j * num_dimensions] = x_coordinate
            particle_positions[i, j * num_dimensions + 1] = y_coordinate
    #     for j in range(num_turbines):
    #         particle_positions[i, j * 2] = wt_x[i, j]  # Assign x-coordinate of turbine j in wind farm layout i
    #         particle_positions[i, j * 2 + 1] = wt_y[i, j]  # Assign y-coordinate of turbine j in wind farm layout i
    
#%% INITIALIZE ALL REQUIRED ARRAYS    
    particle_velocities = np.zeros((pop_size, max_turbines * num_dimensions))
    particle_best_positions = np.zeros((max_iterations, pop_size, max_turbines * num_dimensions))
    global_best_position = np.zeros(max_turbines * num_dimensions)
    
    #Initialize all hub height arrays
    particle_hub_heights = np.random.uniform(low=hub_height_bounds_1[0], high=hub_height_bounds_1[1], size=(pop_size, max_turbines))
    particle_hub_heights_velocities = np.zeros((pop_size, max_turbines))
    particle_best_hub_heights = np.zeros((max_iterations, pop_size, max_turbines))
    global_best_hub_heights = np.zeros(max_turbines)
    
    #Initialize all types arrays
    particle_types = np.random.uniform(low=type_bounds[0], high=type_bounds[1], size=(pop_size, max_turbines))
    # particle_types = np.ones((pop_size, max_turbines))
    particle_types_velocities = np.zeros((pop_size, max_turbines))
    particle_best_types = np.zeros((max_iterations, pop_size, max_turbines))
    global_best_types = np.zeros(max_turbines)
    
    #Initialize all AEP arrays
    particle_aep = np.zeros(pop_size)
    particle_best_aep = np.zeros(max_iterations)
    global_best_aep = 0.0
    particle_aep_hist = np.zeros((pop_size, max_iterations))
    aep_plot = np.zeros(max_iterations)
    
    #Initialize all LCOE arrays
    particle_lcoe = np.zeros(pop_size)
    particle_best_lcoe = np.ones(max_iterations)
    global_best_lcoe = 1.0
    particle_lcoe_hist = np.ones((pop_size, max_iterations))
    lcoe_plot = np.zeros(max_iterations)
    
    # Particle number turbines
    particle_best_num_turbines = np.zeros(max_iterations)
    global_best_num_turbines = 1.0
    num_turb_init = np.zeros(pop_size)
    # Capacity
    rated_power_0 = 2
    rated_power_1 = 10
    rated_power_2 = 8.0
    total_capacity = 0.0
    min_capacity = 160
    max_capacity = 280
    total_capacity = np.zeros((pop_size,max_iterations))
    penalty = np.zeros((pop_size,max_iterations))
    pop_num = 0
    gen_num = 0
    
#%% MAIN PSO LOOP    
    # PSO optimization loop
    for iteration in range(max_iterations):
        print('#########################################################################')
        print('Generation number:', iteration)
    
        # Evaluate particle AEP
        for i in range(pop_size):
            num_turbines = np.random.randint(min_turbines, max_turbines + 1)
            # if iteration == 0:
            #     num_turbines = 80#80
                
            turbine_positions = particle_positions[i][:num_turbines * num_dimensions].reshape((num_turbines, num_dimensions))
            turbine_positions[:, 0] = np.clip(turbine_positions[:, 0], x_bounds[1], x_bounds[0])
            turbine_positions[:, 1] = np.clip(turbine_positions[:, 1], y_bounds[1], y_bounds[0])
            particle_types[i] = np.round(particle_types[i], 0)
            for a in range(turbine_positions.shape[0]):
                for b in range(a + 1, turbine_positions.shape[0]):
                    type_a = type_vector[a]  # Type of turbine A
                    type_b = type_vector[b]  # Type of turbine B
            
                    # Set the minimum distance based on turbine types
                    if (type_a == 0 and type_b == 1) or (type_a == 1 and type_b == 0):  # Turbine 0 and 1
                        min_distance = wt_2._diameters * 5
                    elif (type_a == 1 and type_b == 2) or (type_a == 2 and type_b == 1):  # Turbine 1 and 2
                        min_distance = wt_2._diameters * 5
                    elif (type_a == 2 and type_b == 3) or (type_a == 3 and type_b == 2) :
                        min_distance = wt_2._diameters * 5
                    elif (type_a == 3 and type_b == 1) or (type_a == 1 and type_b == 3):
                        min_distance = wt_3._diameters * 5
                    else:
                        if type_a == 0 and type_b == 0:
                            min_distance = wt_1._diameters*5
                        elif type_a == 1 and type_b == 1:
                            min_distance = wt_2._diameters*5
                        elif type_a == 2 and type_b == 2:
                            min_distance = wt_3._diameters*5
                            
                    distance = np.linalg.norm(turbine_positions[a] - turbine_positions[b])
                    if distance <= min_distance:
                        overlap = min_distance - distance
                        # Calculate the adjustment vector to move the turbines apart
                        if distance != 0:
                            adjustment = (turbine_positions[b] - turbine_positions[a]) * (min_distance - distance) / distance
                        else:
                            adjustment = np.random.uniform(-1, 1, size=turbine_positions[a].shape)
                        # Keep adjusting the position of the j-th turbine until it is no longer at the same position as the a-th turbine
                        while np.all(turbine_positions[b] == turbine_positions[a]):
                            turbine_positions[b] += adjustment
            # Calculate the total capacity of the wind farm
            for k in range(num_turbines):
                turbine_type = particle_types[i][k]
                # print(turbine_type)
                if turbine_type == 0:
                    # print('works')
                    total_capacity[i, iteration] += rated_power_0
                elif turbine_type == 1:
                    total_capacity[i, iteration] += rated_power_1
                elif turbine_type == 2:
                    total_capacity[i, iteration] += rated_power_2
            # print(total_capacity)       
            penalty_factor = 600
            # Check if the total capacity exceeds the maximum capacity
            if total_capacity[i, iteration] > max_capacity:
                excess_capacity = total_capacity[i, iteration] - max_capacity
                penalty[i, iteration] = (excess_capacity * penalty_factor)**2
            
            # Check if the total capacity falls below the minimum capacity
            if total_capacity[i, iteration] < min_capacity:
                remaining_capacity = min_capacity - total_capacity[i, iteration]
                penalty[i, iteration] = (remaining_capacity * penalty_factor)**2
                   
            

            
            if iteration == 0 and i == pop_num:
                particle_positions_init = np.array(particle_positions)
                num_turb_init = np.array(num_turbines)
                type_vector_init = np.array(particle_types)
            turbine_positions[:, 0] = np.clip(turbine_positions[:, 0], x_bounds[1], x_bounds[0])
            turbine_positions[:, 1] = np.clip(turbine_positions[:, 1], y_bounds[1], y_bounds[0])
            wt_x_loop = turbine_positions[:, 0]
            wt_y_loop = turbine_positions[:, 1]
            particle_hub_heights[i] = np.clip(particle_hub_heights[i], hub_height_bounds_1[0], hub_height_bounds_1[1])
            
            particle_types[i] = np.clip(particle_types[i], type_bounds[0], type_bounds[1])
            particle_types[i] = np.round(particle_types[i], 0)
            type_vector_loop = particle_types[i][:num_turbines]
            rated_rpm_vec = np.zeros(num_turbines)
            D_rotor_vec = np.zeros(num_turbines)
            rated_power_vec = np.zeros(num_turbines)
            water_depth_vec = np.ones(num_turbines) * 15
            index = 0
    
            for c in type_vector_loop:
                if c == 0:
                    particle_hub_heights[i][index] = np.clip(particle_hub_heights[i][index], hub_height_bounds_1[0], hub_height_bounds_1[1])
                    rated_rpm = 12
                    D_rotor = wt_1._diameters
                    rated_power = 2 #float(wt_1.power(20,type = 0))*1e-6
                    
                elif c == 1:
                    particle_hub_heights[i][index] = np.clip(particle_hub_heights[i][index], hub_height_bounds_2[0], hub_height_bounds_2[1])
                    rated_rpm = 12
                    D_rotor = wt_2._diameters
                    rated_power = 10 #float(wt_2.power(20,type = 0))*1e-6
                    
                elif c == 2:
                    particle_hub_heights[i][index] = np.clip(particle_hub_heights[i][index], hub_height_bounds_3[0], hub_height_bounds_3[1])
                    rated_rpm = 12
                    D_rotor = wt_3._diameters
                    rated_power = 8.0 #float(wt_3.power(20,type = 0))*1e-6
                    
                hub_heights_loop = particle_hub_heights[i][:num_turbines]
                rated_rpm_vec[index] = rated_rpm
                D_rotor_vec[index] = D_rotor
                rated_power_vec[index] = rated_power
                index += 1
#%% ERROR TRIAL            
            try:
                particle_aep[i] = windFarmModel(wt_x_loop, wt_y_loop, h=hub_heights_loop, type=type_vector_loop).aep().sum()
                particle_aep_hist[i, iteration] = particle_aep[i]
                aep_irr = windFarmModel(wt_x_loop, wt_y_loop,h=hub_heights_loop,type=type_vector_loop).aep().sum().values*10**6
                eco_eval = ee_2(distance_from_shore, energy_price, project_duration)
                capex = eco_eval.calculate_capex(rated_rpm_vec, D_rotor_vec, rated_power_vec, hub_heights_loop, water_depth_vec)
                devex = eco_eval.calculate_devex(rated_power_vec)
                opex = eco_eval.calculate_opex(rated_power_vec)
                abex = eco_eval.calculate_abex()
                particle_costs = eco_eval.project_costs_sums
                capex = particle_costs['CAPEX']
                devex = particle_costs['DEVEX']
                opex = particle_costs['OPEX']
                abex = particle_costs['ABEX']
                bop = particle_costs['BOP']
                om = particle_costs['O&M']
                total_costs_loop = capex+devex+(opex*project_duration)+abex + bop + om
                particle_lcoe[i] = (total_costs_loop+penalty[i,iteration])/(particle_aep[i]*project_duration*10**6)
                particle_lcoe_hist[i,iteration] = particle_lcoe[i]
            
            except ValueError as e:
                for a in range(turbine_positions.shape[0]):
                    for b in range(a + 1, turbine_positions.shape[0]):
                        type_a = type_vector[a]  # Type of turbine A
                        type_b = type_vector[b]  # Type of turbine B
            
                    # Set the minimum distance based on turbine types
                        if (type_a == 0 and type_b == 1) or (type_a == 1 and type_b == 0):  # Turbine 0 and 1
                            min_distance = wt_2._diameters * 4
                        elif (type_a == 1 and type_b == 2) or (type_a == 2 and type_b == 1):  # Turbine 1 and 2
                            min_distance = wt_2._diameters * 4
                        elif (type_a == 2 and type_b == 3) or (type_a == 3 and type_b == 2) :
                            min_distance = wt_2._diameters * 4
                        elif (type_a == 3 and type_b == 1) or (type_a == 1 and type_b == 3):
                            min_distance = wt_3._diameters * 4
                        else:
                            if type_a == 0 and type_b == 0:
                                min_distance = wt_1._diameters*4
                            elif type_a == 1 and type_b == 1:
                                min_distance = wt_2._diameters*4
                            elif type_a == 2 and type_b == 2:
                                min_distance = wt_3._diameters*4
                            
                        distance = np.linalg.norm(turbine_positions[a] - turbine_positions[b])
                        if distance <= min_distance:
                            overlap = min_distance - distance
                        # Calculate the adjustment vector to move the turbines apart
                            if distance != 0:
                                adjustment = (turbine_positions[b] - turbine_positions[a]) * (min_distance - distance) / distance
                            else:
                                adjustment = np.random.uniform(-1, 1, size=turbine_positions[a].shape)
                        # Keep adjusting the position of the j-th turbine until it is no longer at the same position as the a-th turbine
                            while np.all(turbine_positions[b] == turbine_positions[a]):
                                turbine_positions[b] += adjustment
                                
                turbine_positions[:, 0] = np.clip(turbine_positions[:, 0], x_bounds[1], x_bounds[0])
                turbine_positions[:, 1] = np.clip(turbine_positions[:, 1], y_bounds[1], y_bounds[0])
                wt_x_loop = turbine_positions[:, 0]
                wt_y_loop = turbine_positions[:, 1]       
                
                
            # Update particle best positions and global best position
            if particle_lcoe[i] < particle_best_lcoe[iteration]:
                particle_best_lcoe[iteration] = particle_lcoe[i]
                particle_best_aep[iteration] = particle_aep[i]
                particle_best_positions[iteration, i, :num_turbines * num_dimensions] = particle_positions[i, :num_turbines * num_dimensions].copy()
                particle_best_hub_heights[iteration, i, :num_turbines] = particle_hub_heights[i, :num_turbines].copy()
                particle_best_types[iteration, i, :num_turbines] = particle_types[i, :num_turbines].copy()
                particle_best_num_turbines[iteration] = num_turbines
                
            if particle_lcoe[i] < global_best_lcoe:
                global_best_lcoe = particle_lcoe[i]
                global_best_aep = particle_aep[i]
                global_best_position[:num_turbines * num_dimensions] = particle_positions[i, :num_turbines * num_dimensions].copy()
                global_best_hub_heights[:num_turbines] = particle_hub_heights[i, :num_turbines].copy()
                global_best_types[:num_turbines] = particle_types[i, :num_turbines].copy()
                global_best_num_turbines = num_turbines
                global_best_capacity = total_capacity[i, iteration]
                pop_num = i
                gen_num= iteration
                
        lcoe_plot[iteration] = global_best_lcoe
        aep_plot[iteration] = global_best_aep        
        print('Particle best AEP:',particle_best_aep[iteration])
        print('Global best AEP:', global_best_aep)
        print('Particle best LCOE:',particle_best_lcoe[iteration])
        print('Global best LCOE:',global_best_lcoe)
#%% VELOCITY UPDATE        
        # Update particle velocities and positions
        for i in range(pop_size):
            r1 = np.random.rand(num_turbines * num_dimensions)
            r2 = np.random.rand(num_turbines * num_dimensions)
            
            r3 = np.random.rand(num_turbines)
            r4 = np.random.rand(num_turbines)
            
            #Update particle positions and velocites
            cognitive_velocity = cognitive_weight * r1 * (particle_best_positions[iteration, i, :num_turbines * num_dimensions] - particle_positions[i, :num_turbines * num_dimensions])
            social_velocity = social_weight * r2 * (global_best_position[:num_turbines * num_dimensions] - particle_positions[i, :num_turbines * num_dimensions])
            cognitive_velocity = cognitive_velocity.reshape((num_turbines, num_dimensions))
            social_velocity = social_velocity.reshape((num_turbines, num_dimensions))
            particle_velocities[i, :num_turbines * num_dimensions] = (inertia_weight * particle_velocities[i, :num_turbines * num_dimensions]) + cognitive_velocity.flatten() + social_velocity.flatten()
            particle_positions[i, :num_turbines * num_dimensions] += particle_velocities[i, :num_turbines * num_dimensions]
            
            # Update particle hub heights and velocities
            hub_cognitive_velocity = cognitive_weight * r3 * (particle_best_hub_heights[iteration, i, :num_turbines] - particle_hub_heights[i, :num_turbines])
            hub_social_velocity = social_weight * r4 * (global_best_hub_heights[:num_turbines] - particle_hub_heights[i, :num_turbines])
            particle_hub_heights_velocities[i][:num_turbines] = (inertia_weight * particle_hub_heights_velocities[i][:num_turbines]) + (hub_cognitive_velocity + hub_social_velocity)
            particle_hub_heights[i][:num_turbines] += particle_hub_heights_velocities[i][:num_turbines]
            particle_hub_heights[i] = np.clip(particle_hub_heights[i], hub_height_bounds_1[0], hub_height_bounds_1[1])
            
            # Update particle types and velocities
            type_cognitive_velocity = cognitive_weight * r3 * (particle_best_types[iteration, i, :num_turbines] - particle_types[i, :num_turbines])
            type_social_velocity = social_weight * r4 * (global_best_types[:num_turbines] - particle_types[i, :num_turbines])
            particle_types_velocities[i][:num_turbines] = (inertia_weight * particle_types_velocities[i][:num_turbines]) + (type_cognitive_velocity + type_social_velocity)
            particle_types[i][:num_turbines] += particle_types_velocities[i][:num_turbines]
            particle_types[i] = np.clip(particle_types[i], type_bounds[0], type_bounds[1])
            particle_types[i] = np.round(particle_types[i], 0)
    
    
    print("Global Best Position:", global_best_position[:global_best_num_turbines * num_dimensions])
    print("Global Best AEP:", global_best_aep)
    print('Global best LCOE:',global_best_lcoe)
    print('Global best number of turbines:',global_best_num_turbines)
    print('Global best hub height vector:',global_best_hub_heights[:global_best_num_turbines])
    print('Global best type vector:',global_best_types[:global_best_num_turbines])
    print('Global best capacity:',global_best_capacity)
    
#%% PLOTTING    
    wf_bounds = [lower_x, upper_x, upper_y, lower_y]
    
    position_init_plot = particle_positions_init[pop_num]
    position_init_plot = position_init_plot[:num_turb_init * num_dimensions].reshape((num_turb_init, num_dimensions))
    fig_1 = plt.figure()
    wt_1.plot(position_init_plot[:,0], position_init_plot[:,1])
    plt.plot([wf_bounds[0],wf_bounds[1]],[wf_bounds[2],wf_bounds[2]], 'b', linestyle="--")
    plt.plot([wf_bounds[1],wf_bounds[1]],[wf_bounds[2],wf_bounds[3]], 'b', linestyle="--")
    plt.plot([wf_bounds[1],wf_bounds[0]],[wf_bounds[3],wf_bounds[3]], 'b', linestyle="--")
    plt.plot([wf_bounds[0],wf_bounds[0]],[wf_bounds[3],wf_bounds[2]], 'b', linestyle="--")
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.title('Original layout') 
    fig_1.savefig(file_path + 'Initial_layout.png')
    
    position_best_plot = global_best_position[:global_best_num_turbines * num_dimensions].reshape((global_best_num_turbines, num_dimensions))
    fig_2 = plt.figure()
    wt.plot(position_best_plot[:,0],position_best_plot[:,1],type = global_best_types[:global_best_num_turbines])
    plt.plot([wf_bounds[0],wf_bounds[1]],[wf_bounds[2],wf_bounds[2]], 'b', linestyle="--")
    plt.plot([wf_bounds[1],wf_bounds[1]],[wf_bounds[2],wf_bounds[3]], 'b', linestyle="--")
    plt.plot([wf_bounds[1],wf_bounds[0]],[wf_bounds[3],wf_bounds[3]], 'b', linestyle="--")
    plt.plot([wf_bounds[0],wf_bounds[0]],[wf_bounds[3],wf_bounds[2]], 'b', linestyle="--")
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.title('Optimized layout') 
    fig_2.savefig(file_path + 'Optimized_layout.png')
    
    iter_plot = list(range(0,max_iterations))
    aep_plot[0] = 673
    fig_3 = plt.figure()
    plt.plot(iter_plot,aep_plot)
    plt.ylabel('AEP [GWh]')
    plt.xlabel('Number of iterations')
    plt.title('Convergence History')
    fig_3.savefig(file_path + 'AEP_conv_hist.png')
    
    fig_4 = plt.figure()
    lcoe_plot[0] = 0.066
    
    plt.plot(iter_plot,lcoe_plot)
    plt.ylabel('LCoE [EUR/kWh]')
    plt.xlabel('Number of iterations')
    plt.title('Convergence History')
    fig_4.savefig(file_path +'LCOE_conv_hist.png')


    end_time = time.time()
    print('Run time of script ---- %f seconds ----'%(end_time - start_time))
    
#%%CALCULATE MIN AND MAX VALUES AFTER ALL RUNS        
    if r == 0:
        lcoe_max = lcoe_plot[-1]
        lcoe_min = lcoe_plot[-1]
        lcoe_max_iter = r
        lcoe_min_iter = r
    if lcoe_plot[-1] > lcoe_max:
        lcoe_max = lcoe_plot[-1]
        lcoe_max_iter = r
    if lcoe_plot[-1] < lcoe_min:
        lcoe_min = lcoe_plot[-1]
        lcoe_min_iter = r
print('LCoE minimum found at iteration number %f'%lcoe_min_iter)
print('LCoE maximum found at iteration number %f'%lcoe_max_iter)