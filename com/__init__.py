import header

header_dict = {k: v for k, v in vars(header).items() if not k.startswith("__")}
header_list = list(header_dict.values())
header_max = max(header_list)
