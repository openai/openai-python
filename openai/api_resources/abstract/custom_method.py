from urllib.parse import quote_plus

from openai import util


def custom_method(name, http_verb, http_path=None):
    if http_verb not in ["get", "post", "delete"]:
        raise ValueError(
            "Invalid http_verb: %s. Must be one of 'get', 'post' or 'delete'"
            % http_verb
        )
    if http_path is None:
        http_path = name

    def wrapper(cls):
        def custom_method_request(cls, sid, **params):
            url = "%s/%s/%s" % (
                cls.class_url(),
                quote_plus(sid),
                http_path,
            )
            return cls._static_request(http_verb, url, **params)

        existing_method = getattr(cls, name, None)
        if existing_method is None:
            setattr(cls, name, classmethod(custom_method_request))
        else:
            # If a method with the same name we want to use already exists on
            # the class, we assume it's an instance method. In this case, the
            # new class method is prefixed with `_cls_`, and the original
            # instance method is decorated with `util.class_method_variant` so
            # that the new class method is called when the original method is
            # called as a class method.
            setattr(cls, "_cls_" + name, classmethod(custom_method_request))
            instance_method = util.class_method_variant("_cls_" + name)(existing_method)
            setattr(cls, name, instance_method)

        return cls

    return wrapper
