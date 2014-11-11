#---------------------------------------------------------------------
# Core of the physical simulation
#--------------------------------------------------------------------- 

from __future__ import division
from time import sleep
from numpy import sin, cos, pi
from numpy import array as narray
from scipy.integrate import ode

from settings import *

class Simulator:
    """Simulation Wrapper"""

    traj_gen = None
    controller = None
    solver = None
    logger = None
    visualizer = None

    def __init__(self, trajectory_generator, controller):
        self.traj_gen = trajectory_generator
        self.controller = controller

        # solver
        self.solver = ode(rhs)
        self.solver.set_initial_value(q0)
        self.solver.set_integrator(int_mode, method=int_method, rtol=int_rtol, atol=int_atol)

    def set_visualizer(self, visualizer_cb):
        self.visualizer = visualizer_cb

    def set_logger(self, logger_cb):
        self.logger = logger_cb

    def calcStep():
        '''
        Calcualte one step in simulation
        '''

        return solver.t, solver.integrate(solver.t+dt)

    def run(self):
        self.run = True
        while self.run:
            t, q = calcStep()

            if self.logger is not None:
                logger.log(t,q)

            if self.visualizer is not None:
                r_beam, T_beam, r_ball, T_ball = model.calcPositions(q)
                visualizer.updateScene(r_beam, T_beam, r_ball, T_ball)

            time.sleep(0.01)

    def stop(self):
        self.run = False


#---------------------------------------------------------------------
# plotting 
#---------------------------------------------------------------------
table = vtk.vtkTable()
#Time:
arrTime = vtk.vtkFloatArray()
arrTime.SetName("time")
#Error: yd-r
arrE = vtk.vtkFloatArray()
arrE.SetName("epsilon")
#psi3
arrPsi3 = vtk.vtkFloatArray()
arrPsi3.SetName("psi3")
#theta
arrTheta = vtk.vtkFloatArray()
arrTheta.SetName("theta")
#tau
arrTau = vtk.vtkFloatArray()
arrTau.SetName("tau")
# add rows to table 
table.AddColumn(arrTime)
table.AddColumn(arrE)
table.AddColumn(arrTheta)
table.AddColumn(arrPsi3)
table.AddColumn(arrTau)





#---------------------------------------------------------------------
# controller
#---------------------------------------------------------------------
def p_controller(t,q):
    yd = calcTrajectory(t,0)
    x1 = q[0]
    x4 = q[3]
    # Kp for yd = 0.1 and dr = 0.01
    Kp = 8
    if yd<0:
        yd = yd*(-1)
    if (x1>-0.05 and x1<0.05) or x4==0:
        return 0
    # ball is on the right side
    if x1>0:
        return Kp*(yd-x1)
    
    # ball is on the left side
    if x1<0:
        return  Kp*(yd+x1)

# Controller for modification of f designed by Christoph
def f_controller(t,q):
    yd_0 , yd_1 , yd_2 , yd_3 , yd_4 = calcTrajectory(t,4)
    x1 = q[0]
    x2 = q[1]
    x3 = q[2]
    x4 = q[3]
    # gain of the controller
    k0 = 16
    k1 = 32
    k2 = 24
    k3 = 8
    
    # calculate nonlinear terms phi
    phi1 = x1
    phi2 = x2  
    phi3 = -B*G*sin(x3)
    phi4 = -B*G*x4*sin(x3)
    
    # calculate fictional input v
    v = yd_4 + k3*(yd_3 - phi4) + k2*(yd_2 - phi3) + k1*(yd_1 - phi2) + k0*(yd_0 - phi1)
    
    # calculate a(x)
    a = -B*G*cos(x3)
    # calculate b(x)
    b = B*G*x4**2*sin(x3)
    
    # calculate u
    u = (v-b)/a
    
    return u

#---------------------------------------------------------------------
#
#---------------------------------------------------------------------

    
#---------------------------------------------------------------------
#
#---------------------------------------------------------------------
def updateScene(*args):
    '''
    Calculate new states and update the scene
    '''

    t, q = calcStep()
    print t,'\t', q
    r_beam, T_beam, r_ball, T_ball = calcPositions(q)

    setBodyState(beamActor, r_beam, T_beam)
    setBodyState(ballActor, r_ball, T_ball)

    renWin.Render()

    if abs(q[0]) > beam_length/2 :
        print '\n###################################### \n#  Ball fell down -> exiting application.'
        quit()
        raw_input('Simulation paused press Enter to continue')





'''
print '\n-> End of Simulation dumping measurements:'
table.Dump(6)

done = False
while not done:
    fileName = '../measurements/' + raw_input('Please specify filename: ') + '.vtk'
    if os.path.isfile(fileName):
        if raw_input('file already exists, overwrite? (y/n)') == 'y':
            done = True
    else:
        done  = True
    
print 'saving to', fileName

tWriter = vtk.vtkTableWriter()
tWriter.SetInputData(table)
tWriter.SetFileName(fileName)
tWriter.Update()
'''
