from helper import Session
import helper as h
import tqdm


class Crawler:
    def __init__(self, url, log):
        self.sess = Session(url_base=url, test_verify=True, verbose=2, log=log)
        self.log = log

    def all_characters(self, save_path, thumb_path):
        # init
        rsp = self.sess.get("page-data/character-builder/page-data.json")
        # Get data
        rsp = self.sess.get(f"page-data/sq/d/{rsp.json()['staticQueryHashes'][0]}.json")

        char_data = rsp.json()['data']['allContentfulCharacter']['nodes']
        self.log.info(f"Total Entries pulled: {len(char_data)}")

        out_data = {}
        for entry in tqdm.tqdm(char_data, total=len(char_data), desc="Processing Char"):
            char_name = entry['shortName'].upper()

            entry['attributes']['ATK'] = entry['attributes'].pop("atk")
            entry['attributes']['HP'] = entry['attributes'].pop("hp")
            entry['attributes']['DEF'] = entry['attributes'].pop("def")
            entry['attributes']['SPD'] = entry['attributes'].pop("spd")
            entry['attributes']['CRIT'] = entry['attributes'].pop("crit")
            entry['attributes']['CRIT DMG'] = entry['attributes'].pop("critDMG")
            entry['attributes']['STATUS ACC'] = entry['attributes'].pop("hit")
            entry['attributes']['STATUS RES'] = entry['attributes'].pop("res")
            entry['attributes']['DUAL'] = entry['attributes'].pop("dual")

            img_url = entry['cardImage']['localFile']['childImageSharp']['gatsbyImageData']['images']['fallback']['src']
            out_data[char_name] = {
                'fullName': entry['fullName'],
                'attr': entry['attributes']
            }

            # if exist don't need to download
            if (thumb_path / f"{char_name}.png").is_file():
                continue

            # download thumbnail
            self._download_img(img_url, thumb_path / f"{char_name}.png")

        h.write_json(save_path, out_data)

    def _download_img(self, url, dl_path):
        try:
            r = self.sess.get(url)
            with open(dl_path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        except Exception as e:
            self.log.debug(e)
            self.log.warning(f"Unable to download images for {dl_path.stem}, url: {url}")

