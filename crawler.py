import pandas as pd
import tqdm
import numpy as np
from bs4 import BeautifulSoup


import helper as h
from helper import Session


class Crawler:
    def __init__(self, url, log):
        self.sess = Session(url_base=url, test_verify=True, verbose=2, log=log)
        self.log = log

    def all_characters(self, save_path, thumb_path):
        # init
        rsp = self.sess.get("/page-data/character-builder/page-data.json")
        # Get data
        rsp = self.sess.get(f"/page-data/sq/d/{rsp.json()['staticQueryHashes'][0]}.json")

        char_data = rsp.json()['data']['allContentfulCharacter']['nodes']
        self.log.info(f"Total Entries pulled: {len(char_data)}")

        # Save response for viewing
        h.write_json(save_path.parent / f"{save_path.stem}.example.json", char_data)

        out_data = []
        for entry in tqdm.tqdm(char_data, total=len(char_data), desc="Processing Char"):
            img_url = entry['cardImage']['localFile']['childImageSharp']['gatsbyImageData']['images']['fallback']['src']

            data = {'fullName': entry['fullName'], 'name': entry['shortName'].lower()}
            data.update({status.lower(): value for status, value in entry['attributes'].items()})

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

    def gear_stats(self, main_path, sub_path):
        self.log.info("Pulling Gear Information ...")
        rsp = self.sess.get("/guides/gear-stats/")
        soup = BeautifulSoup(rsp.text, "html.parser")

        tables = soup.findAll("table")
        assert len(tables) == 2, "Unable to find gear stat tables from server"

        # process Gear Main Stat
        main_df = self._gear_main(tables[0])
        # process Gear Sub Stat Min Max
        sub_df = self._gear_sub(tables[1])

        h.pickle_file("write", fname=main_path, data=main_df)
        h.pickle_file("write", fname=sub_path, data=sub_df)

    def _download_img(self, url, dl_path):
        try:
            r = self.sess.get(url)
            with open(dl_path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        except Exception as e:
            self.log.debug(e)
            self.log.warning(f"Unable to download images for {dl_path.stem}, url: {url}")

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
