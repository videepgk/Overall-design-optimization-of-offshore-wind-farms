import numpy as np
from py_wake import BastankhahGaussian
from py_wake import FugaBlockage
from change_loc import Change_Location
from change_type import Change_Type
from change_hh import Change_hubheight
from add_rem_turb import Change_number
# from topfarm.cost_models.py_wake_wrapper import PyWakeAEPCostModelComponent
from topfarm.cost_models.economic_models.dtu_wind_cm_main import economic_evaluation as ee_2
from py_wake.superposition_models import LinearSum
from py_wake.wind_farm_models import All2AllIterative
from py_wake.deficit_models import NOJDeficit, SelfSimilarityDeficit

class Optimization(object):
    
    def __init__(self, aep_ref_orig,aep_total_increase,
                 aep_total_increase_per,wt_x,wt_y,aep_plot, iter_plot,type_vector,
                 aep_irr_ref,irr_plot,lcoe_plot,number_of_turb_plot):
        self.aep_ref_orig = aep_ref_orig
        self.total_increase = aep_total_increase
        self.total_increase_per = aep_total_increase_per
        self.wt_x_optimized = wt_x
        self.wt_y_optimized = wt_y
        self.aep_plot = aep_plot
        self.iter_plot = iter_plot
        self.type_vector = type_vector
        self.aep_irr_ref = aep_irr_ref
        self.irr_plot = irr_plot
        self.lcoe_plot = lcoe_plot
        self.number_of_turb_plot = number_of_turb_plot
        
    @classmethod
    def optimize(cls,max_step_size,max_iter,wt_x,wt_y, 
                 site, wt, bounds,min_dist,site_eval,min_cap,max_cap,
                 type_1_cap,type_2_cap,type_3_cap,D_rotor,hub_heights,
                 rated_power,rated_rpm,water_depth):
        lut_path = r"C:/Users/videe/AppData/Roaming/Python/Python38/site-packages/py_wake/tests/test_files/fuga/2MW/Z0=0.03000000Zi=00401Zeta0=0.00E+00"
        
        # windFarmModel = BastankhahGaussian(site, wt)
        # windFarmModel = FugaBlockage(lut_path,site, wt)
        windFarmModel = All2AllIterative(site,wt,
                                          wake_deficitModel=NOJDeficit(),
                                          superpositionModel=LinearSum(),
                                          blockage_deficitModel=SelfSimilarityDeficit())
        arr_size = len(wt_x)
        D_rotor_vec = [D_rotor[0]] * arr_size
        hub_height_vec = [hub_heights[0]] * arr_size
        rated_power_vec = [rated_power[0]] * arr_size
        rated_rpm_vec = [rated_rpm[0]] * arr_size
        water_depth_vec = list([water_depth[0]] * arr_size)
        # print(water_depth_vec)
        distance_from_shore = 30         # [km]
        energy_price = 0.1               # [Euro/kWh] What we get per kWh
        project_duration = 20 
        type_vector = np.zeros(arr_size)
        aep_ref_orig = windFarmModel(wt_x,wt_y,type=type_vector).aep().sum()
        aep_irr_ref_orig = windFarmModel(wt_x, wt_y,type = type_vector).aep().sum(['wd','ws']).values*10**6
        eco_eval = ee_2(distance_from_shore, energy_price, project_duration)
        irr_ref_orig = eco_eval.calculate_irr(rated_rpm_vec, D_rotor_vec, 
                             rated_power_vec, hub_height_vec, 
                             water_depth_vec, aep_irr_ref_orig)
        costs_ref_orig = eco_eval.project_costs_sums
        capex_ref_orig = costs_ref_orig['CAPEX']
        devex_ref_orig = costs_ref_orig['DEVEX']
        opex_ref_orig = costs_ref_orig['OPEX']
        abex_ref_orig = costs_ref_orig['ABEX']
        bop_ref_orig = costs_ref_orig['BOP']
        om_ref_orig = costs_ref_orig['O&M']
        total_costs_loop = capex_ref_orig+devex_ref_orig+(opex_ref_orig*project_duration)+abex_ref_orig+bop_ref_orig+om_ref_orig
        lcoe_ref_orig = total_costs_loop/(aep_ref_orig*project_duration*10**6)
        aep_ref = aep_ref_orig
        aep_irr_ref = aep_irr_ref_orig
        irr_ref = irr_ref_orig
        lcoe_ref = lcoe_ref_orig
        lay_change = 0
        iter_num = 0
        tol = 1e-4
        converged = 0
        irr_plot = [irr_ref_orig]
        aep_plot = [aep_ref_orig]
        lcoe_plot = [lcoe_ref_orig]
        iter_plot = [iter_num]
        number_of_turb_plot = [len(type_vector)]
        other_turb = 0
        cap_eval = type_1_cap*(arr_size - other_turb) + type_2_cap*other_turb
        cap_ref = float(cap_eval)
        max_choice_val = 5
        number_DTU = 0
        number_V80 = 0
        number_IEA = 0

        while iter_num in range(max_iter) and converged <=1000:
            choice = np.random.randint(1,max_choice_val)
            if iter_num == 0:
                choice = 1
                
            
            if choice == 1: #CHANGE POSITION
                change_loc = Change_Location.change_loc(wt_x, wt_y, max_step_size, 
                                                        bounds, min_dist, type_vector, 
                                                        site, wt, choice, aep_ref_orig, 
                                                        iter_num, aep_plot, iter_plot, 
                                                        lay_change, converged, tol,
                                                        D_rotor_vec,hub_height_vec,
                                                        rated_power_vec,rated_rpm_vec,
                                                        water_depth_vec,distance_from_shore,
                                                        energy_price,project_duration,irr_plot,
                                                        irr_ref_orig,aep_ref,irr_ref,lcoe_ref,
                                                        lcoe_plot)
                iter_num = change_loc.iter_num
                aep_new = change_loc.aep_new
                converged = change_loc.converged
                lay_change = change_loc.lay_change
                wt_x = change_loc.wt_x
                wt_y = change_loc.wt_y
                type_vector = change_loc.type_vector
                aep_ref = aep_new
                irr_new = change_loc.irr_new
                irr_ref = irr_new
                lcoe_new = change_loc.lcoe_new
                lcoe_ref = lcoe_new
                
            elif choice == 2: #CHANGE TYPE
                type_change = Change_Type.change_type(choice, cap_eval, max_cap, 
                                                      arr_size, type_vector, 
                                                      other_turb, iter_num, 
                                                      type_1_cap, type_2_cap,type_3_cap, 
                                                      wt_x, wt_y, site, wt, 
                                                      lay_change, aep_ref, 
                                                      converged, aep_plot, 
                                                      iter_plot, tol,max_choice_val,
                                                      D_rotor_vec,hub_height_vec,
                                                      rated_power_vec,rated_rpm_vec,
                                                      water_depth_vec,distance_from_shore
                                                      ,energy_price,project_duration,
                                                      irr_plot,irr_ref,D_rotor,
                                                      hub_heights,rated_power,rated_rpm,number_DTU,
                                                      number_V80,number_IEA,lcoe_ref,lcoe_plot)
                iter_num = type_change.iter_num
                aep_new = type_change.aep_new
                converged = type_change.converged
                lay_change = type_change.lay_change
                wt_x = type_change.wt_x
                wt_y = type_change.wt_y
                type_vector = type_change.type_vector
                D_rotor_vec = type_change.D_rotor_vec
                hub_height_vec = type_change.hub_height_vec
                rated_rpm_vec = type_change.rated_rpm_vec
                rated_power_vec = type_change.rated_power_vec
                aep_ref = aep_new
                irr_new = type_change.irr_new
                irr_ref = irr_new
                cap_eval = type_change.cap_eval
                other_turb = type_change.other_turb
                max_choice_val = type_change.max_choice_val
                number_DTU = type_change.number_DTU
                number_V80 = type_change.number_V80
                number_IEA = type_change.number_IEA
                lcoe_new = type_change.lcoe_new
                lcoe_ref = lcoe_new
            
            elif choice == 3: #CHANGE HUB HEIGHT
                hh_change = Change_hubheight.change_hubheight(site, wt, arr_size, 
                                                              choice, hub_heights, 
                                                              distance_from_shore, 
                                                              energy_price, project_duration, 
                                                              hub_height_vec, 
                                                              wt_x, wt_y, type_vector, 
                                                              D_rotor_vec, 
                                                              rated_power_vec, 
                                                              rated_rpm_vec, 
                                                              water_depth_vec, 
                                                              irr_ref, iter_num, 
                                                              aep_ref, converged, tol, 
                                                              aep_plot, iter_plot, irr_plot,
                                                              lcoe_ref,lcoe_plot)
                
                
                iter_num = hh_change.iter_num
                aep_new = hh_change.aep_new
                converged = hh_change.converged
                hub_height_vec = hh_change.hub_height_vec
                aep_ref = aep_new
                irr_new = hh_change.irr_new
                irr_ref = irr_new
                lcoe_new = hh_change.lcoe_new
                lcoe_ref = lcoe_new
            
            elif choice == 4: #CHANGE NUMBER OF TURBINES
                number_change = Change_number.change_number_turb(distance_from_shore, 
                                                                 energy_price, 
                                                                 project_duration, 
                                                                 wt_x, wt_y, bounds, 
                                                                  min_dist, type_vector, 
                                                                  aep_ref, irr_ref, 
                                                                  site, wt, 
                                                                  hub_height_vec, 
                                                                  rated_rpm_vec,
                                                                  D_rotor_vec, 
                                                                  rated_power_vec, 
                                                                  water_depth_vec, 
                                                                  D_rotor, hub_heights, 
                                                                  rated_power, rated_rpm, 
                                                                  water_depth, iter_num, 
                                                                  aep_plot, irr_plot, 
                                                                  iter_plot, converged, 
                                                                  lay_change,max_step_size,
                                                                  number_DTU,number_V80,number_IEA,
                                                                  type_1_cap,type_2_cap,
                                                                  type_3_cap,cap_eval,max_cap,
                                                                  lcoe_ref,lcoe_plot,number_of_turb_plot)
                
                iter_num = number_change.iter_num
                aep_new = number_change.aep_new
                converged = number_change.converged
                lay_change = number_change.lay_change
                wt_x = number_change.wt_x
                wt_y = number_change.wt_y
                type_vector = number_change.type_vector
                D_rotor_vec = number_change.D_rotor_vec
                hub_height_vec = number_change.hub_height_vec
                rated_rpm_vec = number_change.rated_rpm_vec
                rated_power_vec = number_change.rated_power_vec
                # print(water_depth_vec)
                water_depth_vec = number_change.water_depth_vec
                # print(water_depth_vec)
                aep_ref = aep_new
                irr_new = number_change.irr_new
                irr_ref = irr_new
                lcoe_new = number_change.lcoe_new
                lcoe_ref = lcoe_new
                # cap_eval = type_change.cap_eval
                # other_turb = type_change.other_turb
                # max_choice_val = type_change.max_choice_val
                number_DTU = number_change.number_DTU
                number_V80 = number_change.number_V80
                number_IEA = number_change.number_IEA
                cap_eval = number_change.cap_eval
                
        irr_total_increase = irr_new - irr_ref_orig              
        aep_total_increase = aep_new - aep_ref_orig
        aep_total_increase_per = (aep_total_increase/aep_ref_orig)*100
        lcoe_total_decrease = lcoe_new - lcoe_ref_orig
        lcoe_total_decrease_per = (lcoe_total_decrease/lcoe_ref_orig)*100
        print('Original AEP: %f GWh' %aep_ref_orig )
        print('Optimized AEP: %f GWh'%aep_new)
        print('Final increase in AEP = %f GWh (%f %%)' 
              %(aep_total_increase,aep_total_increase_per))
        print('Original capacity : %f MW'%cap_ref)
        print('Final capacity : %f MW'%cap_eval)
        print('Original IRR: %f %%' %irr_ref_orig)
        print('Optimized IRR :%f %%' %irr_new)
        print('Final increase in IRR:%f %%' %irr_total_increase)
        print('Original LCoE : %f EUR/kWh' %lcoe_ref_orig)
        print('Optimized LCoE : %f EUR/KWh' %lcoe_new)
        print('Final decrease in LCoE : %f EUR/kWh (%f %%)' 
              %(lcoe_total_decrease,lcoe_total_decrease_per))
        print('Layout changed',lay_change,'times')
        print('Number of',site_eval.wt_list._names[0],'turbines =',number_V80)
        print('Number of',site_eval.wt_list._names[1],'turbines =',number_DTU)
        print('Number of',site_eval.wt_list._names[2],'turbines =',number_IEA)
        print('Final hub height vector is :',hub_height_vec)
        
        opt_para_final = cls(aep_ref_orig,aep_total_increase,
                             aep_total_increase_per,wt_x,wt_y,
                             aep_plot, iter_plot,type_vector,
                             aep_irr_ref,irr_plot,lcoe_plot,number_of_turb_plot)
        return opt_para_final
    
    
