import numpy as np
from py_wake import BastankhahGaussian
from py_wake import FugaBlockage
from constraint_checker import Constraint_checker
from py_wake.superposition_models import LinearSum
from py_wake.wind_farm_models import All2AllIterative
from py_wake.deficit_models import NOJDeficit, SelfSimilarityDeficit
from topfarm.cost_models.economic_models.dtu_wind_cm_main import economic_evaluation as ee_2


class Change_Location(object):
    def __init__(self,wt_x,wt_y,aep_plot, iter_plot,type_vector,
                 iter_num,aep_new,converged,lay_change,
                 irr_new,irr_plot,lcoe_new,lcoe_plot):
        self.wt_x = wt_x
        self.wt_y = wt_y
        self.aep_plot = aep_plot
        self.iter_plot = iter_plot
        self.type_vector = type_vector
        self.iter_num = iter_num
        self.aep_new = aep_new
        self.irr_new = irr_new
        self.converged = converged
        self.lay_change = lay_change
        self.irr_plot = irr_plot
        self.lcoe_new = lcoe_new
        self.lcoe_plot = lcoe_plot
        
        
    @classmethod
    def change_loc(cls,wt_x,wt_y,max_step_size,bounds,min_dist,type_vector,
                   site,wt,choice,aep_ref_orig,iter_num,aep_plot,iter_plot,lay_change,
                   converged,tol,D_rotor_vec,hub_height_vec,rated_power_vec,rated_rpm_vec,
                   water_depth_vec,distance_from_shore,energy_price,project_duration,irr_plot,
                   irr_ref_orig,aep_ref,irr_ref,lcoe_ref,lcoe_plot):
        one_iter = True
        arr_size = len(wt_x)
        flag_num = 0
        lut_path = r"C:/Users/videe/AppData/Roaming/Python/Python38/site-packages/py_wake/tests/test_files/fuga/2MW/Z0=0.03000000Zi=00401Zeta0=0.00E+00"
        # windFarmModel = FugaBlockage(lut_path,site, wt)
        #windFarmModel = BastankhahGaussian(site, wt)
        windFarmModel = All2AllIterative(site,wt,
                                          wake_deficitModel=NOJDeficit(),
                                          superpositionModel=LinearSum(),
                                          blockage_deficitModel=SelfSimilarityDeficit())
        eco_eval = ee_2(distance_from_shore, energy_price, project_duration)

        print('Action chosen is No.',choice,':Changing location')
        loc_flag = 0
        while one_iter == True and loc_flag<=100:
            
            if iter_num == 0:
                aep_ref = aep_ref_orig
                irr_ref = irr_ref_orig
            
            wt_x_loop = list(wt_x)
            wt_y_loop = list(wt_y)
            
            check = False
            loc_flag+=1
        
            while check == False:
                
                random_turb_pick = np.random.randint(0,arr_size)
        
                x_resh = np.reshape(wt_x,(arr_size)).astype(int)
                y_resh = np.reshape(wt_y,(arr_size)).astype(int)
        
                x_rand_pick = x_resh[random_turb_pick]
                y_rand_pick = y_resh[random_turb_pick]
        
        
                move_size = np.random.random() * max_step_size
                move_theta = np.random.random() * np.pi * 2
                x_new =  x_rand_pick + move_size*np.sin(move_theta)
                y_new =  y_rand_pick + move_size*np.cos(move_theta)
                
                bounds_flag = Constraint_checker.checker(wt_x_loop,
                                                         wt_y_loop,
                                                          bounds, x_new,
                                                          y_new, 
                                                          random_turb_pick,
                                                          min_dist,type_vector)
                
                if bounds_flag.boundary_checker == False:
                    check = False
                    flag_num += 1
                else:
                    check = True
            wt_x_loop[random_turb_pick] = x_new
            wt_y_loop[random_turb_pick] = y_new
            aep_new_loop = windFarmModel(wt_x_loop,wt_y_loop,h=hub_height_vec,type=type_vector).aep().sum()
            aep_irr_new = windFarmModel(wt_x_loop, wt_y_loop,h=hub_height_vec,type=type_vector).aep().sum(['wd','ws']).values*10**6
            irr_new_loop = eco_eval.calculate_irr(rated_rpm_vec, D_rotor_vec, 
                             rated_power_vec, hub_height_vec, 
                             water_depth_vec, aep_irr_new)
            costs = eco_eval.project_costs_sums
            capex_loop = costs['CAPEX']
            devex_loop = costs['DEVEX']
            opex_loop = costs['OPEX']
            abex_loop = costs['ABEX']
            bop_loop = costs['BOP']
            om_loop = costs['O&M']
            total_costs_loop = capex_loop+devex_loop+(opex_loop*project_duration)+abex_loop+bop_loop+om_loop
            lcoe_new_loop = total_costs_loop/(aep_new_loop*project_duration*10**6)
            # print(irr_ref)
            # print(irr_new_loop)
            if lcoe_new_loop < lcoe_ref:
                one_iter = False
                iter_num += 1
                aep_new = aep_new_loop
                irr_new = irr_new_loop
                lcoe_new = lcoe_new_loop
                print('Iteration number : ', iter_num)
                lay_change = lay_change + 1
                aep_increase = float(aep_new - aep_ref)
                aep_per_increase = float((aep_increase/aep_ref)*100)
                irr_increase = float(irr_new - irr_ref)
                lcoe_decrease = float(lcoe_ref - lcoe_new)
                lcoe_per_decrease = float(lcoe_decrease/lcoe_ref)*100 
                
                wt_x = wt_x_loop
                wt_y = wt_y_loop  
                print ('New AEP: %f GWh'%aep_new)
                print('Increase in AEP = %f GWh (%f %%)' 
                      %(aep_increase,aep_per_increase))
                print ('New IRR: %f %%'%irr_new)
                print('Increase in IRR = %f %% ' 
                      %irr_increase)
                print('New LCoE : %f EUR/kWh'%lcoe_new)
                print('Decrease in LCoE = %f EUR/kWh (%f %%) '
                      %(lcoe_decrease,lcoe_per_decrease))
                print('Turbine changed : Number', random_turb_pick)
                print('Random step flagged:', flag_num,' times')
                print('Converged counter is at ', converged)
                print()
                irr_plot.append(irr_new)
                aep_plot.append(aep_new)
                lcoe_plot.append(lcoe_new)
                iter_plot.append(iter_num)
                irr_ref = irr_new
                flag_num = 0
                loc_flag = 0
            elif lcoe_new_loop>=lcoe_ref:
                iter_num += 1
                aep_plot.append(aep_ref)
                iter_plot.append(iter_num)
                irr_plot.append(irr_ref)
                lcoe_plot.append(lcoe_ref)
        if loc_flag>100:
            one_iter = False
            converged += 1
            iter_num+=1
            aep_new = aep_ref
            irr_new = irr_ref
            lcoe_new = lcoe_ref
            loc_flag = 0
            print('Maximum number of evaluations have been reached')
            print('Moving to the next iteration')
            print()
            # if aep_new > aep_ref:
            #     one_iter = False
            #     iter_num += 1
            #     print('Iteration number : ', iter_num)
            #     lay_change = lay_change + 1
            #     aep_increase = float(aep_new - aep_ref)
            #     aep_per_increase = float((aep_increase/aep_ref)*100)
            #     wt_x = wt_x_loop
            #     wt_y = wt_y_loop    
            #     print ('New AEP: %f GWh'%aep_new)
            #     print('Increase in AEP = %f GWh (%f %%)' 
            #           %(aep_increase,aep_per_increase))
            #     print('Turbine changed : Number', random_turb_pick)
            #     print('Random step flagged:', flag_num,' times')
            #     print('Converged counter is at ', converged)
            #     print()
            #     aep_plot.append(aep_new)
            #     iter_plot.append(iter_num)
            #     aep_ref = aep_new
            #     flag_num = 0
            #     if aep_per_increase<=tol:
            #         converged += 1
            # else:
            #     continue
        
        change_loc_para = cls(wt_x,wt_y,aep_plot, iter_plot,type_vector,
                              iter_num,aep_new,converged,lay_change,irr_new,irr_plot,
                              lcoe_new,lcoe_plot)
        return change_loc_para