
import numpy as np
from py_wake import BastankhahGaussian
from py_wake import FugaBlockage
# from constraint_checker import Constraint_checker
from topfarm.cost_models.economic_models.dtu_wind_cm_main import economic_evaluation as ee_2
from py_wake.superposition_models import LinearSum
from py_wake.wind_farm_models import All2AllIterative
from py_wake.deficit_models import NOJDeficit, SelfSimilarityDeficit

class Change_Type(object):
    def __init__(self,wt_x,wt_y,aep_plot, iter_plot,type_vector,
             iter_num,aep_new,converged,lay_change,other_turb,cap_eval,max_choice_val,
             D_rotor_vec,hub_height_vec,rated_power_vec,rated_rpm_vec,number_DTU,number_V80,
             number_IEA,irr_new,lcoe_new,lcoe_plot):
        self.wt_x = wt_x
        self.wt_y = wt_y
        self.aep_plot = aep_plot
        self.iter_plot = iter_plot
        self.type_vector = type_vector
        self.iter_num = iter_num
        self.aep_new = aep_new
        self.converged = converged
        self.lay_change = lay_change
        self.other_turb = other_turb
        self.cap_eval = cap_eval
        self.max_choice_val = max_choice_val
        self.D_rotor_vec = D_rotor_vec
        self.hub_height_vec = hub_height_vec
        self.rated_power_vec = rated_power_vec
        self.rated_rpm_vec = rated_rpm_vec
        self.number_DTU = number_DTU
        self.number_V80 = number_V80
        self.number_IEA = number_IEA
        self.irr_new = irr_new
        self.lcoe_new = lcoe_new
        self.lcoe_plot = lcoe_plot
        
    @classmethod    
    def change_type(cls,choice,cap_eval,max_cap,arr_size,type_vector,other_turb,
                    iter_num,type_1_cap,type_2_cap,type_3_cap,wt_x,wt_y,site,wt,lay_change,
                    aep_ref,converged,aep_plot,iter_plot,tol,max_choice_val,
                    D_rotor_vec,hub_height_vec,rated_power_vec,rated_rpm_vec,
                   water_depth_vec,distance_from_shore,energy_price,project_duration,
                   irr_plot,irr_ref,D_rotor,hub_heights,rated_power,rated_rpm,
                   number_DTU,number_V80,number_IEA,lcoe_ref,lcoe_plot):
        lut_path = r"C:/Users/videe/AppData/Roaming/Python/Python38/site-packages/py_wake/tests/test_files/fuga/2MW/Z0=0.03000000Zi=00401Zeta0=0.00E+00"
        # windFarmModel = BastankhahGaussian(site, wt)
        # windFarmModel = FugaBlockage(lut_path,site, wt)
        windFarmModel = All2AllIterative(site,wt,
                                          wake_deficitModel=NOJDeficit(),
                                          superpositionModel=LinearSum(),
                                          blockage_deficitModel=SelfSimilarityDeficit())
        one_iter = True
        print('Action chosen is No.',choice,'Changing type of turbine')
        # print('Current capacity of design is %f MW'%cap_eval)
        # print('Maximum possible capacity is : %f'%max_cap)
        type_flag = 0
        eco_eval = ee_2(distance_from_shore, energy_price, project_duration)
        # print(irr_ref)

        arr_size = len(wt_x)
        while one_iter == True and type_flag<=100:
            
            type_vector_loop = list(type_vector)
            rated_rpm_vec_loop= list(rated_rpm_vec)
            D_rotor_vec_loop = list(D_rotor_vec)
            rated_power_vec_loop = list(rated_power_vec)
            hub_height_vec_loop = list(hub_height_vec)
            
            random_turb_pick = np.random.randint(0,arr_size)
            random_change_pick = np.random.randint(0,3)
            
            type_vector_loop[random_turb_pick] = random_change_pick
            rated_rpm_vec_loop[random_turb_pick] = rated_rpm[random_change_pick]
            D_rotor_vec_loop[random_turb_pick] = D_rotor[random_change_pick]
            rated_power_vec_loop[random_turb_pick] = rated_power[random_change_pick]
            hub_height_vec_loop[random_turb_pick] = hub_heights[random_change_pick]
            aep_new_loop = windFarmModel(wt_x,wt_y,h=hub_height_vec_loop,type=type_vector_loop).aep().sum()
            aep_irr = windFarmModel(wt_x, wt_y,h=hub_height_vec_loop,type = type_vector_loop).aep().sum(['wd','ws']).values*10**6
            
            irr_new_loop = eco_eval.calculate_irr(rated_rpm_vec_loop, D_rotor_vec_loop, 
                             rated_power_vec_loop, hub_height_vec_loop, 
                             water_depth_vec, aep_irr)
            costs = eco_eval.project_costs_sums
            # expenditures = eco_eval.calculate_expenditures(rated_rpm_vec_loop, D_rotor_vec_loop, 
            #                    rated_power_vec_loop, hub_height_vec_loop, 
            #                   water_depth_vec, aep_irr)
            # print(costs)
            # print(expenditures)
            capex_loop = costs['CAPEX']
            devex_loop = costs['DEVEX']
            opex_loop = costs['OPEX']
            # print(opex_loop)
            abex_loop = costs['ABEX']
            bop_loop = costs['BOP']
            om_loop = costs['O&M']
            total_costs_loop = capex_loop+devex_loop+(opex_loop*project_duration)+abex_loop+bop_loop+om_loop
            # print(total_costs_loop)
            lcoe_new_loop = total_costs_loop/(aep_new_loop*project_duration*10**6)
            type_flag += 1
            
            if lcoe_new_loop<lcoe_ref and cap_eval<=max_cap:
                number_DTU = 0
                number_V80 = 0
                number_IEA = 0  
                irr_new = irr_new_loop
                lcoe_new = lcoe_new_loop
                one_iter = False
                type_vector = type_vector_loop
                D_rotor_vec = D_rotor_vec_loop
                rated_power_vec = rated_power_vec_loop
                rated_rpm_vec = rated_rpm_vec_loop
                hub_height_vec = hub_height_vec_loop
                for i in range(len(D_rotor_vec)):
                    if type_vector[i] == 0:
                        number_V80 +=1
                    elif type_vector[i] == 1:
                        number_DTU += 1
                    else:
                        number_IEA +=1
                
                cap_eval = number_V80*type_1_cap + number_DTU*type_2_cap + number_IEA*type_3_cap
                lcoe_decrease = float(lcoe_ref - lcoe_new)
                lcoe_per_decrease = float(lcoe_decrease/lcoe_ref)*100 
                iter_num += 1
                aep_new = aep_new_loop
                aep_increase = float(aep_new - aep_ref)
                aep_per_increase = float((aep_increase/aep_ref)*100)
                irr_increase = float(irr_new - irr_ref)
                print('Turbine changed : Number', random_turb_pick)
                print('New capacity of design is %f MW'%cap_eval)
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
                
                aep_plot.append(aep_new)
                iter_plot.append(iter_num)
                irr_plot.append(irr_new)
                lcoe_plot.append(lcoe_new)
                aep_ref = aep_new
                irr_ref = irr_new
                lcoe_ref = lcoe_new
                type_flag = 0
                # if aep_per_increase<=tol:
                #     converged += 1
            elif lcoe_new_loop>=lcoe_ref:
                iter_num += 1
                aep_plot.append(aep_ref)
                iter_plot.append(iter_num)
                irr_plot.append(irr_ref)
                lcoe_plot.append(lcoe_ref)
            if cap_eval >= max_cap:
                # converged += 1
                iter_num+=1
                # print()
                aep_new = aep_ref
                irr_new = irr_ref
                lcoe_new = lcoe_ref
                type_flag = 0
                one_iter = False
                print('Maximum possible capacity has been reached')
                print('Turbines will no longer be changed')
                # max_choice_val = 2
                print()

        if type_flag>100:
            one_iter = False
            converged += 1
            iter_num+=1
            print('Maximum number of evaluations have been reached')
            print('Moving to the next iteration')
            print()
            aep_new = aep_ref
            irr_new = irr_ref
            lcoe_new = lcoe_ref
            type_flag = 0
        # aep_ref = aep_new
        # irr_ref = irr_new
            # if type_vector[random_turb_pick] == 0 and cap_eval <= max_cap:
            #     type_vector[random_turb_pick] = 1
            #     one_iter = False
            #     other_turb += 1
            #     iter_num += 1
            #     cap_eval = type_1_cap*(arr_size - other_turb) + type_2_cap*other_turb    
            #     print('Turbine changed : Number', random_turb_pick) 
            #     print('New capacity of design is %f MW'%cap_eval)
            #     aep_new = windFarmModel(wt_x,wt_y,type=type_vector).aep().sum()
            #     print('Iteration number : ', iter_num)
            #     lay_change = lay_change + 1
            #     aep_increase = float(aep_new - aep_ref)
            #     aep_per_increase = float((aep_increase/aep_ref)*100)
            #     print ('New AEP: %f GWh'%aep_new)
            #     print('Increase in AEP = %f GWh (%f %%)' 
            #           %(aep_increase,aep_per_increase))
            #     print('Converged counter is at ', converged)
            #     print()
            #     aep_plot.append(aep_new)
            #     iter_plot.append(iter_num)
            #     aep_ref = aep_new
            #     if aep_per_increase<=tol:
            #         converged += 1
            # if cap_eval >= max_cap:
            #     one_iter = False
            #     print('Maximum possible capacity has been reached')
            #     print('Turbines will no longer be changed')
            #     max_choice_val = 2
            #     print()
        change_type_para = cls(wt_x,wt_y,aep_plot, iter_plot,type_vector,
                              iter_num,aep_new,converged,lay_change,other_turb,
                              cap_eval,max_choice_val,D_rotor_vec,hub_height_vec,
                              rated_power_vec,rated_rpm_vec,number_DTU,number_V80,
                              number_IEA,irr_new,lcoe_new,lcoe_plot)
        return change_type_para