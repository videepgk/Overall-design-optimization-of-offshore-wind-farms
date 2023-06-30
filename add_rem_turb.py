import numpy as np
from py_wake import BastankhahGaussian
from py_wake import FugaBlockage
# from constraint_checker import Constraint_checker
from topfarm.cost_models.economic_models.dtu_wind_cm_main import economic_evaluation as ee_2
from constraint_checker_add_rem import Constraint_checker_add_rem
from py_wake.superposition_models import LinearSum
from py_wake.wind_farm_models import All2AllIterative
from py_wake.deficit_models import NOJDeficit, SelfSimilarityDeficit

class Change_number(object):
    def __init__(self,wt_x,wt_y,aep_plot, iter_plot,type_vector,
             iter_num,aep_new,converged,lay_change,
             D_rotor_vec,hub_height_vec,rated_power_vec,rated_rpm_vec,number_DTU,number_V80,
             number_IEA,irr_new,water_depth_vec,cap_eval,lcoe_new,lcoe_plot,number_of_turb_plot):
        self.wt_x = wt_x
        self.wt_y = wt_y
        self.aep_plot = aep_plot
        self.iter_plot = iter_plot
        self.type_vector = type_vector
        self.iter_num = iter_num
        self.aep_new = aep_new
        self.converged = converged
        self.lay_change = lay_change
        # self.other_turb = other_turb
        # self.cap_eval = cap_eval
        # self.max_choice_val = max_choice_val
        self.D_rotor_vec = D_rotor_vec
        self.hub_height_vec = hub_height_vec
        self.rated_power_vec = rated_power_vec
        self.rated_rpm_vec = rated_rpm_vec
        self.water_depth_vec = water_depth_vec
        self.number_DTU = number_DTU
        self.number_V80 = number_V80
        self.number_IEA = number_IEA
        self.irr_new = irr_new
        self.cap_eval = cap_eval
        self.lcoe_new = lcoe_new
        self.lcoe_plot = lcoe_plot
        self.number_of_turb_plot = number_of_turb_plot
        
    @classmethod
    def change_number_turb(cls,distance_from_shore, energy_price, 
                           project_duration,wt_x,wt_y,bounds,
                           min_dist,type_vector,aep_ref,irr_ref,site,wt,hub_height_vec,
                           rated_rpm_vec, D_rotor_vec, rated_power_vec, water_depth_vec,
                           D_rotor,hub_heights,rated_power,rated_rpm,water_depth,iter_num
                           ,aep_plot,irr_plot,iter_plot,converged,lay_change,max_step_size,
                           number_DTU,number_V80,number_IEA,type_1_cap,type_2_cap,type_3_cap,
                           cap_eval,max_cap,lcoe_ref,lcoe_plot,number_of_turb_plot):
        
        
        eco_eval = ee_2(distance_from_shore, energy_price, project_duration)
        lut_path = r"C:/Users/videe/AppData/Roaming/Python/Python38/site-packages/py_wake/tests/test_files/fuga/2MW/Z0=0.03000000Zi=00401Zeta0=0.00E+00"
        # windFarmModel = FugaBlockage(lut_path,site, wt)
        # windFarmModel = BastankhahGaussian(site, wt)
        windFarmModel = All2AllIterative(site,wt,
                                          wake_deficitModel=NOJDeficit(),
                                          superpositionModel=LinearSum(),
                                          blockage_deficitModel=SelfSimilarityDeficit())
        add_flag_num = 0
        rem_flag_num = 0
        one_iter = True
        arr_size = len(wt_x)
        # print(type(water_depth_vec))
        # print(len(wt_x))
        add_rem_choice = np.random.randint(1,3)
        # max_turb = 25
        # min_turb = 10
        max_turb = 20
        min_turb = 12
        number_of_turb = len(wt_x)
        if add_rem_choice == 1: #ADD
            print('Action chosen is No.4 : Adding turbine')
            while one_iter == True and number_of_turb<max_turb:
                check = False
                while check == False: 
                    random_turb_pick = np.random.randint(0,arr_size)
                    wt_x_loop = list(wt_x)
                    wt_y_loop = list(wt_y)
                    type_vector_loop = list(type_vector)
                    # print(len(type_vector_loop))
                    # print(len(wt_x_loop))
                    rated_rpm_vec_loop= list(rated_rpm_vec)
                    D_rotor_vec_loop = list(D_rotor_vec)
                    rated_power_vec_loop = list(rated_power_vec)
                    hub_height_vec_loop = list(hub_height_vec)
                    
                    water_depth_vec_loop = list(water_depth_vec)
                    x_resh = np.reshape(wt_x,(arr_size)).astype(int)
                    y_resh = np.reshape(wt_y,(arr_size)).astype(int)
            
                    x_rand_pick = x_resh[random_turb_pick]
                    y_rand_pick = y_resh[random_turb_pick]
            
            
                    move_size = np.random.random() * max_step_size
                    move_theta = np.random.random() * np.pi * 2
                    x_new =  x_rand_pick + move_size*np.sin(move_theta)
                    y_new =  y_rand_pick + move_size*np.cos(move_theta)
                    add_rem_check = Constraint_checker_add_rem.add_rem_checker(wt_x_loop,
                                                                 wt_y_loop,
                                                                  bounds, x_new,
                                                                  y_new,min_dist,type_vector)
                    
                    if add_rem_check.add_rem_check_flag == False:
                        check = False
                        
                    else:
                        check = True
                type_vector_loop = np.append(type_vector,0)
                D_rotor_vec_loop = np.append(D_rotor_vec,D_rotor[0])
                rated_rpm_vec_loop = np.append(rated_rpm_vec,rated_rpm[0])
                rated_power_vec_loop = np.append(rated_power_vec,rated_power[0])
                hub_height_vec_loop = np.append(hub_height_vec,hub_heights[0])
                water_depth_vec_loop = np.append(water_depth_vec,water_depth_vec[0])
                

                wt_x_loop = np.append(wt_x_loop,x_new)
                wt_y_loop = np.append(wt_y_loop,y_new)

                aep_new_loop = windFarmModel(wt_x_loop,wt_y_loop,h=hub_height_vec_loop,type=type_vector_loop).aep().sum()
                aep_irr = windFarmModel(wt_x_loop, wt_y_loop,h=hub_height_vec_loop,type = type_vector_loop).aep().sum(['wd','ws']).values*10**6
                
                irr_new_loop = eco_eval.calculate_irr(rated_rpm_vec_loop, D_rotor_vec_loop, 
                             rated_power_vec_loop, hub_height_vec_loop, 
                             water_depth_vec_loop, aep_irr)
                costs = eco_eval.project_costs_sums
                capex_loop = costs['CAPEX']
                devex_loop = costs['DEVEX']
                opex_loop = costs['OPEX']
                abex_loop = costs['ABEX']
                bop_loop = costs['BOP']
                om_loop = costs['O&M']
                total_costs_loop = capex_loop+devex_loop+(opex_loop*project_duration)+abex_loop+bop_loop+om_loop
                lcoe_new_loop = total_costs_loop/(aep_new_loop*project_duration*10**6)
                add_flag_num += 1    
                if lcoe_new_loop < lcoe_ref: #and cap_eval<max_cap:
                    
                    wt_x = wt_x_loop
                    wt_y = wt_y_loop 
                    print('Initial number of turbines is equal to : %f'%len(type_vector))
                    number_DTU = 0
                    number_V80 = 0
                    number_IEA = 0  
                    one_iter = False
                    iter_num += 1
                    aep_new = aep_new_loop
                    irr_new = irr_new_loop    
                    lcoe_new = lcoe_new_loop
                    type_vector = type_vector_loop
                    D_rotor_vec = D_rotor_vec_loop
                    rated_power_vec = rated_power_vec_loop
                    rated_rpm_vec = rated_rpm_vec_loop
                    hub_height_vec = hub_height_vec_loop
                    water_depth_vec = water_depth_vec_loop
                    lcoe_decrease = float(lcoe_ref - lcoe_new)
                    lcoe_per_decrease = float(lcoe_decrease/lcoe_ref)*100 
                    for i in range(len(D_rotor_vec)):
                        if type_vector[i] == 0:
                            number_V80 +=1
                        elif type_vector[i] == 1:
                            number_DTU += 1
                        else:
                            number_IEA +=1
                    cap_eval = number_V80*type_1_cap + number_DTU*type_2_cap + number_IEA*type_3_cap 
                    number_of_turb = len(type_vector)
                    print('New number of turbines is equal to : %f'%number_of_turb)
                    aep_new = aep_new_loop
                    aep_increase = float(aep_new - aep_ref)
                    aep_per_increase = float((aep_increase/aep_ref)*100)
                    irr_increase = float(irr_new - irr_ref)
                    # print('New capacity of design is %f MW'%cap_eval)
                    lay_change = lay_change + 1
                    print('Iteration number : ', iter_num)
                    print ('New AEP: %f GWh'%aep_new)
                    print('Increase in AEP = %f GWh (%f %%)' 
                          %(aep_increase,aep_per_increase))
                    print ('New IRR: %f '%irr_new)
                    print('Increase in IRR = %f %% ' 
                          %irr_increase)
                    print('New LCoE : %f EUR/kWh'%lcoe_new)
                    print('Decrease in LCoE = %f EUR/kWh (%f %%) '
                      %(lcoe_decrease,lcoe_per_decrease))
                    # print('Converged counter is at ', converged)
                    print()
                    add_flag_num = 0
                    aep_plot.append(aep_new)
                    iter_plot.append(iter_num)
                    irr_plot.append(irr_new)
                    lcoe_plot.append(lcoe_new)
                    number_of_turb_plot.append(number_of_turb)
                    aep_ref = aep_new
                    irr_ref = irr_new
                    lcoe_ref = lcoe_new
                elif lcoe_new_loop>=lcoe_ref:
                    iter_num += 1
                    aep_plot.append(aep_ref)
                    iter_plot.append(iter_num)
                    irr_plot.append(irr_ref)
                    lcoe_plot.append(lcoe_ref)
                    number_of_turb_plot.append(number_of_turb)
                if add_flag_num>100:
                    aep_new = aep_ref
                    irr_new = irr_ref
                    lcoe_new = lcoe_ref
                    add_flag_num = 0
                    one_iter = False
                    print('Maximum number of evaluations has been reached')
                    print('Moving to the next iteration')
                    print()
                    
                    
