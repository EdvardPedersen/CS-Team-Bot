#!/usr/bin/env python3.10


class  MyDict(dict):


    def top_n(self, n):
        return sorted(self, key=self.get, reverse=True)[:n]

test = MyDict()
test['te'] = 0
test['tes']=1
test['test']=2

print(test.top_n(2))