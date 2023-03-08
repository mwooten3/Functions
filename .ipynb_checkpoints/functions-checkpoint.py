# Stupid script to hold various stupid functions because i'm lazy


# Given start and end time objects, return string with elapsed time
def calculateElapsedTime(start, end, unit = 'minutes'):
    
    # start and end = time.time()
    
    if unit == 'minutes':
        elapsedTime = round((time.time()-start)/60, 4)
    elif unit == 'hours':
        elapsedTime = round((time.time()-start)/60/60, 4)
    elif unit == 'seconds':
        elapsedTime = round((time.time()-start), 4)  
        
    #print("\nEnd: {}\n".format(time.strftime("%m-%d-%y %I:%M:%S %p")))
    #print(" Elapsed time: {} {}\n".format(elapsedTime, unit))
    
    return "{} {}".format(elapsedTime, unit)