#################################################################################################################                    
                    
                    
        elif add_rem_choice == 2:
            print('Action chosen is No.5 : Removing turbine')
            while one_iter == True and number_of_turb>min_turb:
                random_turb_pick = np.random.randint(0,arr_size)
                # print(random_turb_pick)
                wt_x_loop = list(wt_x)
                wt_y_loop = list(wt_y)
                type_vector_loop = list(type_vector)
                # print(len(type_vector_loop))
                # print(len(wt_x_loop))
                rated_rpm_vec_loop= list(rated_rpm_vec)
                D_rotor_vec_loop = list(D_rotor_vec)
                rated_power_vec_loop = list(rated_power_vec)
                hub_height_vec_loop = list(hub_height_vec)
                
                water_depth_vec_loop = list(water_depth_vec)
                
                wt_x_loop = np.delete(wt_x_loop,random_turb_pick)
                wt_y_loop = np.delete(wt_y_loop,random_turb_pick)
                rated_rpm_vec_loop = np.delete(rated_rpm_vec_loop,random_turb_pick)
                D_rotor_vec_loop = np.delete(D_rotor_vec_loop,random_turb_pick)
                rated_power_vec_loop = np.delete(rated_power_vec_loop,random_turb_pick)
                hub_height_vec_loop= np.delete(hub_height_vec_loop,random_turb_pick)
                water_depth_vec_loop = np.delete(water_depth_vec_loop,random_turb_pick)
                type_vector_loop = np.delete(type_vector_loop,random_turb_pick)
                aep_new_loop = windFarmModel(wt_x_loop,wt_y_loop,h=hub_height_vec_loop,type=type_vector_loop).aep().sum()
                aep_irr = windFarmModel(wt_x_loop, wt_y_loop,h=hub_height_vec_loop,type = type_vector_loop).aep().sum(['wd','ws']).values*10**6
                
                irr_new_loop = eco_eval.calculate_irr(rated_rpm_vec_loop, D_rotor_vec_loop, 
                             rated_power_vec_loop, hub_height_vec_loop, 
                             water_depth_vec_loop, aep_irr)
                costs = eco_eval.project_costs_sums
                capex_loop = costs['CAPEX']
                devex_loop = costs['DEVEX']
                opex_loop = costs['OPEX']
                abex_loop = costs['ABEX']
                bop_loop = costs['BOP']
                om_loop = costs['O&M']
                total_costs_loop = capex_loop+devex_loop+(opex_loop*project_duration)+abex_loop+bop_loop+om_loop
                lcoe_new_loop = total_costs_loop/(aep_new_loop*project_duration*10**6)
                # print('works?')
                # add_flag_num += 1  
                rem_flag_num += 1
                if lcoe_new_loop < lcoe_ref: #and cap_eval<max_cap:
                    # print('works?')
                    wt_x = wt_x_loop
                    wt_y = wt_y_loop 
                    print('Initial number of turbines is equal to : %f'%len(type_vector))
                    number_DTU = 0
                    number_V80 = 0
                    number_IEA = 0  
                    one_iter = False
                    iter_num += 1
                    aep_new = aep_new_loop
                    irr_new = irr_new_loop    
                    lcoe_new = lcoe_new_loop
                    type_vector = type_vector_loop
                    D_rotor_vec = D_rotor_vec_loop
                    rated_power_vec = rated_power_vec_loop
                    rated_rpm_vec = rated_rpm_vec_loop
                    hub_height_vec = hub_height_vec_loop
                    water_depth_vec = water_depth_vec_loop
                    lcoe_decrease = float(lcoe_ref - lcoe_new)
                    lcoe_per_decrease = float(lcoe_decrease/lcoe_ref)*100 
                    for i in range(len(D_rotor_vec)):
                        if type_vector[i] == 0:
                            number_V80 +=1
                        elif type_vector[i] == 1:
                            number_DTU += 1
                        else:
                            number_IEA +=1
                    cap_eval = number_V80*type_1_cap + number_DTU*type_2_cap + number_IEA*type_3_cap    
                    number_of_turb = len(type_vector)
                    print('New number of turbines is equal to : %f'%number_of_turb)
                    
                    aep_new = aep_new_loop
                    aep_increase = float(aep_new - aep_ref)
                    aep_per_increase = float((aep_increase/aep_ref)*100)
                    irr_increase = float(irr_new - irr_ref)
                    # print('New capacity of design is %f MW'%cap_eval)
                    lay_change = lay_change + 1
                    print('Iteration number : ', iter_num)
                    print ('New AEP: %f GWh'%aep_new)
                    print('Increase in AEP = %f GWh (%f %%)' 
                          %(aep_increase,aep_per_increase))
                    print ('New IRR: %f '%irr_new)
                    print('Increase in IRR = %f %% ' 
                          %irr_increase)
                    print('New LCoE : %f EUR/kWh'%lcoe_new)
                    print('Decrease in LCoE = %f EUR/kWh (%f %%) '
                      %(lcoe_decrease,lcoe_per_decrease))
                    # print('Converged counter is at ', converged)
                    print()
                    rem_flag_num = 0
                    aep_plot.append(aep_new)
                    iter_plot.append(iter_num)
                    irr_plot.append(irr_new)
                    lcoe_plot.append(lcoe_new)
                    number_of_turb_plot.append(number_of_turb)
                    aep_ref = aep_new
                    irr_ref = irr_new
                    lcoe_ref = lcoe_new
                elif lcoe_new_loop>=lcoe_ref:
                    iter_num += 1
                    aep_plot.append(aep_ref)
                    iter_plot.append(iter_num)
                    irr_plot.append(irr_ref)
                    lcoe_plot.append(lcoe_ref)
                    number_of_turb_plot.append(number_of_turb)
                if rem_flag_num > 100:
                    aep_new = aep_ref
                    irr_new = irr_ref
                    lcoe_new = lcoe_ref
                    rem_flag_num = 0
                    one_iter = False
                    print('Maximum number of evaluations has been reached')
                    print('Moving on to the next iteration')
                    print()
        if number_of_turb>=max_turb:
            print('Maximum number of turbines has been reached')
            aep_new = aep_ref
            irr_new = irr_ref
            lcoe_new = lcoe_ref
            converged += 1
            iter_num+=1
            one_iter = False
   
        if number_of_turb<=min_turb:
             print('Minimum number of turbines has been reached')
             aep_new = aep_ref
             irr_new = irr_ref
             lcoe_new = lcoe_ref
             converged += 1
             iter_num+=1
             one_iter = False       
        add_rem_turb_para_final = cls(wt_x,wt_y,aep_plot, iter_plot,type_vector,
                                       iter_num,aep_new,converged,lay_change,
                                       D_rotor_vec,hub_height_vec,rated_power_vec,rated_rpm_vec,number_DTU,number_V80,
                                       number_IEA,irr_new,water_depth_vec,cap_eval,lcoe_new,
                                       lcoe_plot,number_of_turb_plot) 
        return add_rem_turb_para_final         