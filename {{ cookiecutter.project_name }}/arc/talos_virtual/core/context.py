class Context(object):
    pass


class TalosVirtual:
    context = None

    def __init__(self, context):
        self.context = context


class RuntimeDatas:
    context = None

    def __init__(self, context):
        self.context = context
