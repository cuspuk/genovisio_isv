from typing import Any

def count_or_append_types(type_element: str, cnv_types_dict: dict[str, int]):
    if type_element in cnv_types_dict.keys():
        cnv_types_dict[type_element] = cnv_types_dict[type_element] + 1
    else:
        cnv_types_dict[type_element] = 1

    return cnv_types_dict


def iterate_sv_info(info_sv: list[dict[str, Any]], element_type: str):
    cnv_types_dict = {}
    for doc in info_sv:
        if element_type in doc.keys():
            cnv_types_dict = count_or_append_types(doc[element_type], cnv_types_dict)
    return cnv_types_dict