import pandas as pd
import tqdm

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

    def _download_img(self, url, dl_path):
        try:
            r = self.sess.get(url)
            with open(dl_path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        except Exception as e:
            self.log.debug(e)
            self.log.warning(f"Unable to download images for {dl_path.stem}, url: {url}")
