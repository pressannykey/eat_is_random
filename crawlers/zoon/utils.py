import requests
import typing as t


def get_html(url: str, method: str, data: t.Any = None) -> t.Optional[str]:
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
    }

    proxies = {
        "http": "103.111.183.46:80",
        "https": "103.111.183.46:80",
    }

    if method.upper() == "GET":
        result = requests.get(url, headers=headers, proxies=proxies)
    elif method.upper() == "POST":
        result = requests.post(url, headers=headers, proxies=proxies, data=data)
    else:
        raise NotImplementedError()

    result.raise_for_status()
    return result.text


def normilize_text(field: str) -> str:
    result = field.replace(u"\xa0", u" ").replace("\t", " ").replace("\n", " ").strip()
    return result


def parse_values(page, crawl_item) -> t.Dict:
    item_dict = {}
    for field in crawl_item:
        field_value = get_field_value(
            page, crawl_item[field].css_selectors, crawl_item[field].attr
        )
        item_dict[field] = field_value

    return item_dict


def get_field_value(
    page, css_selectors: t.List[str], attr: t.Optional[str] = None,
) -> t.Union[t.List, str]:
    field_value = []
    if not css_selectors:
        # just for lon-lat :(
        value = page[attr]
        field_value.append(value)
        return field_value[0]

    for selector in css_selectors:
        all_items = page.select(selector)
        if not all_items:
            continue

        for item in all_items:
            value = item[attr] if attr else normilize_text(item.text)
            field_value.append(value)

    if len(field_value) == 1:
        field_value = field_value[0]
    elif len(field_value) == 0:
        field_value = ""

    return field_value
