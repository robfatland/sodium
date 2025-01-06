import random as rand
from random import randint, choice
from math import fabs, sqrt
import numpy as np, matplotlib.pyplot as plt, sys


####
####
#
# format utility
#
####
####

def padnum(n, w):
    '''use spaces to left-pad a number (n) to a fixed width (w) string'''
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


def R_n_rough(n, x):
    '''returns a 1-sum ring with most if not all values between -x and x inclusive'''
    p = [randint(-x, x) for i in range(n-1)]
    p.append(1 - sum(p))
    return p


def R_n(n, x):
    '''builds and returns a random n-vertex ring: all values on [-x, x], sum = 1'''
    tries = 0
    while True:
        p = [randint(-x, x) for i in range(n)]
        if sum(p) == 1: return p
        tries += 1
        if tries > 1000000: break
    return []

def R_n_S(n, x, S):
    '''builds, returns a random n-vertex ring: all values on [-x, x], sum = S'''
    tries = 0
    while True:
        p = [randint(-x, x) for i in range(n)]
        if sum(p) == S: return p
        tries += 1
        if tries > 1000000: return 0
    return []

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
    '''return positive-valued shortest distances between sites a and b in ring Rn'''
    return min(abs(a - b), abs((a + n) - b), abs((a - n) - b))

def D(n, a, b):
    '''return compound distance between sites a and b in ring of size n'''
    if a < 0 or b < 0 or a >= n or b >= n or a == b: return 0
    if b > a: return (b - a)*(b - a - n)
    return (a - b)*(a - b - n) 

def CompoundDistance(n, a, b):
    '''return compound distance between sites a and b in ring of size n'''
    return D(n, a, b)

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
    '''Generalized to S > 0: return bool Is R quiescent? (all values non-negative)'''
    for i in range(len(R)):
        if R[i] < 0: return False
    return True


def Entropy(R):
    '''return entropy(R) aka flip sum aka entropy cost function, a double sum over site pairs: a * b * D(a, b)'''
    n, E = len(R), 0
    for i in range(n-1):
        for j in range(i+1, n): E += R[i]*R[j]*(j-i)*(j-i-n)
    return E


