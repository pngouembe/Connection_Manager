from com.header import Header

action_list = []


def pass_fct(*args, **kwargs):
    pass


for i in [e.value for e in Header]:
    action_list.append(pass_fct)


def action(com_header: Header):
    global action_list

    def wrap(func):
        action_list[com_header.value] = func
    return wrap


@action(Header.INVALID)
def invalid_handling(msg):
    print(msg)
    return False
