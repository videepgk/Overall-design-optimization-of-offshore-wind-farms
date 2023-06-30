import numpy as np
from py_wake import BastankhahGaussian
from py_wake import FugaBlockage
from py_wake.superposition_models import LinearSum
from py_wake.wind_farm_models import All2AllIterative
from py_wake.deficit_models import NOJDeficit, SelfSimilarityDeficit
# from constraint_checker import Constraint_checker
from topfarm.cost_models.economic_models.dtu_wind_cm_main import economic_evaluation as ee_2

class Change_hubheight(object):
    def __init__(self,wt_x,wt_y,aep_plot, iter_plot,type_vector,
             iter_num,aep_new,converged,irr_new,irr_plot,hub_height_vec,
             lcoe_new,lcoe_plot):
        self.aep_plot = aep_plot
        self.iter_plot = iter_plot
        self.iter_num = iter_num
        self.aep_new = aep_new
        self.irr_new = irr_new
        self.converged = converged
        self.irr_plot = irr_plot
        self.hub_height_vec = hub_height_vec
        self.lcoe_new = lcoe_new
        self.lcoe_plot = lcoe_plot
        
    @classmethod    
    def change_hubheight(cls,site,wt,arr_size,choice,hub_heights,distance_from_shore, 
                         energy_price,project_duration,hub_height_vec,wt_x,wt_y,
                         type_vector,D_rotor_vec,rated_power_vec,rated_rpm_vec,
                         water_depth_vec,irr_ref,iter_num,aep_ref,converged,tol,
                         aep_plot,iter_plot,irr_plot,lcoe_ref,lcoe_plot):
        lut_path = r"C:/Users/videe/AppData/Roaming/Python/Python38/site-packages/py_wake/tests/test_files/fuga/2MW/Z0=0.03000000Zi=00401Zeta0=0.00E+00"
        # windFarmModel = FugaBlockage(lut_path,site, wt)
        # windFarmModel = BastankhahGaussian(site, wt)
        windFarmModel = All2AllIterative(site,wt,
                                          wake_deficitModel=NOJDeficit(),
                                          superpositionModel=LinearSum(),
                                          blockage_deficitModel=SelfSimilarityDeficit())
        one_iter = True
        print('Action chosen is No.',choice,'Changing hubheight of random turbine')
        hh_flag = 0
        eco_eval = ee_2(distance_from_shore, energy_price, project_duration)
        arr_size = len(wt_x)
        #MAGIC NUMBERS CHANGE
        while one_iter == True and hh_flag<=100:
            # print(aep_ref)
            # hub_height_eval = np.linspace(min(hub_heights)*0.5,165,27)
            random_turb_pick = np.random.randint(0,arr_size)
            if type_vector[random_turb_pick] == 0:
                hub_height_eval = np.linspace(60,90,7)
            elif type_vector[random_turb_pick] == 1:
                hub_height_eval = np.linspace(110,140,7)
            elif type_vector[random_turb_pick] == 2:
                hub_height_eval = np.linspace(100,130,7)
            
            # print(hub_height_eval)
            random_hh_pick = np.random.randint(0,len(hub_height_eval))
            hub_height_pick = hub_height_eval[random_hh_pick]
            hub_height_vec_loop = list(hub_height_vec)
            hub_height_vec_loop[random_turb_pick] = hub_height_pick
            aep_new_loop = windFarmModel(wt_x,wt_y,h=hub_height_vec_loop,type=type_vector).aep().sum()
            aep_irr = windFarmModel(wt_x, wt_y,h=hub_height_vec_loop,type = type_vector).aep().sum(['wd','ws']).values*10**6
            irr_new_loop = eco_eval.calculate_irr(rated_rpm_vec, D_rotor_vec, 
                             rated_power_vec, hub_height_vec_loop, 
                             water_depth_vec, aep_irr)
            costs = eco_eval.project_costs_sums
            capex_loop = costs['CAPEX']
            devex_loop = costs['DEVEX']
            opex_loop = costs['OPEX']
            abex_loop = costs['ABEX']
            bop_loop = costs['BOP']
            om_loop = costs['O&M']
            total_costs_loop = capex_loop+devex_loop+(opex_loop*project_duration)+abex_loop+bop_loop+om_loop
            lcoe_new_loop = total_costs_loop/(aep_new_loop*project_duration*10**6)
            hh_flag+=1
            if lcoe_new_loop<lcoe_ref:
                one_iter = False
                aep_new = aep_new_loop
                irr_new = irr_new_loop
                lcoe_new = lcoe_new_loop
                aep_increase = float(aep_new - aep_ref)
                aep_per_increase = float((aep_increase/aep_ref)*100)
                irr_increase = float(irr_new - irr_ref)
                lcoe_decrease = float(lcoe_ref - lcoe_new)
                lcoe_per_decrease = float(lcoe_decrease/lcoe_ref)*100 
                print('Turbine changed : Number', random_turb_pick)
                print('Iteration number : ', iter_num)
                print('Old hub height was:%f m' %hub_height_vec[random_turb_pick])
                iter_num += 1
                hub_height_vec = hub_height_vec_loop
                print('New hub height is : %f m'%hub_height_vec[random_turb_pick])
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
                hh_flag = 0
                # if aep_per_increase<=tol:
                #     converged += 1
            elif lcoe_new_loop>=lcoe_ref:
                iter_num += 1
                aep_plot.append(aep_ref)
                iter_plot.append(iter_num)
                irr_plot.append(irr_ref)
                lcoe_plot.append(lcoe_ref)
                
            if hh_flag>100:
                one_iter = False
                converged += 1
                iter_num+=1
                print('Maximum number of evaluations have been reached')
                print('Moving to the next iteration')
                print()
                aep_new = aep_ref
                irr_new = irr_ref
                lcoe_new = lcoe_ref
                hh_flag = 0
        change_hh_para = cls(wt_x,wt_y,aep_plot, iter_plot,type_vector,
             iter_num,aep_new,converged,irr_new,irr_plot,hub_height_vec,lcoe_new,
             lcoe_plot)
        return change_hh_para