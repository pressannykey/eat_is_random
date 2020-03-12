from bs4 import BeautifulSoup
import requests


def get_html(url, method):
    try:
        result = getattr(requests, method)(url)
        result.raise_for_status()
        return result.text
    except(requests.RequestException, ValueError):
        return False


class DataFiller():
    def __init__(self):
        self.result_rests = []
        self.result_menu = []

    def _get_menu(self, html):
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            # не у всех ресторанов етсь меню. если есть, забираем
            try:
                all_dishes = soup.find(
                    'div', class_='pricelist-group').findAll('div', class_='pricelist-item-content oh')
                menu = []
                for dish in all_dishes:
                    if dish.find('div', class_='title fs-large oh').find('a'):
                        title = dish.find('a').text
                        category_url = dish.find('a')['href']
                    else:
                        title = dish.find('span').text
                        category_url = ''
                    if 'antikafe' in category_url:
                        continue
                    if dish.find('div', class_='description'):
                        description = dish.find(
                            'div', class_='description').find('span', class_='js-pricelist-description').text
                    else:
                        description = ''
                    if dish.find('div', class_='price-weight'):
                        price = dish.find(
                            'div', class_='price-weight').find('strong').text
                    else:
                        price = ''
                    menu.append({
                        'title': title.replace(u'\xa0', u' ').replace('\t', '').replace('\n', '').strip(),
                        'description': description.replace(u'\xa0', u' ').replace('\t', '').replace('\n', '').strip(),
                        'category_url': category_url.replace(u'\xa0', u' ').replace('\t', '').replace('\n', ''),
                        'price': price.replace(u'\xa0', u' ').replace('\t', '').replace('\n', ''),
                    })
                return menu
            except AttributeError:
                return False
        return False

    def _get_info(self, html):
        # разбить на более мелкие функции
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            if soup.find('span', class_='rating-value'):
                rating = float(soup.find('span', class_='rating-value').text)
            else:
                rating = ''
            all_info = soup.find('div', class_='oh service-maininfo')
            if all_info.find('div', class_='service-phones-list'):
                phone_number = all_info.find(
                    'div', class_='service-phones-list').find('span')['data-number']
            else:
                phone_number = ''
            other_info = all_info.find('div', class_='mg-bottom-m')
            if other_info.find('div', class_='invisible-links'):
                adress = other_info.find(
                    'div', class_='invisible-links').find('address').text
            else:
                adress = ''
            if other_info.find('div', class_='invisible-links').findAll('a'):
                rayon = []
                rayon_all = other_info.find(
                    'div', class_='invisible-links').findAll('a')
                for rayons in rayon_all:
                    rayon1 = rayons.text.replace(u'\xa0', u' ').replace(
                        '\t', '').replace('\n', '')
                    rayon.append(rayon1)
            else:
                rayon = ''
            metro_all = other_info.findAll('div', class_='address-metro')
            if metro_all:
                metro = []
                for metros in metro_all:
                    metro1 = metros.text.replace(u'\xa0', u' ').replace(
                        '\t', '').replace('\n', '')
                    metro.append(metro1)
            else:
                metro = ''
            if all_info.find('span', itemprop='priceRange'):
                price_range = all_info.find(
                    'span', itemprop='priceRange').text
            else:
                price_range = ''
            if all_info.find('dd', class_='upper-first'):
                business_hours = all_info.find(
                    'dd', class_='upper-first').find('div').text
            else:
                business_hours = ''
            if all_info.find('div', class_="service-website"):
                link = all_info.find(
                    'div', class_="service-website").find('a')['href']
            else:
                link = ''

            info = {
                'phone_number': phone_number.replace(u'\xa0', u' ').replace('\t', '').replace('\n', ''),
                'adress': adress.replace(u'\xa0', u' ').replace('\t', '').replace('\n', ''),
                'rayon': rayon,
                'metro': metro,
                'price_range': price_range.replace(u'\xa0', u' ').replace('\t', '').replace('\n', ''),
                'business_hours': business_hours.replace(u'\xa0', u' ').replace('\t', '').replace('\n', ''),
                'original_link': link,
                'rating': rating,
            }
            return info
        return False

    def _fill_rest_data(self, rest):
        rest_url = rest.find('div', class_='H3').find('a')['href']
        if 'night_clubs' in rest_url:
            return False
        rest_name = rest.find('div', class_='H3').find('a').text
        rest_info = {
            'name': rest_name.replace(u'\xa0', u' ').replace('\t', '').replace('\n', ' ').strip(),
            'url': rest_url,
        }
        url = f"{rest_info['url']}menu"
        html = get_html(url, 'get')
        menu = self._get_menu(html)
        self.result_menu.append({
            'name': rest_info['name'],
            'menu': menu
        })
        info = self._get_info(html)
        # дополняем "каркас" ресторана дополнительной инфой
        rest_info.update({'have_menu': bool(menu)})
        for key, value in info.items():
            rest_info[key] = value
        self.result_rests.append(rest_info)

    def _parse_rest_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        all_rests = soup.find(
            'ul', class_='service-items-medium').findAll('div', class_='service-description')
        for rest in all_rests:
            self._fill_rest_data(rest)

    def get_all_data(self):
        # пока забираем столько страниц, сколько хотим. потом изменить на while
        for page in range(1, 3):
            url = f"https://spb.zoon.ru/restaurants/?action=list&type=service&search_query_form=1&sort_field=rating&need%5B%5D=items&page={page}"
            html = get_html(url, 'post')
            if html:
                self._parse_rest_page(html)


if __name__ == "__main__":
    data = DataFiller()
    data.get_all_data()
#    print(data.result_rests)
    print(data.result_menu)


# запись в файл csv
# with open('rests.csv', 'w', encoding='utf-8', newline='') as f:
#     fields = ['name', 'url', 'metro', 'adress'....]
#     writer = csv.DictWriter(f, fields, delimiter='|')
#     writer.writeheader()
#     for rest in result_rests:
#         writer.writerow(rest)
