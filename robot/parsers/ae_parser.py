# coding=utf-8
from parsers import ParserBase, Item
from bs4 import BeautifulSoup
import re
import os


cat_id_regex = re.compile(r'.*/category/(\d+)/.*')


cat_mapping = {
    '100003109': 'f_clothing_accessories',
        '200003482': 'f_dresses',
        '200001648': 'f_blouses_shirts',
        '100003141': 'f_hoodies_sweatshirts',
        '200000783': 'f_sweaters',
            '202003500': 'f_cardigans',
            '202003502': 'f_pullovers',
            '202003503': 'f_shrugs',  # накидки
            '202003504': 'f_vests',
            '202061873': 'f_cloak',
        '200000775': 'f_jackets_coats',
            '202003530': 'f_basic_jackets',
            '202005126': 'f_parkas',
            '202005127': 'f_faux_fur',
            '202005128': 'f_leather_suede',
            '202005129': 'f_trench',
            '202001903': 'f_vests_waistcoats',  # безрукавки
            '202005130': 'f_wool_blends',  # полушерстяные пальто
            '202060221': 'f_down_coats',  # пуховики
            '202061136': 'f_real_fur',
        '200000724': 'f_accessories',
            '202003430': 'f_sunglasses',
            '202032009': 'f_eyewear_frames',
            '202003424': 'f_eyewear_accessories',
            '202003426': 'f_scarves',
            '202005122': 'f_belts_cummerbunds',
            '202003439': 'f_hats_caps',
                '202000439': 'f_berets',
                '202003545': 'f_bomber_hats',  # шапки-ушанки
                '202003543': 'f_baseball_caps',
                '202003546': 'f_bucket_hats',  # панамки
                '202003547': 'f_cowboy_hats',
                '202003548': 'f_fedoras',  # фетровые шляпы
                '202005093': 'f_military_hats',
                '202003549': 'f_newsboy_caps',  # кепки с закругленными краями
                '202003550': 'f_skullies_beanies',  # трикотажные шапки
                '202003551': 'f_sun_hats',
                '202003552': 'f_visors', # козырьки
            '202003423': 'f_gloves_mittens',
            '202003421': 'f_arm-warmers',  # рукава без рубашки
            '202003422': 'f_earmuffs',
            '202004146': 'f_hair_accessories',
            '202004101': 'f_scarf_hat_glove_sets',
            '202005124': 'f_suspenders',  # подтяжки
            '202005125': 'f_ties_handkerchiefs',
            '201930012': 'f_masks',
        '200118010': 'f_bottoms',
            '202002388': 'f_skirts',
            '202001905': 'f_pants_capris',
            '202003586': 'f_leggings',
            '202001909': 'f_shorts',
            '202001908': 'f_jeans',
        '200215341': 'f_rompers',  # песочники
        '200000785': 'f_tops_tees',
            '202001901': 'f_t-shirts',
            '202003454': 'f_camis',  # топики
            '202001902': 'f_tank_tops',  # майки
            '202032002': 'f_polo_shirts',
        '200000773': 'f_intimates',  # нижнее белье
            '202002389': 'f_bras',
            '202002391': 'f_bra_brief_sets',
            '202003566': 'f_bustiers_corsets',
            '202003563': 'f_shapers',  # корректирующее белье
            '202003562': 'f_panties',
            '202002390': 'f_camisoles_tanks',  # майки и топики
            '202015067': 'f_tube_tops',
            '202004111': 'f_long_johns',  # кальсоны?
        '200001092': 'f_jumpsuits',
        '200215336': 'f_bodysuits',
        '200000782': 'f_suits_sets',
            '202003507': 'f_blazers',
            '202003508': 'f_dress-suits',  # платье с пиджаком
            '202003505': 'f_pant-suits',
            '202003506': 'f_skirt-suits',
            '202032004': 'f_women_sets',  # комплекты
        '200000781': 'f_socks_hosiery',
            '202003515': 'f_leg_warmers',  # гетры
            '202003511': 'f_socks',
            '202005131': 'f_stockings',
            '202003521': 'f_tights',  # колготки
        '200000777': 'f_sleep_lounge',

    '202001764': 'f_shoes',
        '202060327': 'f_boots',
        '202060314': 'f_ankle_boots',

    '100003070': 'm_clothing_accessories',
        '100003084': 'm_hoodies_sweatshirts',
        '200000707': 'm_tops_tees',
            '202028001': 'm_polo_shirts',
            '202003415': 'm_tank_tops',  # майки
            '202001893': 'm_t-shirts',
        '200000662': 'm_jackets_coats',
            '202005135': 'm_down_jackets',  # пуховики
            '202003387': 'm_jackets',
            '202032007': 'm_parkas',
            '202005138': 'm_faux_leather_coats',
            '202005144': 'm_trench',
            '202005162': 'm_wool_blends',
            '202001894': 'm_vest_waistcoats',
            '202003399': 'm_blazers',
            '202003400': 'm_suit_jackets',
            '202060226': 'm_genuine_leather_coats',
        '200118008': 'm_pants',
            '202001896': 'm_casual_pants',
            '202060236': 'm_cargo_pants',
            '202060231': 'm_overalls',  # комбинезоны
            '202032006': 'm_sweatpants',  # треники
            '202060241': 'm_harem_pants',  # зауженные шаровары
            '202060246': 'm_wide_leg_pants',  # шаровары
            '202060251': 'm_flare_pants',  # клеш
            '202060252': 'm_skinny_pants',
            '202060256': 'm_cross_pants',  # хламидообразные
            '202061650': 'm_leather_pants',
            '202061869': 'm_leggings',
        '200000668': 'm_shirts',
            '202003389': 'm_casual_shirts',
            '202003390': 'm_dress_shirts',
            '202003391': 'm_tuxedo_shirts',
            '202058001': 'm_short_sleeve_shirts',
        '100003086': 'm_jeans',
        '200000708': 'm_underwear',
            '202003417': 'm_boxers',
            '202003418': 'm_briefs',
            '202004110': 'm_long_johns',
            '202004960': 'm_shapers',
            '202001899': 'm_undershirts',
            '202003419': 'm_g-strings_thongs',
        '200000599': 'm_accessories',
            '202003373': 'm_scarves',
            '202003367': 'm_belts_cummerbunds',
            '202003368': 'm_ties_handkerchiefs',
            '202003375': 'm_eyewear_accessories',
                '202004108': 'm_glasses_accessories',
                '202004186': 'm_reading_glasses',
                '202003376': 'm_sunglasses',
                '202032010': 'm_eyewear_frames',
                '202061539': 'm_prescription_glasses',
            '202003377': 'm_hats_caps',
                '202003378': 'm_baseball_caps',
                '202005136': 'm_bomber_hats',  # шапки-ушанки
                '202003379': 'm_bucket_hats',  # панамки,
                '202003380': 'm_cowboy_hats',
                '202003381': 'm_fedoras',  # фетровые шляпы
                '202005137': 'm_military_hats',
                '202003382': 'm_newsboy_caps',
                '202003383': 'm_skullies_beanies',  # трикотажные шапки
                '202003384': 'm_visors',  # козырьки
                '202032001': 'm_sun_hats',
                '202032008': 'm_berets',
            '202003369': 'm_arm_warmers',  # татуировки на руки
            '202003370': 'm_earmuffs',
            '202003371': 'm_gloves_mittens',
            '202003372': 'm_headbands',
            '202004100': 'm_scarf_hat_glove_sets',
            '202003385': 'm_suspenders',  # подтяжки
            '201906015': 'm_masks',
        '200000701': 'm_sweaters',
            '202003405': 'm_cardigans',
            '202003406': 'm_pullovers',
            '202003407': 'm_sweater_vests',
        '200000692': 'm_suits_blazers',
            '202003402': 'm_suits',
            '202003403': 'm_suits_vests',
            '202061395': 'm_tailor_made_suits',
        '200000673': 'm_sleep_lounge',
            '202004140': 'm_pajama_sets',
            '202003393': 'm_robes',  # халаты
            '202003394': 'm_sleep_bottoms',
            '202003395': 'm_robe_sets',
            '202003396': 'm_sleep_tops',
        '100003088': 'm_casual_shorts',
        '200003491': 'm_socks',
        '200216733': 'm_men_sets',
        '200000709': 'm_board_shorts',
}


