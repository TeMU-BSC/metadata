from typing import List, Union, Dict, Tuple, Set
from pathlib import Path
import json
from datetime import datetime
from urllib.parse import urlparse
import os

LANGS = ['ab', 'aa', 'af', 'ak', 'sq', 'am', 'ar', 'an', 'hy', 'as', 'av', 'ae', 'ay', 'az', 'bm', 'ba', 'eu', 'be',
         'bn', 'bh', 'bi', 'bs', 'br', 'bg', 'my', 'ca', 'ch', 'ce', 'ny', 'zh', 'cv', 'kw', 'co', 'cr', 'hr', 'cs',
         'da', 'dv', 'nl', 'dz', 'en', 'eo', 'et', 'ee', 'fo', 'fj', 'fi', 'fr', 'ff', 'gl', 'ka', 'de', 'el', 'gn',
         'gu', 'ht', 'ha', 'he', 'hz', 'hi', 'ho', 'hu', 'ia', 'id', 'ie', 'ga', 'ig', 'ik', 'io', 'is', 'it', 'iu',
         'ja', 'jv', 'kl', 'kn', 'kr', 'ks', 'kk', 'km', 'ki', 'rw', 'ky', 'kv', 'kg', 'ko', 'ku', 'kj', 'la', 'lb',
         'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv', 'gv', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mh', 'mn', 'na',
         'nv', 'nb', 'nd', 'ne', 'ng', 'nn', 'no', 'ii', 'nr', 'oc', 'oj', 'cu', 'om', 'or', 'os', 'pa', 'pi', 'fa',
         'pl', 'ps', 'pt', 'qu', 'rm', 'rn', 'ro', 'ru', 'sa', 'sc', 'sd', 'se', 'sm', 'sg', 'sr', 'gd', 'sn', 'si',
         'sk', 'sl', 'so', 'st', 'es', 'su', 'sw', 'ss', 'sv', 'ta', 'te', 'tg', 'th', 'ti', 'bo', 'tk', 'tl', 'tn',
         'to', 'tr', 'ts', 'tt', 'tw', 'ty', 'ug', 'uk', 'ur', 'uz', 've', 'vi', 'vo', 'wa', 'cy', 'wo', 'fy', 'xh',
         'yi', 'yo', 'za', 'zu']

FORMATS = ['pdf', 'json', 'xml', 'txt']

ENCODINGS = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775',
             'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864',
             'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125',
             'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258',
             'cp65001', 'euc-jp', 'euc-jis-2004', 'euc-jisx0213', 'euc-kr', 'gb2312', 'gbk', 'gb18030', 'hz',
             'iso2022-jp', 'iso2022-jp-1', 'iso2022-jp-2', 'iso2022-jp-2004', 'iso2022-jp-3', 'iso2022-jp-ext',
             'iso2022-kr', 'latin-1', 'iso8859-2', 'iso8859-3', 'iso8859-4', 'iso8859-5', 'iso8859-6', 'iso8859-7',
             'iso8859-8', 'iso8859-9', 'iso8859-10', 'iso8859-11', 'iso8859-13', 'iso8859-14', 'iso8859-15',
             'iso8859-16', 'johab', 'koi8-r', 'koi8-t', 'koi8-u', 'kz1048', 'mac-cyrillic', 'mac-greek',
             'mac-iceland', 'mac-latin2', 'mac-roman', 'mac-turkish', 'ptcp154', 'shift-jis', 'shift-jis-2004',
             'shift-jisx0213', 'utf-32', 'utf-32-be', 'utf-32-le', 'utf-16', 'utf-16-be', 'utf-16-le', 'utf-7',
             'utf-8', 'utf-8-sig']


class GlobalInformation:
    def __init__(self, used_attributes: Union[Dict, None]):
        """
        Class for handling global metadata information. In the current implementation, it is used only for keeping track
        of the existing attributes in order to provide suggestions to the user
        :param used_attributes: Dictionary {class_name: attribute_name: [existing attribute_values]}
        """
        self.used_attributes = used_attributes

    def load_from_disk(self, path: Path):
        """
        Loads self.used_attributes json dictionary from path
        :param path: path to json dictionary
        :return:
        """
        assert self.used_attributes is None
        with path.open('r') as f:
            self.used_attributes = json.loads(f.read())

    def write_to_disk(self, path: Path):
        """
        Writes self.used_attribute dictionary as json to path
        :param path: Path where the json will be saved
        :return:
        """
        assert self.used_attributes is not None
        with path.open('w') as f:
            f.write(json.dumps(self.used_attributes))

    def init_dict(self):
        """
        Initialize self.used_attributes as empty dictionary (used to differentiate between non-initialized dictionary
        (eg. to be loaded) or new dictionary (eg. first run)
        :return:
        """
        assert self.used_attributes is None
        self.used_attributes = {}


