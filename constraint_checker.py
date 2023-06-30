import math
class Constraint_checker(object):
    
    
    def __init__(self, boundary_checker):
        self.boundary_checker = boundary_checker
        
    @classmethod
    def checker(cls,wt_x_loop,wt_y_loop,bounds, x_new,y_new,random_turb_pick,min_dist,type_vector):
        boundary_checker = True
        min_dist_eval = min_dist[1]
        # if type_vector[random_turb_pick] == 0:
        #     min_dist_eval = min_dist[0]
        # else:
        #     min_dist_eval = min_dist[1]
        for i in range(len(wt_x_loop)):
            turb_to_check = (wt_x_loop[i],wt_y_loop[i])
            turb_new_pos = (x_new,y_new)
            wt_dist = math.dist(turb_new_pos,turb_to_check)
            
            if wt_dist<=min_dist_eval:
                boundary_checker = False
                
        if x_new > bounds[1] or x_new < bounds[0]:
            boundary_checker = False
        
        elif y_new > bounds[2] or y_new < bounds[3]:
            boundary_checker = False
            
        else:
            boundary_checker = True
            
        boundary_checker_final = cls(boundary_checker)
        return boundary_checker_final     
    
    
