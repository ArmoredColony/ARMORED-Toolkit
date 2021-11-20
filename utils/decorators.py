
def abstract_class_attributes(*names):
    """Class decorator to add one or more abstract attribute."""

    def _func(cls, *names):
        """ Function that extends the __init_subclass__ method of a class."""

        # Add each attribute to the class with the value of NotImplemented
        for name in names:
            setattr(cls, name, NotImplemented)

        # Save the original __init_subclass__ implementation, then wrap
        # it with our new implementation.
        orig_init_subclass = cls.__init_subclass__

        def new_init_subclass(cls, **kwargs):
            """
            New definition of __init_subclass__ that checks that
            attributes are implemented.
            """

            # The default implementation of __init_subclass__ takes no
            # positional arguments, but a custom implementation does.
            # If the user has not reimplemented __init_subclass__ then
            # the first signature will fail and we try the second.
            try:
                orig_init_subclass(cls, **kwargs)
            except TypeError:
                orig_init_subclass(**kwargs)

            # Check that each attribute is defined.
            for name in names:
                if getattr(cls, name, NotImplemented) is NotImplemented:
                    raise NotImplementedError(f'You forgot to define a <{name}> class attribute for the <{cls.__name__}> sub class!')

        # Bind this new function to the __init_subclass__.
        # For reasons beyond the scope here, it we must manually
        # declare it as a classmethod because it is not done automatically
        # as it would be if declared in the standard way.
        cls.__init_subclass__ = classmethod(new_init_subclass)

        return cls

    return lambda cls: _func(cls, *names)

