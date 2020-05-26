import numpy as np

def bufferArray(Arr):

    # Buffer the 0-pixels in a binary array by 1 pixel, 8-pixel window
    
    nrows= Arr.shape[0] # number of rows (size of Y direction)
    ncols= Arr.shape[1] # number of columns (size of X)

    ones_row = np.ones((1, ncols), dtype = np.int) # add to top and bottom
    ones_col = np.ones((nrows), dtype = np.int) # add to left and right

    # Arr1 - shift up (remove first row, add bottom row) - then multiply
    Arr1 = np.delete(Arr, (0), axis=0) # removes first row
    #Arr1 = np.append(Arr1, ones_row, 0) # zero adds to the row axis
    Arr1 = np.insert(Arr1, (nrows-1), ones_row, axis=0) # zero adds to the row axis

    # Arr2 - shift down (remove last row, add first row)
    Arr2 = np.delete(Arr, (nrows-1), axis=0) # removes last row
    Arr2 = np.insert(Arr2, 0, ones_row, axis=0)

    # Arr3 - shift right (remove last column, add first column)
    Arr3 = np.delete(Arr, (ncols-1), axis=1)
    Arr3 = np.insert(Arr3, 0, ones_col, axis=1)

    #Arr4 - shift left (remove first column, add last column)
    Arr4 = np.delete(Arr, (0), axis=1)
    Arr4 = np.insert(Arr4, (ncols-1), ones_col, axis=1)

    # Arr5 shift up one AND left one, Arr1 is already shifted up, now shift left
    Arr5 = np.delete(Arr1, (0), axis=1)
    Arr5 = np.insert(Arr5, (ncols-1), ones_col, axis=1)

    # Arr6 shift up one AND right one -- shift Arr1 right
    Arr6 = np.delete(Arr1, (ncols-1), axis=1)
    Arr6 = np.insert(Arr6, 0, ones_col, axis=1)

    # Arr7 shift down one AND left one -- shift Arr2 left
    Arr7 = np.delete(Arr2, (0), axis=1)
    Arr7 = np.insert(Arr7, (ncols-1), ones_col, axis=1)

    # Arr8 shift down one AND right one -- shift Arr2 right
    Arr8 = np.delete(Arr2, (ncols-1), axis=1)
    Arr8 = np.insert(Arr8, 0, ones_col, axis=1)

    bufferedArr = Arr*Arr1*Arr2*Arr3*Arr4*Arr5*Arr6*Arr7*Arr8

    #print "   Finish buffering array: %s" % datetime.datetime.now().strftime("%I:%M%p  %a, %m-%d-%Y")
    return bufferedArr

def swapValues(arr):
    
    # To swap values in a binary 0/1 array

    arrSwap = np.where(arr==0, 2, arr)          # 0 --> 2
    arrSwap = np.where(arrSwap==1, 0, arrSwap)  # 1 --> 0
    arrSwap = np.where(arrSwap==2, 1, arrSwap)  # 2 --> 1

    return arrSwap
    
# So actually bufferArray buffers 0-pixels, not 1
# Solution if you want to buffer 1-pixels is to switch 0's and 1's, buffer, then switch back

# Original array - 1 for cloud, 0 for not-cloud
arr = np.array([[0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 1]])
print arr

# New array - 0 for cloud, 1 for not-cloud
swapArr = swapValues(arr)
print swapArr

outSwap = bufferArray(swapArr)
out = swapValues(outSwap)

print out
