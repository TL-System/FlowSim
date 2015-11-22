
class PowerLaw:
    """
    This class is used to generate power-law distribution.
    """
    def __init__(self, alpha=1.0, totalNums = 1000, rank=100):
        self.alpha = alpha
        self.N = totalNums
        self.rankRange = rank
        self.SetAccessPattern()

    def GetCoefficient(self):
        """
        The power-law distribution is formed as y=A*x^(-alpha). y is the number of access times for range x'th item.
        alpha(>0) indicates the skewness of the distirbution.
        N is the total access times. If we consider the first rank M items, we have
        N = A*1^(-alpha) + A*2^(-alpha) + ... + A*M^(-alpha), thus
        This function is to compute the value of A
        """
        l = [i ** (-self.alpha) for i in range(1, self.rankRange + 1)]
        self.A = float(self.N) / sum(l)

    def SetAccessPattern(self):
        """
        Set the access list along with the rankRange. For example, for rank 100, there are 100 items
        in the access list sorted by their rank
        """
        self.GetCoefficient()

    def GetTotalNumber(self, cof):
        totalNums = sum([cof * (i ** (-self.alpha)) for i in range(1, self.rankRange + 1)])
        print totalNums

    def GetDistribution(self):
        dist = []
        for i in range(1, self.rankRange + 1):
            v = int(self.A * (i ** (-self.alpha)))
            if v > 0:
                dist.append(v)
            else:
                break
        return dist

