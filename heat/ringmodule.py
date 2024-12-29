import random as rand
from random import randint, choice

####
####
#
# format utility
#
####
####

def padnum(n, w):
    s = str(n)
    if len(s) > w: return -1
    else: return ' '*(w - len(s)) + s

####
####
#
# ring utility
#
####
####

def R_n_zero(n, x):
    '''returns a zero-sum ring with most values between -x and x inclusive'''
    p = [randint(-x, x) for i in range(n-1)]
    p.append(-sum(p))
    return p

def R_n(n, x):
    '''returns a 1-sum ring with most or all values between -x and x inclusive'''
    p = [randint(-x, x) for i in range(n-1)]
    p.append(1 - sum(p))
    return p

def kJustify(k, n):
    '''ensure site index k is on [0, n-1]'''
    while k < 0: k += n
    while k >= n: k -= n
    return k

def kDec(k, n):
    '''safely decrement site index k'''
    kmo = k - 1
    while kmo < 0: kmo += n
    return kmo

def kInc(k, n):
    '''safely increment site index k'''
    kpo = k + 1
    while kpo >= n: kpo -= n
    return kpo

def Distance(a, b, n):
    '''shorter of two distances between site indices a and b for ring n'''
    return min(abs(a - b), abs((a + n) - b), abs((a - n) - b))

def NegList(R):
    '''for R: return count of negative-valued sites and a list of their indices'''
    neglocs, nNeg, n = [], 0, len(R)
    for i in range(n):
        if R[i] < 0: neglocs.append(i); nNeg += 1
    return nNeg, neglocs

def PosList(R):
    '''for R: return count of positive-valued sites and a list of their indices'''
    poslocs, nPos, n = [], 0, len(R)
    for i in range(n):
        if R[i] > 0: poslocs.append(i); nPos += 1
    return nPos, poslocs

def Flip(R, a):
    '''for R: flip site a; return both R and the flip 'double-positive' value'''
    n = len(R)
    if a >= 0 and a < n:
        v = -R[a]
        if v > 0:
            R[a] = v
            R[kDec(a, n)] -= v
            R[kInc(a, n)] -= v
    return R, 2*v

def IsQuiescent(R):
    '''for R: Is quiescent? (presumes sum = 1)'''
    n, Rsum = len(R), 0
    for i in range(n):
        if R[i] < 0: return False
        Rsum += R[i]
    if not Rsum == 1: return False
    return True

def Q(R):
    '''for R: all values non-negative? (generalized quiescence)'''
    for i in range(len(R)):
        if R[i] < 0: return False
    return True

def Entropy(R):
    '''for R: return a predicted flip sum to reach Q'''
    n, E = len(R), 0
    for i in range(n-1):
        for j in range(i+1, n): E += R[i]*R[j]*(j-i)*(j-i-n)
    return E

def Entropy2(R):
    """
    for R: Second version of entropy calculation... a bit obscure... fossil note is: E = triangle + final vertical (j = n - 1). Does s2 save the day?
    """
    n, s1, s2 = len(R), 0, 0
    for i in range(n-2):                                    
        for j in range(i+1, n-1): s1 += R[i]*R[j]*(j - i)*((j - i) - n) 
    j = n - 1
    for i in range(n-1): s2 += R[i]*R[j]*(j - i)*((j - i) - n) 
    return s1, s2, s1 + s2

def RQ(R, verbose=False):
    '''for R, verbose False: resolve to Q via random choices and return fc, fs'''
    fc, fs = 0, 0                                            # reset flip count and sum
    while not IsQuiescent(R):                                # Given R this while drives it to Q
        if verbose: print(Entropy(R), R)       
        nn, nl  = NegList(R)                                 # number and list of negative sites
        R, v    = Flip(R, nl[rand.randint(0, nn-1)])         # flip randomly; return 
                                                             #   tuple = new R + 2 x abs(negative site) 
        fc     += 1                                          # update flip count
        fs     += v                                          # update flip sum
    return fc, fs


def RPositives(R):
    '''for R: return a list of positive-valued indices'''
    return [i for i in range(len(R)) if R[i]  > 0]


def RNegatives(R):
    '''for R: return a list of negative-valued indices'''
    return [i for i in range(len(R)) if R[i]  < 0]


def RNonpositives(R):
    '''for R: return a list of non-positive-valued indices'''
    return [i for i in range(len(R)) if R[i] <= 0]


