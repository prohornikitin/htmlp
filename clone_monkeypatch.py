from bs4 import Tag, NavigableString

def tag_clone(self):
    copy = type(self)(None, self.builder, self.name, self.namespace, 
                      self.nsprefix)
    # work around bug where there is no builder set
    # https://bugs.launchpad.net/beautifulsoup/+bug/1307471
    copy.attrs = dict(self.attrs)
    for attr in ('can_be_empty_element', 'hidden'):
        setattr(copy, attr, getattr(self, attr))
    for child in self.contents:
        copy.append(child.clone())
    return copy


Tag.clone = tag_clone
NavigableString.clone = lambda self: type(self)(self)