class Component:
    def __init__(self, g: GlobalInformation):
        """
        Base class for components of the metada. It has methods for extending or retrieving global information
        :param g: GlobalInformation object
        """
        assert g.used_attributes is not None
        self.g = g

    def _stringify_attribute(self, attribute_name: str) -> Tuple[str, str, str]:
        """
        Converts attribute name into a tuple of strings with the class name and the attribute value
        :param attribute_name: Name of an attribute of the class
        :return: Tuple (class_name, attribute_name, attribute_value)
        """
        class_name = self.__class__.__name__
        attribute_value = self. __getattribute__(attribute_name)
        return class_name, attribute_name, attribute_value

    def _add_global_attributes(self, attribute_names: List[str]):
        """
        Add attribute value to the global information for future suggestions to the user
        :param attribute_names: List of attribute names the values of which are to be added
        :return:
        """
        class_name = self.__class__.__name__
        for attribute_name in attribute_names:
            if not self._allow_new(attribute_name):
                return
            attribute_value = self.__getattribute__(attribute_name)
            if class_name not in self.g.used_attributes:
                self.g.used_attributes[class_name] = {}
            if attribute_name not in self.g.used_attributes[class_name]:
                self.g.used_attributes[class_name][attribute_name] = []
            if attribute_value not in self.g.used_attributes[class_name][attribute_name]:
                self.g.used_attributes[class_name][attribute_name].append(attribute_value)

    @staticmethod
    def _allow_new(attribute_name: str) -> bool:
        """
        Computes whether a given attribute should be added in the global information dictionary for future suggestions.
        Since the possible formats, encodings and langs are known in advance, they are hardcoded and we do not new
        possible values
        :param attribute_name: name of the attribute to be checked
        :return:
        """
        return attribute_name not in ['format', 'encoding', 'langs']

    def get_global_values(self, attribute_name: str) -> Set:
        """
        Return existing values (historically) of the given attribute
        :param attribute_name: Name of the attribute
        :return: Set of existing values
        """
        class_name = self.__class__.__name__
        global_attribute_values = []
        if class_name in self.g.used_attributes and attribute_name in self.g.used_attributes[class_name]:
            global_attribute_values = self.g.used_attributes[class_name][attribute_name]
        return global_attribute_values

    def _check_fields(self):
        """
        Checks whether the attributes are correct (if possible), otherwise throws an AssertionError
        :return:
        """
        raise NotImplementedError()


class Action(Component):
    def __init__(self, name: str, src: str, tgt: str, script: Union[Path, None], order: int, g: GlobalInformation):
        """
        Processing action applied to a given corpus version
        :param name: Name of the action (eg. 'tokenization'). It should be a name as standard as possible.
        :param src: input format (eg. pdf)
        :param tgt: output format (eg. txt). src might be equal to tgt.
        :param script: filename of the script used to. It should be directly executable as it is, therefore it is
        advised to provide a bash script that calls the used program with the required parameters. It is assumed to be a
        filepath within the 'scripts' directory of the corpus.
        :param order: order in which the action was applied
        """

        super().__init__(g)
        self.name = name
        self.src = src
        self.tgt = tgt
        self.script = script
        self.order = order
        self._check_fields()
        self._add_global_attributes(['name', 'src', 'tgt', 'script', 'order'])

    def _check_fields(self):
        assert len(self.name) > 0
        assert self.name.lower() == self.name
        assert len(self.src) > 0
        assert self.src.lower() == self.src
        assert len(self.tgt) > 0
        assert self.tgt.lower() == self.tgt
        assert self.script is not None or self.order == 0
        assert (self.script.exists() and self.script.is_file() and not self.script.is_absolute()) or self.script is None
        assert self.script is None or self.script[-3:] == '.sh'
        assert self.script is None or ('/' not in self.script and '\\' not in self.script)
        assert self.order >= 0