def RNonnegatives(R): 
    '''for R: return a list of non-negative-valued indices'''
    return [i for i in range(len(R)) if R[i] >= 0]


def ReverseFlip(R, i, n):
    '''for R: Returns R after site i has been reverse-flipped'''
    RF = R[:]
    a = RF[i]
    RF[i] = -a
    RF[i-1] += a
    RF[(i+1)%n] += a
    return RF


def Congruent(R1, R2):
    '''for R1, R2: bool R1 congruent with R2 up to a phase shift, does not handle CW/CCW (cf list.reverse())'''
    n = len(R2)
    for i in range(n):              # start-compare index of R2
        match = True                # presume this is a match
        for j in range(n):          # run through R1 indices
            R2idx = (i + j) % n     
            if R1[j] != R2[R2idx]: 
                match = False
                break
        if match: return True
    return False


def RingMagnitude(R):
    '''
    returns the maximum absolute value of site values in R
    '''
    n, ringmax = len(R), 0
    for i in range(n):
        if abs(R[i]) > ringmax: ringmax = abs(R[i])
    return ringmax


def IncrementR(R, m, i):
    '''IncrementR(R, m, i): From R build (odometer-style) and return a new ring constrained by abs(site) <= m.
    The index i indicates where the increment should be attempted. Use recursion to accommodate rollover.'''
    n = len(R)
    if i >= n or i < 0: return False
    R[i] += 1
    if R[i] > m:
        R[i] = -m
        return IncrementR(R, m, i+1)
    else: return R


def GenerateAllPossibleRings(m, n):
    '''
    Return a list of all possible rings Rn with abs(site) <= m: Excluding cyclic/chiral degeneracy
    '''
    L = []                  # To return L: A list of lists (rings)
    R = [-m]*n              # An "all negative values" ring... has a bad sum
    
    while True:
        Rt = R.copy()                                              # Rt is a trial ring, a copy of R (that we may need to reverse)
        if not sum(Rt) == 1:                       goodR = False   # Check that Rt has sum 1
        elif not (min(Rt) >= -m and max(Rt) <= m): goodR = False   #     ...and that all of Rt is in-bounds 
        else: 
            goodR = True                          # Rt has sum = 1, sites all in (-m, m)
            for c in L:                           # c is sequence of rings from the existing L for comparison
                if Congruent(Rt, c):
                    goodR = False
                    break
                Rt.reverse()
                if Congruent(Rt, c):
                    goodR = False
                    break
        if goodR: L.append(R[:])                  # Rt may at this point be reversed; so append R 
        R = IncrementR(R, m, 0)                   # Always attempt the odometer increase of R at site 0
        if not R: return L                        #    returns False when no more increments are possible

####
####
#
# Baroque and Bespoke output
#
####
####

def PrintCaseTables(n1, n2, b1, b2):
    print()
    print('Binary rings')
    print('Place a positive value b at site index 0')
    print('Place a negative value 1-b at site index s and calculate D = s*s - n*s')
    print('Flip the negative-valued site; and repeat flips until the ring is quiescent')
    print('  ...with results tallied in these tables')
    print()
    print('n = number of sites, b is the value of the + site, s is the site offset between + and -')
    print()
    print(" n, b     s   fc   fs   -D     s   fc   fs   -D     s   fc   fs   -D     s   fc   fs   -D     s   fc   fs   -D")      
    for n in range(n1, n2 + 1):
        for b in range(b1, b2+1):
            msg = padnum(n, 2) + ',' + padnum(b, 2) + ' '*5
            for s in range(1, n//2 + 1):
                R = [b]
                for i in range(1, s): R.append(0)
                R.append(1-b)
                for i in range(s+1, n): R.append(0)
                fc, fs = RQ(R)
                D = s*s - n*s
                msg = msg + padnum(s,1) + ' '
                msg = msg + padnum(fc, 4) + ' '
                msg = msg + padnum(fs, 4) + ' '
                msg = msg + padnum(-D, 4) + ' '*5
            print(msg)
        print()
        
def PrintPossible(m_max, n):
    '''Print how many non-degenerate ring configurations exist for a given size n and site constraint m'''
    print('For ring size ' + str(n) + '...')
    for m in range(1, m_max + 1):
        p = GenerateAllPossibleRings(m, n)
        print('       constraint ' + str(m) + ' yields ' + str(len(p)) + ' possible rings')

