import json

import pandas as pd
import tqdm

from Requests import Req


class Logic:
    def __init__(self, args, log):
        self.a = args
        self.lg = log
        self.r = Req(self.lg)

    def get_db(self, info):
        """
        get csv file into df
        :param info:  a dictionary of key: f_path, value: kwargs
        :return:
        """

        dfs = {}
        for f_path, kwargs in info.items():
            df = self._check_db(f_path, **kwargs)
            dfs[f_path.stem] = df

        return dfs

    def get_all_char_info(self):
        rsp = self.r.req(f"{self.a.base_url}page-data/character-builder/page-data.json")

        url = f"{self.a.base_url}page-data/sq/d/{rsp.json()['staticQueryHashes'][0]}.json"
        rsp = self.r.req(url)

        self.lg.info(f"Total Entries pulled: {len(rsp.json()['data']['allContentfulCharacter']['nodes'])}")

        out = self.a.out_dir / "char_info.json"
        self.write_json(out, rsp.json()['data']['allContentfulCharacter']['nodes'])

    def process_char_info(self):
        char_file = self.a.out_dir / "char_info.json"
        char_data = self.read_json(char_file)

        thumb_dir = self.a.out_dir / "thumb"
        thumb_dir.mkdir(parents=True, exist_ok=True)

        out = {}
        for entry in tqdm.tqdm(char_data, total=len(char_data), desc="Processing Char"):
            out[entry['shortName']] = {
                'fullName': entry['fullName'],
                'imgPath': entry['cardImage']['localFile']['childImageSharp']['gatsbyImageData']['images']['fallback'][
                    'src'],
                'attr': entry['attributes']
            }

            if (thumb_dir / f"{entry['shortName']}.png").is_file():  # if exist don't need to download
                continue

            # Download Image if you have not yet.
            url = f"{self.a.base_url[:-1]}{out[entry['shortName']]['imgPath']}"
            try:
                r = self.r.req(url)
                with open(thumb_dir / f"{entry['shortName']}.png", 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
            except Exception as e:
                self.lg.debug(e)
                self.lg.warning(f"Unable to download images for {entry['shortName']}, url: {url}")

        self.write_json(self.a.out_dir / "processed_char.json", out)

    @staticmethod
    def write_json(out, data):
        # Serializing json
        json_object = json.dumps(data, indent=4)

        with open(out, "w") as outfile:
            outfile.write(json_object)

    @staticmethod
    def read_json(path):
        # Opening JSON file
        with open(path, 'r') as openfile:
            # Reading from json file
            json_data = json.load(openfile)

        return json_data

    @staticmethod
    def compute_eff(stat_name, stat_val, db):
        """
        compute efficiency of gear for each sub stat
        :return: efficiency val
        """
        # COMPUTE FOR INDIVIDUAL EFFICIENCY SUB STAT USED FOR GEAR
        # 10 * (ATK% - LOWESTSubStatVal) / (MAXSubStatVal - LOWESTSubStatVal)
        min_val = db['BLUE']['Min'][stat_name]
        max_val = db['GOLD']['Max'][stat_name]
        return 10 * ((stat_val - min_val) / (max_val - min_val))

    def _check_db(self, path, **kwargs):
        assert path.is_file(), f"Unable to locate csv file. {path}"

        self.lg.info(f"Reading from {path}")
        df = pd.read_csv(path, **kwargs)
        return df
