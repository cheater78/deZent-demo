# https://www.geeksforgeeks.org/counting-bloom-filters-introduction-and-implementation/
# https://medium.com/analytics-vidhya/cbfs-44c66b1b4a78
# https://www.geeksforgeeks.org/bloom-filters-introduction-and-python-implementation/

# from fnvhash import fnv1a_32
import mmh3
from bitarray import bitarray
from bitarray.util import ba2int,int2ba

from counting_data_structure import CntDataStructure, MeasurementKey

class CBloomFilter(CntDataStructure):

	def __init__(self, n: int, counter_size: int, bucket_size: int, no_hashfn: int):
		self.n: int = n
		self.N: int = counter_size
		self.m: int = bucket_size
		self.k: int = no_hashfn

		self.bit_array: list[bitarray] = []
		for _ in range(self.m):
			count=bitarray(self.N)
			count.setall(0)
			self.bit_array.append(count)

	def add(self, item: MeasurementKey) -> None:
		for i in range(self.k):
			index: int = self.__cfb_hash__(item, i)

			cur_val = ba2int(self.bit_array[index])
			new_array = int2ba(cur_val+1,length=self.N)
			
			self.bit_array[index] = new_array
			
	def check(self, item: MeasurementKey) -> bool:
		for i in range(self.k):
			index: int = self.__cfb_hash__(item, i)
			cur_val = ba2int(self.bit_array[index])

			if(not cur_val>0):
				return False
		return True
	
	def remove(self, item: MeasurementKey):
		if(self.check(item)):
			for i in range(self.k):
				index: int = self.__cfb_hash__(item, i)
				
				cur_val = ba2int(self.bit_array[index])
				new_array = int2ba(cur_val-1,length=self.N)
				self.bit_array[index] = new_array

			# print('Element Removed')
		else:
			print('Element does probably not exist')
			pass

	def is_empty(self) -> bool:
		is_empty = True
		bool_buckets = [b.any() for b in self.bit_array]
		for bb in bool_buckets:
			if(bb):
				is_empty = False
				break
		return is_empty
	
	def subtract_constant(self, z_min: int) -> None:
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
	
	def print_cnt_struct(self):
		line_cnt: int = 0
		bit_str: str = ''
		for b in self.bit_array:
			bit_str = bit_str + b.to01() + ' '
			line_cnt += 1
			if(line_cnt == 4):
				line_cnt = 0
				print(bit_str)
				bit_str = ''
		print(bit_str)

	'''
		The Hash function used by the CFB to index its items
	'''
	def __cfb_hash__(self, item: MeasurementKey, seed: int) -> int:
		# previously was:
		# return fnv1a_32(item.encode(),seed) % self.m # only 
		# return fnv1a_32(str(item).encode(),seed) % self.m
		# return fnv1a_32(item.to_bytes(32),seed) % self.m
		h = mmh3.hash(item.to_bytes(32), seed, False)
		return h % self.m