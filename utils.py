import requests
import typing as t


def get_html(url: str, method: str, data: t.Any = None) -> t.Optional[str]:
    try:
        if method.upper() == 'GET':
            result = requests.get(url)
        elif method.upper() == 'POST':
            result = requests.post(url, data=data)
        else:
            raise NotImplementedError()

        result.raise_for_status()
        return result.text

    except(requests.RequestException, ValueError):
        return None


def normilize_text(field: str) -> str:
    result = field.replace(u'\xa0', u' ').replace(
        '\t', '').replace('\n', '').strip()
    return result


def crawl_values(page, crawl_item) -> t.Dict:
    item_dict = {}
    for field in crawl_item:
        field_value = get_field_value(
            page,
            crawl_item[field].css_selectors,
            crawl_item[field].attr
        )
        item_dict[field] = field_value
    return item_dict


def get_field_value(page, css_selectors, attr=None) -> t.Any:
    for selectors in css_selectors:
        selector = selectors
        if page.select(selector):
            all_items = page.select(selector)
            field_value = []
            for item in all_items:
                if not attr:
                    value = normilize_text(item.text)
                else:
                    value = item[attr]
                field_value.append(value)
            if len(field_value) == 1:
                field_value = field_value[0]
            return field_value
        else:
            field_value = ''
            continue
    return field_value
