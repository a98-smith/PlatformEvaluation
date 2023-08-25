import matplotlib.pyplot as plt
import numpy as np
import analysis_utils as utils

pi = np.pi
twopi = 2 * pi

chirps = {'contact':0,'release':0.5}
frequencies = {'low':2,'med':4,'high':8,'max':16}
colors = ['darkblue','mediumblue','slateblue','royalblue']

signals = {'contact':0,'low':2,'med':4,'high':8,'max':16,'release':0.5}

if __name__ == '__main__':
    
	i = 0 
 
	for signal in signals:
		if signal in ['contact','release']:
			x = np.linspace(0,0.25,250)
			start = end = np.zeros(1)
			y = 100 * np.sin(( twopi * x) + signals[signal]*pi ) 
			y = np.append(start, y)
			y = np.append(y, end)
	
			plt.plot( y ,'midnightblue')

		else:
			x = np.linspace(0,0.5, 500)
			y = 50 * np.sin((signals[signal] * twopi * x) - pi/2) +50
		
			plt.plot( y ,color=colors[i])
			i+=1
   
		plt.show()
 
 
 
	# for frequency in frequencies:
    
	# 	x = np.linspace(0,0.5, 500)
	# 	y = 50 * np.sin((frequencies[frequency] * twopi * x) - pi/2) +50
	
	# 	plt.plot( y ,color=colors[i])
	# 	i+=1
	# 	plt.show()
  
	# for chirp in ['contact','release']:
		
	# 	x = np.linspace(0,0.25,250)
	# 	start = end = np.zeros(1)
	# 	y = 100 * np.sin(( twopi * x) + chirps[chirp]*pi ) 
	# 	y = np.append(start, y)
	# 	y = np.append(y, end)
  
	# 	plt.plot( y ,'midnightblue')
	# 	plt.show()