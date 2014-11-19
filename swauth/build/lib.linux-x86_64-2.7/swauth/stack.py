class stack:
    def __init__(self):
        self.content = []
    
    def push(self, con):
        self.content.append(con)
    	
    def pop(self):
        if len(self.content) > 0:
            self.content.pop()
        
    def top(self):
        return self.content[len(self.content) - 1]
    	
    def isempty(self):
        if len(self.content) == 0:
            return True
        else:
            return False
            
'''
temp = stack()
temp.push('hello')
temp.push('temp')
temp.push('sadf')
print temp.top()
temp.pop()
print temp.top()
print repr(temp.isempty())
'''