def Entropy2(R):
    """
    Alternate entropy calculation: E = triangle + final vertical (j = n - 1)
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
    while not Q(R):                                          # R -> Q flip iteration
        if verbose: print(Entropy(R), R)       
        nn, nl  = NegList(R)                                 # number and list of negative sites
        if nn < 1: return 0, 0                               # check error condition 
        R, v    = Flip(R, nl[rand.randint(0, nn-1)])         # flip a randomly chosen negative-valued site 
                                                             #   returns the resulting R and -2a, the + double flip sum 
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


######
######
#
# Cost functions
#
######
######


def CCost(R, delta):
    cost = 0
    n = len(R)
    for i in range(n):
        a = R[i]
        ip2 = i + delta
        while ip2 >= n: ip2 -= n
        b = R[ip2]
        cost += (a-b)**2
    return cost


def AbsCost(R, delta):
    '''Returns a cost value for a ring using an ad hoc absolute value scheme'''
    cost = 0
    n = len(R)
    for i in range(n):
        a = R[i]
        ip2 = i + delta
        while ip2 >= n: ip2 -= n
        b = R[ip2]
        cost += fabs(a-b)
    return cost    

def ECost(R): 
    '''Cost function is the Entropy() function'''
    return Entropy(R)


def AllHorseCollarsCost(R):
    '''Cost function for R: sum over all sites i of abs(sum(all-but-i-sites))'''
    n = len(R)
    total_sum = 0
    for i in range(n):
        this_sum = 0
        for j in range(i, i + n - 1):
            j = kJustify(j, n)
            this_sum += R[j]
        total_sum += fabs(this_sum)
    return total_sum


def OneHorseCollarCost(R, a):
    '''Cost function for R: Return sum of all sites except site a'''
    n = len(R)
    this_sum = 0
    for b in range(a + 1, a + 1 + n - 1):
        b = kJustify(b, n)
        this_sum += R[b]
    return this_sum

def ScholesCost(R):
    n = len(R)
    cost = 0
    for i in range(n):
        for j in range(n-1):
            this_sum = 0
            for k in range(i, i + j + 1):
                this_sum += R[kJustify(k, n)]
            cost += fabs(this_sum)
    return cost

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


def ChartIMO1986_3_solution_cost(n, x):
    '''For a ring of size n with max site value x: Chart to olympiad solution cost function'''
    R = R_n(n, x)
    c = []
    while not IsQuiescent(R):
        c.append(CCost(R, 2))
        nn, nl  = NegList(R)                                 # the number and list of negative sites
        R, v    = Flip(R, nl[rand.randint(0, nn-1)])         # execute a flip at a random negative site
    fig,ax=plt.subplots(figsize=(6,4))
    ax.plot(c)
    ax.set(title='Ring cost function with flips: Olympiad solution')


def CompareEntropyFormulaToEmpirical(n1, n2, n_trials, x):
    '''Run a few k trials comparing the entropy formula to actual entropy E(R -> Q) where R is randomly generated'''
    print()
    for n in range(n1, n2 + 1):
        noConflict = True
        for j in range(n_trials):
            R = R_n(n, x)
            E = Entropy(R)
            fc, Ecalc = RQ(R)
            if not E == Ecalc:
                print('    mismatch: ' + str(n) + ' with Rn = ' + str(R))
                noConflict = False
        if noConflict: print('n = ' + str(n) + '   ...all tests agree with the entropy cost function')
    return


def ChartEntropyCostFunction(n, x):
    '''For a ring of size n with max site value x: Chart to olympiad solution cost function'''
    R = R_n(n, x)
    c = []
    while not IsQuiescent(R):
        c.append(ECost(R))
        nn, nl  = NegList(R)                                 # the number and list of negative sites
        R, v    = Flip(R, nl[rand.randint(0, nn-1)])         # execute a flip at a random negative site
    fig,ax=plt.subplots(figsize=(6,4))
    ax.plot(c)
    ax.set(title='Ring entropy (cost function) with flips')


def ChartsToInvestigateHorseCollarCostFunctions(n, x):
    '''Compares horse collar cost function ideas'''
    R = R_n(n, x)
    c, d = [], []
    while True:
        nn, nl  = NegList(R)
        negsite = rand.randint(0, nn - 1)
        c.append(AllHorseCollarsCost(R))
        d.append(OneHorseCollarCost(R, nl[negsite]))
        R, v    = Flip(R, nl[negsite])
        c.append(AllHorseCollarsCost(R))
        d.append(OneHorseCollarCost(R, nl[negsite]))
        if IsQuiescent(R): break
    
    fig,ax=plt.subplots(figsize=(6,4))
    ax.plot(c)
    ax.set(title='All horse collars')
    
    fig,ax=plt.subplots(figsize=(6,4))
    ax.plot(d)
    ax.set(title='One horse collar')     

    
def ChartScholesCostFunction(n, x):
    '''Chart of the Scholes cost function over flips'''
    R = R_n(n, x)
    c = [ScholesCost(R)]
    while True:
        nn, nl  = NegList(R)
        negsite = rand.randint(0, nn - 1)
        R, v    = Flip(R, nl[negsite])
        this_cost = ScholesCost(R)
        c.append(this_cost)
        nn, nl  = NegList(R)
        if nn == 0: break
    fig,ax=plt.subplots(figsize=(6,4))
    ax.plot(c)
    ax.set(title='Scholes Cost Function')
    ax.set_xlabel('successive flips')
    ax.set_ylabel('A(R)')
    print(R)
   
def PrintScholesDeltaTable(spacer, min_a1, max_S):
    print()
    print("Scholes cost function (generalized) produces this table of A(R') - A(R) values")
    print()
    msg = ' ' + 'S         a1:  -1'
    spacer, min_a1, max_S = 8, -12, 12
    for a1 in range(-2, min_a1 -1, -1): msg += padnum(a1, spacer)
    print(msg)
    for S in range(1, max_S + 1):
        msg = padnum(S, 2) + ' '*8
        for a1 in range(-1, min_a1 - 1, -1):
            msg += padnum(fabs(S + a1) - fabs(S - a1), spacer)
        print(msg)

