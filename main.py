import requests
from bs4 import BeautifulSoup
import re
import json
import os

headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }
def get_data(url):
    for i in range(1,150):
        if os.path.exists(f'page_{i}.html'):
            os.remove(f'page_{i}.html')
    req = requests.get(url, headers)

    if not os.path.exists("data"):
        os.mkdir("data")
    with open("page_1.html", "w") as file:
        file.write(req.text)
    with open("page_1.html") as file:
        src = file.read()
        soup = BeautifulSoup(src, "lxml")
        p_check = soup.find("h3", class_="text-danger")

        if p_check != None:
            print('Объявления не найдены')
            return -1
        try:
            page_count1= soup.find("ul", class_="pagination").find_all("a")[-2]
            page_count2 = page_count1.get('href')
            page_count = int(re.split("[=?&/]",page_count2)[5])
        except AttributeError:
            page_count=1
        for i in range(1, page_count + 1):
            nurl = url+f"&page={i}"
            r = requests.get(nurl, headers)
            with open(f"page_{i}.html", "w") as file:
                file.write(r.text)
    return page_count + 1

def data_mine(page_counts):
    urls = []
    for page in range(1, page_counts):
        with open(f"page_{page}.html") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        board = soup.find_all("div", class_="ob_line row")

        for ad in board:
            p_url = "https://chastnik-m.ru/" + ad.find("div", class_="text").find("a").get("href")
            urls.append(p_url)

        for i in range(0, 4):
            urls.pop()
            i += 1

    count = len(urls)
    if os.path.exists('data.json'):
        os.remove('data.json')
    p_data_info = []
    for p_url in urls:
        req = requests.get(p_url, headers=headers)
        p_name = re.split("[=?&/]",p_url)[-3]

        with open(f"data/{p_name}.html", "w") as file:
            src = file.write(req.text)

        with open(f"data/{p_name}.html") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        p_data = soup.find("div", class_="ob_info")

        try:
            p_logo = "https://chastnik-m.ru/" + p_data.find("div", class_="jcarousel").find("a").get("href")
        except AttributeError:
            p_logo = "-"

        try:
            p_city = p_data.find("div", class_="geo").find("span").text
        except AttributeError:
            p_city = "-"
        try:
            p_name = p_data.find("div", class_="body").find("a").text.split()
            p_name = " ".join(p_name)
        except AttributeError:
            p_name = "-"


        try:
            p_prof = p_data.find("div", class_="profession").find("b").text
        except AttributeError:
            #try:
            #    p_prof = p_data.find("div", class_="")
            p_prof = "-"


        try:
            p_earn = p_data.find("div", class_="bold").text.split()
            p_earn = " ".join(p_earn)
        except AttributeError:
            try:
                p_earn = p_data.find("div", class_="price").text.split()
                p_earn = " ".join(p_earn)
            except AttributeError:
                p_earn = "-"


        try:
            p_tel = p_data.find("div", class_="phone").find("a").get("href").split(":")[1]
        except AttributeError:
            p_tel = "-"


        if count != 0:
            print(f"Осталось итеераций: {count} ")
        else:
            print("Работа завершена")
        count -= 1

        if(p_logo == p_city == p_earn == p_name == p_prof == p_tel):
            continue
        p_data_info.append(
            {
                "Ссылка на изображение" : p_logo,
                "Город" : p_city,
                "Объявление" : p_name,
                "Тип" : p_prof,
                'Оплата' : p_earn,
                'Телефон' : p_tel
            }
        )

    with open('data.json', 'a', encoding="utf-8") as file:
        json.dump(p_data_info, file, ensure_ascii=False, indent=4)

city_names = ['Все города','Абакан','Анжеро-Судженск','Белово','Березовский','Гурьевск','Калтан','Кемерово','Киселевск','Ленинск-Кузнецкий','Мариинск',"Междуреченск",'Мыски','Новокузнецк','Осинники','Полысаево','Прокопьевск','Салаир','Тайга','Таштагол','Топки','Юрга','Шерегеш','Тяжинский','Новосибирск']
city_codes = ['-1','1018','312','313','314','315','316','317','318','319','320','321','322','323','324','325','326','327','328','329','330','331','1118','1119','648']
city = dict(zip(city_names,city_codes))
section_name = ['все категории','все для дома','все для ремонта и строительства','детское','животные, растения','недвижимость','оборудование','одежда, обувь, аксессуары','отдых, спорт, туризм','работа','разное','транспорт','услуги','электроника, бытовая техника']
section_codes = ['-1','18','30','35','33','1','84','34','31','19','36','2','103','32']
section = dict(zip(section_name,section_codes))
category_names =[]
def main():
    check = False
    while check == False:
        print("Выберите название города:",city_names)
        cit = input()
        if cit in city_names:
            check = True
        else:
            print("Неверный параметр, повторите попытку")

    while check == True:
        print("Выберите название категории:",section_name)
        sec = input()
        if sec in section_name:
            check = False
        else:
            print("Неверный параметр, повторите попытку")
    url = f"https://chastnik-m.ru/obitem/obitem_list/?city_id={city.get(cit)}&ql0={section.get(sec)}&ql1=-1&ob_type=0&ob_realty=-1&date="
    page_counts=get_data(url)
    if page_counts == -1:
        return False
    data_mine(page_counts)

if __name__ == "__main__":
    main()



