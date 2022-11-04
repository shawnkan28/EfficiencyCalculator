import traceback

from bs4 import BeautifulSoup

from helper import Session
import helper as h
import tqdm
import pandas as pd
import numpy as np


class Crawler:
    def __init__(self, url, env):
        self.sess = Session(url_base=url, test_verify=True, verbose=2, log=env.log)
        self.e = env

    def extract_character_info(self, save_path, character_list, thumb_path, stat_path):
        """
        Crawl from website, process files and output a pickle dataframe
        :param save_path:
        :param character_list: where to save list of characters from website
        :param thumb_path:
        :param stat_path: where to save list of available stats for characters
        :return:
        """
        try:
            rsp = self.sess.get("/page-data/artery-gear/characters/page-data.json")

            char_data = rsp.json()['result']['data']['allCharacters']['nodes']
            self.e.log.info(f"Total Entries pulled: {len(char_data)}")

            # Save response for viewing
            h.write_json(save_path.parent / f"{save_path.stem}.example.json", char_data)

            out_data = []
            for entry in tqdm.tqdm(char_data, total=len(char_data), desc="Processing Char"):
                img_url = entry['cardImage']['localFile']['childImageSharp']['gatsbyImageData']['images']['fallback']['src']

                data = {'fullName': entry['fullName'], 'name': entry['shortName'].lower()}
                stats = {status.lower(): value for status, value in entry['attributes'].items()}
                data.update(stats)

                data['crit dmg'] = data.pop('critdmg')
                data['status res'] = data.pop('res')
                data['status acc'] = data.pop('hit')
                data['dual'] = data.pop('dual')

                out_data.append(data)

                # if exist don't need to download
                thumb_path.mkdir(parents=True, exist_ok=True)
                thumb_file = thumb_path / f"{entry['shortName'].lower()}.png"
                if thumb_file.is_file():
                    continue

                # download thumbnail
                self._download_img(img_url, thumb_file)

            df = pd.DataFrame(out_data)
            df.set_index('name', inplace=True)
            h.pickle_file('write', fname=save_path, data=df)

            char_list = df.index.to_list()
            stat_list = [x for x in df.columns.to_list() if x != "fullName"]
            h.pickle_file("write", fname=character_list, data=char_list)
            h.pickle_file("write", fname=stat_path, data=stat_list)
        except:
            self.e.log.debug(f"{h.trace()} {traceback.format_exc()}")
            self.e.log.error(f"{h.trace()} Unable to crawl artery gear Character stats website. "
                             f"Will use local data if exist.")

    def extract_gear_info(self, gear_main_path, gear_sub_path):
        """
        extract main stat for each gear. and min-max sub stat for each gear
        :param gear_main_path: path to store gear main stat
        :param gear_sub_path:  store gear sub stat min-max
        :return:
        """
        try:
            self.e.log.info("Pulling Gear Information ...")
            rsp = self.sess.get("/artery-gear/database/gear-stats/")
            soup = BeautifulSoup(rsp.text, "html.parser")

            tables = soup.findAll("table")
            assert len(tables) == 2, "Unable to find gear stat tables from server"

            # process Gear Main Stat
            main_df = self._gear_main(tables[0])
            # process Gear Sub Stat Min Max
            sub_df = self._gear_sub(tables[1])

            h.pickle_file("write", fname=gear_main_path, data=main_df)
            h.pickle_file("write", fname=gear_sub_path, data=sub_df)
        except:
            self.e.log.debug(f"{h.trace()} {traceback.format_exc()}")
            self.e.log.error(f"{h.trace()} Unable to crawl artery gear Gear "
                             f"Info website. Will use local data if exist.")

    def extract_gear_set_info(self, sets_path):
        """
        Extract Gear Sets Information, gear sets are in a form of html table.
        :param sets_path:
        :return:
        """
        try:
            self.e.log.info("Pulling Sets Information ...")
            rsp = self.sess.get("/artery-gear/database/gear-sets/")
            soup = BeautifulSoup(rsp.text, 'html.parser')

            table = soup.find("table")
            assert table is not None, "Unable to find gear sets information"

            df = pd.read_html(str(table))[0]
            df = df[['Set Name', 'Equip Slots', 'Set Effects']].copy()
            df['Set Name'] = df['Set Name'].str.replace("Set", "").str.strip()
            df['Equip Slots'] = df['Equip Slots'].str.replace("Slots", "").str.strip()
            df['Set Effects'] = df['Set Effects'].str.extract(r" (\d+)%\s?")
            df = df.loc[df['Set Effects'].notna()]

            h.pickle_file("write", sets_path, data=df)
        except:
            self.e.log.debug(f"{h.trace()} {traceback.format_exc()}")
            self.e.log.error(f"{h.trace()} Unable to crawl artery gear Gear Sets website. "
                             f"Will use local data if exist.")

    def _download_img(self, url, dl_path):
        try:
            r = self.sess.get(url)
            with open(dl_path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        except Exception as e:
            self.e.log.debug(f"{h.trace()} {e}")
            self.e.log.warning(f"{h.trace()} Unable to download images for {dl_path.stem}, url: {url}")

    @staticmethod
    def _gear_main(gms_soup):
        for i in gms_soup.findAll('td'):
            if "data-icon" not in str(i):
                continue
            i.string = i.svg['data-icon']

        gms_df = pd.read_html(str(gms_soup))[0]
        gms_df.columns = [x.split("const t")[0] for x in gms_df.columns]

        for col in gms_df.columns:
            if col in ['Stat', 'Max Value']:
                continue

            gms_df[col] = np.where(gms_df[col] == "check",
                                   gms_df['Max Value'],
                                   np.nan)
        del gms_df['Max Value']
        gms_df.set_index("Stat", inplace=True)
        return gms_df

    @staticmethod
    def _gear_sub(soup):
        df = pd.read_html(str(soup))[0]
        df.set_index('Name', inplace=True)
        del df['Icon']

        grades = df.columns
        sec_col = ['min', 'max']

        c = pd.MultiIndex.from_product([grades, sec_col])
        out = pd.DataFrame(columns=c)

        for i, r in df.iterrows():
            data = []
            for color in grades:
                d = r[color].split("-")
                data.append(d[0].strip())
                data.append(d[1].strip())

            out.loc[i] = data
        return out
