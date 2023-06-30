from py_wake.examples.data.hornsrev1 import V80
from py_wake.examples.data.hornsrev1 import Hornsrev1Site
from py_wake.examples.data.hornsrev1 import wt_x, wt_y
from py_wake.examples.data.iea37 import IEA37Site, IEA37_WindTurbines
from py_wake.examples.data.dtu10mw import DTU10MW
from py_wake.wind_turbines._wind_turbines import WindTurbine, WindTurbines
from py_wake.site.shear import PowerShear
import numpy as np
import os
from py_wake import BastankhahGaussian
from py_wake import FugaBlockage
from py_wake.superposition_models import LinearSum
from py_wake.wind_farm_models import All2AllIterative
from py_wake.deficit_models import NOJDeficit, SelfSimilarityDeficit
from py_wake.examples.data import wtg_path

wtg_file = os.path.join(wtg_path, 'Vestas V164-8MW.wtg')
v164 = WindTurbine.from_WAsP_wtg(wtg_file)
class Site(object):
    
    def __init__(self,site_orig,wt_orig,windFarmModel_orig, wt_x_orig, 
                 wt_y_orig,site_number,min_dist,wt_list,min_capacity,
                 max_capacity,cap_t1,cap_t2,cap_t3):
        self.site_orig = site_orig
        self.wt_orig = wt_orig
        self.windFarmModel_orig = windFarmModel_orig
        self.wt_x_orig = wt_x_orig
        self.wt_y_orig = wt_y_orig
        self.site_number = site_number
        self.min_dist = min_dist
        self.wt_list = wt_list
        self.min_capacity = min_capacity
        self.max_capacity = max_capacity
        self.cap_t1 = cap_t1
        self.cap_t2 = cap_t2
        self.cap_t3 = cap_t3
        
    @classmethod
    def setup_site(cls,site_number):
        lut_path = r"C:/Users/videe/AppData/Roaming/Python/Python38/site-packages/py_wake/tests/test_files/fuga/2MW/Z0=0.03000000Zi=00401Zeta0=0.00E+00"

        if site_number == 1:
            print('Site chosen is HornsRev')
            wd_sectors = int(input('Please enter number of wind direction sectors:\n'))
            wd = np.linspace(0,360,wd_sectors+1)
            site_orig = Hornsrev1Site(shear=PowerShear(h_ref=80, alpha=.1))
            site_orig.default_wd = wd
            wt_orig = V80()
            wt_orig = V80()
            wt_2 = DTU10MW()
            # wt_3 = IEA37_WindTurbines()
            wt_3 = WindTurbine.from_WAsP_wtg(wtg_file)
            wt_list = WindTurbines.from_WindTurbine_lst([wt_orig,wt_2,wt_3])
            print('Turbines picked are - ',wt_list._names[0],
                  ',',wt_list._names[1],'and',wt_list._names[2])
            min_dist = [wt_orig._diameters[0]*5,wt_2._diameters[0]*5,wt_3._diameters[0]*5]
            print('Minimum distance between two turbines is :',min_dist,'m\n')
            cap_t1 = 2 #MAGIC NUMEBRS CHANGE
            cap_t2 = 10 #MAGIC NUMBERS CHANGE
            cap_t3 = 8
            min_capacity = 2*80
            print('Minimum capacity is %f MW'%min_capacity)
            max_capacity = 250#MAGIC NUMBERS
            print('Maximum capacity is %f MW'%max_capacity)
            
            # windFarmModel_orig = BastankhahGaussian(site_orig, wt_orig)
            # windFarmModel_orig = FugaBlockage(lut_path,site_orig, wt_orig)
            windFarmModel_orig = All2AllIterative(site_orig,wt_orig,
                                          wake_deficitModel=NOJDeficit(),
                                          superpositionModel=LinearSum(),
                                          blockage_deficitModel=SelfSimilarityDeficit())
            
            wt_x_orig = wt_x
            wt_y_orig = wt_y
            min_dist = [wt_orig._diameters[0]*5,wt_2._diameters[0]*5,wt_3._diameters[0]*5]
            print('Minimum distance between two turbines is :',min_dist,'m\n')
        
        if site_number == 2:
            print('Site chosen is IEA Test site')
            number_of_wt = int(input('Please enter number of turbines to be used:\n'))
            wd_sectors = int(input('Please enter number of wind direction sectors:\n'))
            wd = np.linspace(0,360,wd_sectors+1)
            site_orig = IEA37Site(number_of_wt,shear=PowerShear(h_ref=80, alpha=.1))
            site_orig.default_wd = wd
            wt_orig = V80()
            wt_2 = DTU10MW()
            # wt_3 = IEA37_WindTurbines()
            wt_3 = WindTurbine.from_WAsP_wtg(wtg_file)
            wt_list = WindTurbines.from_WindTurbine_lst([wt_orig,wt_2,wt_3])

            print('Turbines picked are - ',wt_list._names[0],
                  ',',wt_list._names[1],'and',wt_list._names[2])
            min_dist = [wt_orig._diameters[0]*5,wt_2._diameters[0]*5,wt_3._diameters[0]*5]
            print('Minimum distance between two turbines is :',min_dist,'m\n')
            cap_t1 = 2 #MAGIC NUMEBRS CHANGE
            cap_t2 = 10 #MAGIC NUMBERS CHANGE
            cap_t3 = 8
            min_capacity = 35
            print('Minimum capacity is %f MW'%min_capacity)
            max_capacity = 70#MAGIC NUMBERS
            print('Maximum capacity is %f MW'%max_capacity)
            # windFarmModel_orig = BastankhahGaussian(site_orig, wt_orig)
            # windFarmModel_orig = FugaBlockage(lut_path,site_orig, wt_orig)
            windFarmModel_orig = All2AllIterative(site_orig,wt_orig,
                                          wake_deficitModel=NOJDeficit(),
                                          superpositionModel=LinearSum(),
                                          blockage_deficitModel=SelfSimilarityDeficit())
            wt_x_orig, wt_y_orig = site_orig.initial_position.T
        
        site_orig_val = cls(site_orig, wt_orig, windFarmModel_orig, wt_x_orig, 
                            wt_y_orig, site_number,min_dist,wt_list,min_capacity,
                            max_capacity,cap_t1,cap_t2,cap_t3)
    
        return site_orig_val
       
    def get_site(self):
        return self.site_orig
    
    def get_wt(self):
        return self.wt_orig
    