from com.header import Header

header_dict = {h.name: h.value for h in Header}
header_list = list(header_dict.values())
header_max = max(header_list)