class CorpusVersion(Component):
    def __init__(self, date: str, prev: Union[str, None], path: Path, provider: str, langs: List[str], parallel: bool,
                 encoding: str, format_: str, released: Union[str, None], license_: Union[str, None],
                 actions: List[Action], g: GlobalInformation):
        """
        Corpus version (version as in corpus, processed or not, coming from the exact same original corpus). For
        instance, with this criterion, two different dumps of Wikipedia are different corpus, not different versions
        of the same corpus.
        Specifically, a corpus version is defined to be either the original corpus or a the corpus resulting to applying
        a list of Actions to another version.
        :param date: Date in which the corpus was ADDED to Corpora. Format: ISO 8601 string (YYYYMMDDTHHMMSS)
        :param prev: Directory name of the version on which the corpus is based on. It should be within the same corpus
        directory.
        :param path:
        :param provider: Provider of the corpus, lowercase (eg. 'aquas', 'wikipedia', 'temu',...)
        :param langs: List of Language codes (eg. 'ca', 'en', 'es',...)
        :param parallel: Wheter the corpus is parallel or not. If it is, usual MT conventions are assumed:
            Files in a given language must end in .[language code]. If they are not suffixed also with the directions,
            files with the same prefix are assumed to be parallel.
            Example 1: the directory contains train.en, train.es, valid.en, valid. Es Train is assumed to be parallel
            for English and Spanish, and the same can be said for valid.
            Example 2: the directory contains train.en-es.es, train.en-es.en, train.es-ca.es, train.es-ca.ca
        :param encoding: Encoding (written as in Python's open() function 'encoding' (eg. 'utf-8').
        :param format_: File format. See FORMATS for the valid extensions. Eg. 'json'.
        :param released: Either none, if this version has not been released, or the link to the released (for instance,
        Zenodo)
        :param license_: License name, in lowercase.
        :param actions: List of Actions applied to this corpus version. See Action.
        :param g: See GlobalInformation
        """
        super().__init__(g)
        self.date = datetime.strptime(date, '%Y%m%dT%H%M%S')  # ISO 8601 string (YYYYMMDDTHHMMSS)
        self.prev = prev
        self.path = path
        self.provider = provider
        self.langs = langs
        self.parallel = parallel
        self.encoding = encoding
        self.format = format_
        self.released = released
        self.license = license_
        self.actions = actions
        self._check_fields()
        self._add_global_attributes(['date', 'prev', 'path', 'provider', 'lang', 'parallel', 'encoding', 'format',
                                     'released', 'actions'])

    def _check_fields(self):
        assert self.path.exists() and self.path.is_file() and not self.path.is_absolute()
        assert '/' not in self.path.name and not '\\' not in self.path.name
        assert len(self.provider) > 0
        assert self.provider.lower() == self.provider
        for lang in self.langs:
            assert lang in LANGS
        assert len(self.langs) > 0
        assert (len(self.langs) > 1 and self.parallel) or not self.parallel
        assert self.encoding in ENCODINGS
        assert self.format in FORMATS
        assert self._check_released()
        assert len(self.license) > 0 and self.license.lower() == self.license

    def _check_released(self) -> bool:
        """
        released, if set, should be a URL (of the released corpus)
        :return:
        """
        def is_url(url):
            # https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
            try:
                result = urlparse(url)
                return all([result.scheme, result.netloc])
            except ValueError:
                return False
        return self.released is None or is_url(self.released)


class Corpus(Component):
    def __init__(self, dir_name: str, pretty_name: str, corpus_versions: List[CorpusVersion], g: GlobalInformation):
        """

        :param dir_name: It should be equal to the directory where the corpus is located. Lowercase.
        :param pretty_name: Name of the corpus. Like dirname, nut potentially with spaces, uppercase...
        :param corpus_versions: List of corpus versions (at least with one version). See CorpusVersion.
        :param g:
        """
        super().__init__(g)
        self.dir_name = dir_name
        self.pretty_name = pretty_name
        self.corpus_versions = corpus_versions
        self._check_fields()
        self._add_global_attributes(['dirname', 'pretty_name', 'corpus_versions'])

    def _check_fields(self):
        assert len(self.dir_name) > 0
        assert self.dir_name.lower() == self.dir_name
        assert len(self.pretty_name) > 0
        assert len(self.corpus_versions) > 0
        assert self._check_prev(self.corpus_versions)

    @staticmethod
    def _check_prev(corpus_versions: List[CorpusVersion]) -> bool:
        """
        Computes whether the prev attribute of the different corpus versions is okay
        :param corpus_versions:
        :return: boolean of the condition
        """
        cond = corpus_versions[0].prev is None
        if not cond:
            return False
        paths = {cv.path for cv in corpus_versions}
        for cv in corpus_versions[1:]:
            prev = cv.prev
            if prev not in paths:
                return False
        return True
