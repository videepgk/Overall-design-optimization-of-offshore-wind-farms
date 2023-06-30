import math
class Constraint_checker_add_rem(object):
    
    
    def __init__(self,add_rem_check_flag):
        self.add_rem_check_flag = add_rem_check_flag
        
    @classmethod
    def add_rem_checker(cls,wt_x_loop,wt_y_loop,bounds, x_new,y_new, 
                        min_dist,type_vector):
        add_rem_check_flag = True
        min_dist_eval = min_dist[1]
        for i in range(len(wt_x_loop)):
            turb_to_check = (wt_x_loop[i],wt_y_loop[i])
            turb_new_pos = (x_new,y_new)
            wt_dist = math.dist(turb_new_pos,turb_to_check)
            if wt_dist<=min_dist_eval:
                add_rem_check_flag = False
                
        if x_new > bounds[1] or x_new < bounds[0]:
            add_rem_check_flag = False
        
        elif y_new > bounds[2] or y_new < bounds[3]:
            add_rem_check_flag = False
            
        else:
            add_rem_check_flag = True
        add_rem_check_final = cls(add_rem_check_flag)
        return add_rem_check_final
