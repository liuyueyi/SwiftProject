from stack import stack

class node:
    def __init__(self, value1 = '' ,lchild = None, rchild = None):
        self.value = value1
        self.left = lchild
        self.right = rchild
        return None

def nextAttribute(policy, index):
    start = index
    length = len(policy)
    while index < length :
        index += 1
        if index == length:
            return index, policy[start : ]
        ch = policy[index]
        if ch == ' ' or ch == ')' or ch == '(':
            break
    
    if policy[index] == ' ':
        while index < length and policy[1+index] == ' ':
            index += 1
        return index, policy[start : index].strip()
       
    return index, policy[start : index]
    
    
def generateTree(policy):
    stringStack = stack()
    nodeStack = stack()
    i = 0
    while i < len(policy):
        word = ''
        if policy[i] == '(':
            word = '('
            stringStack.push(word)
            i += 1
        elif policy[i] == ')':
            word = ')'
            r = node()
            if stringStack.top() == 'not':
                r = None
            else:
                r = nodeStack.top()
                nodeStack.pop()
            l = nodeStack.top()
            nodeStack.pop()
            
            n = node(stringStack.top(), l, r)
            nodeStack.push(n)
            stringStack.pop()
            stringStack.pop()
            
            i += 1
        elif policy[i] == ' ':
            i += 1
        else:
            i, word = nextAttribute(policy, i)
            if word == 'and' or word == 'or' or word == 'not':
                stringStack.push(word)
            else:
                n = node(word)
                nodeStack.push(n)

    r = None
    if stringStack.top() != 'not':
        r = nodeStack.top()
        nodeStack.pop()
    
    l = nodeStack.top()
    nodeStack.pop()
    
    root = node(stringStack.top(), l, r)
    stringStack.pop()
    
    return root

def search(root):
    print 'value is : ' , root.value
    if root.left != None:
        search(root.left)
    if root.right != None:
        search(root.right)

def match(root, attrs):
    if root.value == 'not':
        if match(root.left, attrs) > 0 :
            return 0
        else:
            return 1
    elif root.value == 'and':
        if match(root.left, attrs) + match(root.right, attrs) == 2:
            return 1
        else:
            return 0
    elif root.value == 'or':
        if match(root.left, attrs) > 0 or match(root.right, attrs) > 0:
            return 1
        else:
            return 0
    else:
        for temp in attrs:
            if temp == root.value:
                return 1
        return 0      


#policy = '(((A or BC)and(E or  FG ) ) and((H and IJ)or ( K or MN))) or (not TT)'
#attrs = ['A', 'E', 'HIJ', 'KMN']
#policy = '(a and b) or c'
#root = generateTree(policy)
#search(root)
#if match(root, attrs) > 0:
#    print 'matched'
#else:
#    print 'not matched'
