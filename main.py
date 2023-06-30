import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import os
from site_setup import Site
from opt_algo import Optimization
from py_wake import BastankhahGaussian
from py_wake.examples.data import wtg_path
from py_wake.wind_turbines import WindTurbine, WindTurbines
#%% SETUP SITE
#1 - HornsRev 2 - IEA37 Test site
choose_site = 2
site = Site.setup_site(choose_site)
wt_x_init = list(site.wt_x_orig)
wt_y_init = list(site.wt_y_orig)

wt = site.wt_list
#1 - V80 2 - IEA3.35
D_rotor = list(wt._diameters)
hub_heights = list(wt._hub_heights)

power_rated1 = float(wt.power(20,type = 0))*1e-6
power_rated2 = float(wt.power(20,type = 1))*1e-6
power_rated3 = float(wt.power(20,type = 2))*1e-6
rated_power = [power_rated1,power_rated2,power_rated3]
rated_rpm = [12,12,12]
water_depth = [15]
site_chosen = site.site_orig
lcoe_max = 0
lcoe_min = 10

#%% FILE NAME MAGIC
number_of_runs = 1
min_wt_dist = site.min_dist
for i in range(number_of_runs):
    start_time = time.time()
    plt.close('all')
    dir_name = "Run" + str(i)
    parent_dir = 'E:\EWEM\Thesis\HornsRev\Thesis_Code_Final\Random_Search\Runs'  
    dir_path = os.path.join(parent_dir, dir_name) 
    os.mkdir(dir_path)
    file_name = "Run" + str(i) + ".txt"
    file_path = os.path.join(dir_path, file_name)
    sys.stdout = open(file_path, 'x')

    print('This is Run number %f' %i)
    print()
    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')


    
    #%% SETUP BOUNDS 
    left_bound = min(wt_x_init)
    right_bound = max(wt_x_init)
    top_bound = max(wt_y_init)
    bot_bound = min(wt_y_init)
    
    wf_bounds = [left_bound, right_bound, top_bound, bot_bound]
    
    #%% RUN OPTIMIZATION PROBLEM
    maximum_step_size = 5000
    max_iterations = 1000
    
    optimization_problem = Optimization.optimize(maximum_step_size,
                                                max_iterations,wt_x_init,
                                                wt_y_init,site_chosen,wt,
                                                wf_bounds,min_wt_dist,site,
                                                site.min_capacity,
                                                site.max_capacity,site.cap_t1,
                                                site.cap_t2,site.cap_t3,D_rotor,
                                                hub_heights,rated_power,rated_rpm,
                                                water_depth)
    
    
    
                            
    #%% PLOTS
    wf_boundary = [(left_bound,top_bound),(right_bound,top_bound),
                   (bot_bound,right_bound),(bot_bound,left_bound)]
    
    
    aep_plot = np.reshape(optimization_problem.aep_plot,(len(optimization_problem.iter_plot)
                                                         )).astype(float)
    iter_plot = np.reshape(optimization_problem.iter_plot,
                           (len(optimization_problem.iter_plot))).astype(float)
    irr_plot = np.reshape(optimization_problem.irr_plot,(len(optimization_problem.iter_plot)
                                                         )).astype(float)
    
    lcoe_plot = np.reshape(optimization_problem.lcoe_plot,(len(optimization_problem.iter_plot)
                                                         )).astype(float)
    
    # number_of_turb_plot = np.reshape(optimization_problem.number_of_turb_plot,(len(optimization_problem.iter_plot)
    #                                                      )).astype(float)
    fig_1 = plt.figure()
    wt.plot(wt_x_init, wt_y_init)
    # plt.plot(wf_boundary[0],wf_boundary[1], 'b', linestyle="--")
    # plt.plot(wf_boundary[1],wf_boundary[2], 'b', linestyle="--")
    # plt.plot(wf_boundary[2],wf_boundary[3], 'b', linestyle="--")
    # plt.plot(wf_boundary[3],wf_boundary[0], 'b', linestyle="--")
    plt.plot([wf_bounds[0],wf_bounds[1]],[wf_bounds[2],wf_bounds[2]], 'b', linestyle="--")
    plt.plot([wf_bounds[1],wf_bounds[1]],[wf_bounds[2],wf_bounds[3]], 'b', linestyle="--")
    plt.plot([wf_bounds[1],wf_bounds[0]],[wf_bounds[3],wf_bounds[3]], 'b', linestyle="--")
    plt.plot([wf_bounds[0],wf_bounds[0]],[wf_bounds[3],wf_bounds[2]], 'b', linestyle="--")
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.title('Original layout')
    fig_1.savefig(file_path + 'Initial_layout.png')
    type_vec_list = list(optimization_problem.type_vector)
    
    fig_2 = plt.figure()
    wt.plot(optimization_problem.wt_x_optimized, 
            optimization_problem.wt_y_optimized,type = optimization_problem.type_vector)
    # plt.plot(wf_boundary[0],wf_boundary[1], 'b', linestyle="--")
    # plt.plot(wf_boundary[1],wf_boundary[2], 'b', linestyle="--")
    # plt.plot(wf_boundary[2],wf_boundary[3], 'b', linestyle="--")
    # plt.plot(wf_boundary[3],wf_boundary[0], 'b', linestyle="--")
    plt.plot([wf_bounds[0],wf_bounds[1]],[wf_bounds[2],wf_bounds[2]], 'b', linestyle="--")
    plt.plot([wf_bounds[1],wf_bounds[1]],[wf_bounds[2],wf_bounds[3]], 'b', linestyle="--")
    plt.plot([wf_bounds[1],wf_bounds[0]],[wf_bounds[3],wf_bounds[3]], 'b', linestyle="--")
    plt.plot([wf_bounds[0],wf_bounds[0]],[wf_bounds[3],wf_bounds[2]], 'b', linestyle="--")
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.title('Optimized layout')   
    fig_2.savefig(file_path + 'Optimized_layout.png')
    
    fig_3 = plt.figure()
    plt.plot(iter_plot,aep_plot)
    plt.ylabel('AEP [GWh]')
    plt.xlabel('Number of iterations')
    plt.title('Convergence History')
    fig_3.savefig(file_path + 'AEP_conv_hist.png')
    
    fig_4 = plt.figure()
    plt.plot(iter_plot,irr_plot)
    plt.ylabel('IRR [%]')
    plt.xlabel('Number of iterations')
    plt.title('Convergence History')
    fig_4.savefig(file_path +'IRR_conv_hist.png')
    
    fig_5 = plt.figure()
    plt.plot(iter_plot,lcoe_plot)
    plt.ylabel('LCoE [EUR/kWh]')
    plt.xlabel('Number of iterations')
    plt.title('Convergence History')
    fig_5.savefig(file_path +'LCOE_conv_hist.png')
    
    end_time = time.time()
    print('Run time of script ---- %f seconds ----'%(end_time - start_time))
#%% CALCULATE MAX AND MIN VALUES FOR EVERYTHING
    if number_of_runs == 0:
        lcoe_max = lcoe_plot[-1]
        lcoe_min = lcoe_plot[-1]
    if lcoe_plot[-1] > lcoe_max:
        lcoe_max = lcoe_plot[-1]
        lcoe_max_iter = i
    if lcoe_plot[-1] < lcoe_min:
        lcoe_min = lcoe_plot[-1]
        lcoe_min_iter = i
print('LCoE minimum found at iteration number %f'%lcoe_min_iter)
print('LCoE maximum found at iteration number %f'%lcoe_max_iter)


#%% PLOTS
plt.figure()
wd_distribution = site_chosen.plot_wd_distribution(n_wd=12, ws_bins=[0,5,10,15,20,25])
plt.figure()
ws_distribution= site_chosen.plot_ws_distribution(wd=[0,90,180,270])


wtg_file = os.path.join(wtg_path, 'NEG-Micon-2750.wtg')
neg2750 = WindTurbine.from_WAsP_wtg(wtg_file)