class AEParser(ParserBase):
    def parse_itemid(self, html):
        init_data = html.find('meta', attrs={'property': 'og:url'})['content']
        init_data = re.search(r'\d+(?=\.html)', init_data)
        init_data = None if not init_data else init_data.group(0)
        return init_data

    def parse_title(self, html):
        title = html.find(attrs={'itemprop': 'name'}).string
        return title


    def parse_price(self, html):
        price = float(html.find(attrs={'itemprop': 'price'}).string.replace(',', '.'))
        return price

    def parse_currency(self, html):
        res = html.find(attrs={'itemprop': 'priceCurrency'})['content']
        return res

    def parse_img(self, html):
        img = html.find(attrs={'property': 'og:image'})['content']
        basename, ext = os.path.splitext(img)
        img_small = basename + ext + '_220x220' + ext
        img_big = basename + ext + '_640x640' + ext
        return img_small, img_big

    def parse_cat_ids(self, html):
        breadcrumbs = html.find(class_='ui-breadcrumb')
        cat_tags = breadcrumbs.find_all('a', attrs={'href': cat_id_regex})
        links = [x['href'] for x in cat_tags]
        cat_ids = [cat_id_regex.search(x) for x in links]
        cat_ids = [x.group(1) for x in cat_ids]

        res = []
        for cat_id in cat_ids:
            if cat_id in cat_mapping:
                res.append(cat_mapping[cat_id])
        return res



    def parse(self, text):
        html = BeautifulSoup(text)

        init_data = self.parse_itemid(html)
        title = self.parse_title(html)
        price = self.parse_price(html)
        currency = self.parse_currency(html)
        img_big, img_small = self.parse_img(html)
        cat_ids = self.parse_cat_ids(html)

        rating = html.find('span', attrs={'itemprop': 'ratingValue'})




        res = Item(
            init_data=init_data,
            source='ae',
            title=title,
            price=price,
            currency=currency,
            img_big=img_big,
            img_small=img_small,
            cat_ids=,
            'stock_available',
            'rating',
            'votes',
            'orders',
            'reviews',
            'seller',
            'seller_rating',
            'wishlist_count',
            'delivery_time'
        )


        return text

    def build_url(self, data):
        return 'https://ru.aliexpress.com/item/-/%s.html' % data
