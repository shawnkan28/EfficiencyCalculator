import collections
import datetime
import datetime as dt
import inspect
import operator
import os
import pathlib
import pickle
import re
from base64 import urlsafe_b64encode
from datetime import timedelta
from pathlib import Path

import bcrypt
import keyring
import pandas as pd
import requests
from cryptography.fernet import Fernet
from pandas.tseries.offsets import BDay
import json


def trace(offset=0, lvl=1):
    offset += 1
    return f"{os.path.basename(inspect.stack()[offset].filename)}" \
           f":{inspect.stack()[offset].lineno}:" \
           + f" {inspect.stack()[offset].function}()" if lvl > 0 else ""


def change_indexing(widgets, stat_type):
    s = widgets[widgets.index.str.contains(stat_type)]
    new_index = [x.replace(f"{stat_type}_", "") for x in s.index]
    s.index = new_index
    s.name = stat_type
    return s


def write_json(out, data):
    # Serializing json
    json_object = json.dumps(data, indent=4)

    with open(out, "w") as outfile:
        outfile.write(json_object)


def read_json(path):
    # Opening JSON file
    with open(path, 'r') as openfile:
        # Reading from json file
        json_data = json.load(openfile)

    return json_data


def nested_dict():
    return collections.defaultdict(nested_dict)


def clean_logs(path: pathlib.Path, num_days=7, log=None) -> None:
    """
    check log folder and keep only a certain number of days worth of logs
    use the latest log date as start counter.
    :param path: path to folder for cleaning
    :param num_days: num of days worth of logs to keep
    :param log: print in log file if exists, number of files removed
    :return:
    """
    data_list = []

    for log_path in path.iterdir():
        m_timestamp = log_path.stat().st_mtime
        time = datetime.datetime.fromtimestamp(m_timestamp)
        data_list.append({"path": log_path, "m_date": time})

    df = pd.DataFrame(data_list)
    df.sort_values(by='m_date', inplace=True, ascending=False)

    # min_date = date_delta(df.iloc[0]["m_date"], delta=-num_days, out_fmt=None)
    # df = df.loc[df["m_date"] < min_date]

    # keep only 7 files in log
    df = df.iloc[num_days:]

    for i, r in df.iterrows():
        if log:
            log.debug(f"Delete Log: {r['path']}")
        os.remove(r['path'])


def is_float(element) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False


def get_ext(file_path):
    fp = file_path
    if isinstance(file_path, str):
        fp = Path(file_path)

    assert fp.is_file(), f"Path provided is not a file. ({fp})"

    return fp.suffix


def creds_man(app_name, uname, mode="store", pw=None):
    """
    encrypt string with bcrypt and store encrypted string with keyring.
    check keyring data from windows cred manager
    :param app_name: where to get password from
    :param uname: username
    :param mode: selection
                 - store
                 - check
                 - get_keyring = returns keyring password value (will be bcrypt encrypted)
    :param pw: password
    :return:
    """
    assert mode == "store" or mode == "check" or mode == "get_keyring", "Selected mode is unavailable"

    if mode == "store":
        assert pw is not None, "Please include password to encrypt or password to be checked."

        hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode('utf-8')
        keyring.set_password(app_name, uname, hashed)
        return hashed

    elif mode == "get_keyring":
        return keyring.get_password(app_name, uname)

    else:
        assert pw is not None, "Please include password to encrypt or password to be checked."

        dec_pw = keyring.get_password(app_name, uname)
        assert dec_pw is not None, f"Unable to find password for app_name: {app_name}, user: {uname}"
        return bcrypt.checkpw(pw.encode(), dec_pw.encode('utf-8'))


def pickle_file(mode, fname="./pickle_data.pickle", data=None):
    """
    read/write data to a pickle file
    :param mode: types: "read", "write". choose between read and write operation
    :param fname: file location of data
    :param data: data to write. only required if mode is "write".
    :return: if read, returns file data else return file location
    """
    assert mode == "read" or mode == "write", "mode does not exist."

    if mode == "read":
        with open(fname, 'rb') as r:
            return pickle.load(r)
    else:
        assert data is not None, f"mode: {mode}, please use the data parameter to add data to pickle."
        with open(fname, 'wb') as w:
            pickle.dump(data, w)
        return fname


def sort_num_string(data_list):
    """
    Sort Strings that have numerical values by the numeric values
    :param data_list: list of strings
    :return: sorted list
    """

    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        """
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        """
        return [atoi(c) for c in re.split(r'(\d+)', text)]

    data_list.sort(key=natural_keys)
    return data_list


def date_delta(date=None, delta=0, out_fmt=None, in_fmt=None, biz_day=False):
    """
    Get Date or Date difference
    :param date: datetime object or string, date you want to perform operator on, default get current date
    :param delta: int value, add or subtract
    :param out_fmt: string, date output format, e.g. "%Y%m%d", None if out is datetime
    :param in_fmt: string, format of date param, if is string
    :param biz_day: compute delta by using Business Days or not
    :return: output date in string format
    """

    if date is None:
        date = dt.datetime.today()
    elif type(date) is str:
        assert in_fmt is not None
        date = pd.to_datetime(date, in_fmt)

    op = {"add": operator.add, "sub": operator.sub}

    if delta == 0:
        n_date = date
    else:
        key = "add" if delta > 0 else "sub"
        n_date = op[key](date, BDay(abs(delta)) if biz_day else timedelta(days=abs(delta)))

    return n_date if out_fmt is None else n_date.strftime(out_fmt)


class Crypto:
    def __init__(self, key_file=None):
        if key_file is None:
            self.key = Fernet.generate_key()
        else:
            with open(key_file, 'rb') as r:
                self.key = r.read()

        self.fer = Fernet(self.key)

    def get_key(self):
        return self.key

    def set_key(self, new_key, replace=False):
        """
        Extend key with new_key or replace current key with another key
        :param new_key: string to add to key
        :param replace: replace = True replace the whole key while False appends text to key
        :return: None
        """
        # key can only be multiples of 4
        if replace:
            assert len(new_key) >= 32, f"Key used for encryption must be >= 32 in length. key length = {len(new_key)}"
            new_key = new_key[:32]
            self.key = urlsafe_b64encode(new_key.encode())

        else:
            self.key = self.key + new_key.encode()

        self.fer = Fernet(self.key)

    def encrypt(self, data):
        return self.fer.encrypt(data.encode()).decode()

    def decrypt(self, enc_text):
        return self.fer.decrypt(enc_text.encode()).decode()


class Session(requests.Session):
    def __init__(self, url_base=None, log=None, test_verify=False, verbose=1):
        """
        :param url_base:
        :param log:
        :param test_verify: if true will attempt verify=True if fail will run verify=False
        """
        super(Session, self).__init__()
        self.url_base = url_base
        self.log = log
        self.test_verify = test_verify
        self.verbose = verbose

    def request(self, method, url, **kwargs):
        if self.url_base is not None:
            url = self.url_base + url

        if self.test_verify:
            try:
                rsp = super(Session, self).request(method, url, **kwargs)
            except requests.exceptions.SSLError:
                if self.log is not None and self.verbose > 1:
                    self.log.warning("SSL Verification Failed. Using verify=False")

                rsp = super(Session, self).request(method, url, verify=False, **kwargs)
        else:
            rsp = super(Session, self).request(method, url, **kwargs)

        if rsp.status_code > 400 and self.log is not None and self.verbose > 1:
            self.log.error(f"Status Code: {rsp.status_code}, url: {rsp.url}")

        return rsp


