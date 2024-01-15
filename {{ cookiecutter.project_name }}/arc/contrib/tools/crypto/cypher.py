# -*- coding: utf-8 -*-
"""
TalosBDD data encryption actions module.
"""
import logging

from Crypto.Cipher import AES  # noqa
from base64 import b64encode, b64decode

logger = logging.getLogger(__name__)

BLOCK_SIZE = AES.block_size


class Cypher:
    """
    Cypher actions class.
    """

    def __init__(self, passphrase):
        """
        Both seed and iv must have a fixed length of 16.
        :param passphrase:
        """
        self._seed = passphrase
        self._iv = '0999112365734322'

    def encrypt(self, text):
        """
        Given a string, encrypt the data and return the encrypted string.
        :param text:
        """
        logger.debug('Encrypting text in AES mode')
        text = self.__add_bytes(text).encode('cp1252')
        cipher = AES.new(key=self._seed.encode('cp1252'), mode=AES.MODE_CBC, IV=self._iv.encode('cp1252'))
        encrypted_text = cipher.encrypt(text)
        return b64encode(encrypted_text).decode('cp1252')

    def decrypt(self, encrypted_text):
        """
        Given an encrypted text, decrypt the data and return the decrypted string.
        :param encrypted_text:
        """
        logger.debug('Decrypting text in AES mode')
        encrypted_text = b64decode(encrypted_text)
        cipher = AES.new(key=self._seed.encode('cp1252'), mode=AES.MODE_CBC, IV=self._iv.encode('cp1252'))
        decrypted_text = cipher.decrypt(encrypted_text)
        return self.__remove_bytes(decrypted_text).decode('cp1252')

    @staticmethod
    def __add_bytes(string):
        """
        Add bytes to match the required length.
        :param string:
        """
        a = (BLOCK_SIZE - len(string.encode('cp1252')) % BLOCK_SIZE)
        final_text = string + (a * chr(BLOCK_SIZE - len(string.encode('cp1252')) % BLOCK_SIZE))
        return final_text

    @staticmethod
    def __remove_bytes(string):
        """
        Remove the unnecessary bytes after the decryption and decode.
        :param string:
        """
        final_text = string[:-ord(string[len(string) - 1:])]
        return final_text
