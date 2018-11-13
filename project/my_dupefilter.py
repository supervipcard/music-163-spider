from scrapy.utils.project import get_project_settings
from scrapy_redis.dupefilter import RFPDupeFilter


class HashMap(object):
    def __init__(self, m, seed):
        self.m = m
        self.seed = seed

    def hash(self, value):
        """
        Hash Algorithm
        :param value: Value
        :return: Hash Value
        """
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.m - 1) & ret


class BloomFilter(object):
    def __init__(self, server, key, bit, hash_number):
        """
        Initialize BloomFilter
        :param server: Redis Server
        :param key: BloomFilter Key
        :param bit: m = 2 ^ bit
        :param hash_number: the number of hash function
        """
        # default to 1 << 30 = 10,7374,1824 = 2^30 = 128MB, max filter 2^30/hash_number = 1,7895,6970 fingerprints
        self.m = 1 << bit
        self.seeds = range(hash_number)
        self.server = server
        self.key = key
        self.maps = [HashMap(self.m, seed) for seed in self.seeds]

    def exists(self, value):
        """
        if value exists
        :param value:
        :return:
        """
        if not value:
            return False
        exist = True
        for map in self.maps:
            offset = map.hash(value)
            exist = exist & self.server.getbit(self.key, offset)
        return exist

    def insert(self, value):
        """
        add value to bloom
        :param value:
        :return:
        """
        for f in self.maps:
            offset = f.hash(value)
            self.server.setbit(self.key, offset, 1)


class MyRFPDupeFilter(RFPDupeFilter):
    def __init__(self, server, key, debug=False):
        super(MyRFPDupeFilter, self).__init__(server, key, debug)
        settings = get_project_settings()
        bit = settings.getint('BLOOMFILTER_BIT', 30)
        hash_number = settings.getint('BLOOMFILTER_HASH_NUMBER', 6)
        self.bf = BloomFilter(server, key, bit, hash_number)

    def request_seen(self, request):
        fp = self.request_fingerprint(request)
        if self.bf.exists(fp):
            return True    # True if already exists.
        else:
            self.bf.insert(fp)
            return False
