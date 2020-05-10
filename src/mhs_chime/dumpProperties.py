"""

Utility for printing properties of a class object.

"""
import inspect

def dumpProperties(obj, msg=None) :

    if msg is None:print("\n\n- {t:} ------------\n".format(t=(str(type(obj)))))
    else: print("\n\n- {t:} ------------\n".format(t=msg))

    for i in inspect.getmembers(obj):
        # to remove private and protected
        # functions
        if not i[0].startswith('_'):

            # To remove other methods that
            # doesnot start with a underscore
            if not inspect.ismethod(i[1]):
                print(i)

    print("\n-----------------------------\n")
