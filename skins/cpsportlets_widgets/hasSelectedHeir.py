##parameters=listed_tree=[], node=None, **kw

if node in listed_tree:
    index = listed_tree.index(node)
    parent_level = node['level']
    for item in listed_tree[index+1:]:
        if (item['selected'] is True) and (item['level'] > parent_level):
            return True
        if item['level'] <= parent_level:
            return False
        
return False

