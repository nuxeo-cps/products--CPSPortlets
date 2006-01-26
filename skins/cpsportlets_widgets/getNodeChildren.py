##parameters=listed_tree=[], node=None, degree=1, **kw

children = []

if node in listed_tree:
    index = listed_tree.index(node)
    parent_level = node['level']
    for item in listed_tree[index + 1:]:
        if item['level'] == (parent_level + degree):
            children.append(item)
        if item['level'] <= parent_level:
            break
        
return children
