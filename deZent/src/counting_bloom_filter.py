#https://www.geeksforgeeks.org/counting-bloom-filters-introduction-and-implementation/
# https://medium.com/analytics-vidhya/cbfs-44c66b1b4a78
# https://www.geeksforgeeks.org/bloom-filters-introduction-and-python-implementation/
import math
from fnvhash import fnv1a_32
import mmh3
from bitarray import bitarray
from bitarray.util import ba2int,int2ba

from counting_data_structure import CntDataStructure

class CBloomFilter(CntDataStructure):
	def __init__(self, n, Counter_size,bucket_size,no_hashfn):
		#super().__init__(n)
		self.n=n
		self.N=Counter_size
		self.m=bucket_size
		self.k=no_hashfn

		self.bit_array = []
		for i in range(self.m):
			count=bitarray(self.N)
			count.setall(0)
			self.bit_array.append(count)

	def hash(self,item,seed):
		#return fnv1a_32(item.encode(),seed) % self.m
		#return fnv1a_32(str(item).encode(),seed) % self.m
		h = mmh3.hash(item.to_bytes(32), seed, False)
		return h % self.m
		#return fnv1a_32(item.to_bytes(32),seed) % self.m

	def add(self, item):

		for i in range(self.k):
			index = self.hash(item,i)

			cur_val=ba2int(self.bit_array[index])
			new_array=int2ba(cur_val+1,length=self.N)
			
			self.bit_array[index]=new_array
			
	def check(self, item):
		for i in range(self.k):
			index = self.hash(item,i)
			cur_val=ba2int(self.bit_array[index])

			if(not cur_val>0):
				return False
		return True
	
	def remove(self,item):
		if(self.check(item)):
			for i in range(self.k):
				index = self.hash(item,i)
				
				cur_val=ba2int(self.bit_array[index])
				new_array=int2ba(cur_val-1,length=self.N)
				self.bit_array[index]=new_array

			#print('Element Removed')
		else:
			print('Element is probably not exist')

	def is_empty(self):
		is_empty = True
		bool_buckets = [b.any() for b in self.bit_array]
		for bb in bool_buckets:
			if(bb):
				is_empty = False
				break
		return is_empty
	
	def subtract_constant(self, z_min):
		# iterate over buckets of cnt_struct
		for idx in range(len(self.bit_array)) :
			b = self.bit_array[idx].copy()

			# reset bucket to only keep reduced count
			self.bit_array[idx].setall(0)

			# bucket was not empty and larger than minimum required count
			if(ba2int(b) > z_min):
				# reduce count by z
				remainder = int2ba( ba2int(b) - z_min ) # TODO: check z-anon details: if >= z then only substract z-1
				# add padding to beginning of remainder to get bitarrays of same length
				l_pad = len(self.bit_array[idx]) - len(remainder)
				pad_bits = bitarray(l_pad)
				# get new bucket with remainder value
				b_remainder = pad_bits + remainder
				self.bit_array[idx] ^= b_remainder
		return